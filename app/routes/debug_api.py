"""API Endpoints to get and reset data"""
import subprocess
import os, sys
from pathlib import Path
import shutil
from datetime import datetime
from flask import request, jsonify
from sqlalchemy.exc import InvalidRequestError

from config import Config

from app import app, db
from app.story.exceptions import StoryPointInvalid
from app.models.exceptions import DatabaseError
from app.models.game_models import User, TaskAssignment
from app.models.userdata_models import Contact, spydatatypes
from app.models.personalization_model import Personalization
from app.models.utility import db_entry_to_dict, db_single_element_query
from app.story.story_controller import StoryController
from app.story.task_controller import reset_tasks

# ---------- Display/Edit User Info ----------
@app.route('/users/<user_id>', methods=['GET'])
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

@app.route('/users/<user_id>/reset', methods=['PATCH'])
def reset_user(user_id):
    """Resets users to 'before register' state"""
    try:
        user = User.query.get(int(user_id))
        if user:
            # reset user data
            user.handle = None
            user.firstname = None
            user.current_story_point = None
            user.firebase_token = None
            user.phonenumber = None
            db.session.add(user)

            # reset stolen data
            for datatype in spydatatypes.values():
                for entry in datatype.query.filter_by(user_id=user.user_id):
                    db.session.delete(entry)

            # reset personalization
            user_personalization = Personalization.query.get(user.user_id)
            if user_personalization:
                db.session.delete(user_personalization)
            db.session.commit()

            # reset tasks
            reset_tasks(user.user_id)

            # remove sent images
            image_folder = Path(Config.IMAGE_UPLOAD_FOLDER, f"user_{user.user_id}")
            if image_folder.exists() and image_folder.is_dir():
                shutil.rmtree(image_folder)

            return jsonify("User was reset"), 200
        else:
            return jsonify("No such user"), 400
        
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400

@app.route('/users/<user_id>/story/current-story-point', methods=['GET', 'PUT'])
def current_story_point(user_id):
    """Returns a users current story point"""
    try:
        if request.method == 'GET':
            return jsonify(StoryController.get_current_story_point(user_id))
        if request.method == 'PUT':
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

@app.route('/users/<user_id>/story/reset', methods=['PUT'])
def reset_story(user_id):
    try:
        StoryController.start_story(user_id)
    except DatabaseError as e:
        return jsonify(e.args[0])
    return jsonify("story was reset")

@app.route('/users', methods=['GET'])
def all_users():
    """Lists all created users"""
    if request.args.get("handle"):
        try:
            user = db_single_element_query(User, {"handle": request.args.get("handle")}, "User")
            return jsonify(db_entry_to_dict(user, camel_case=True)), 200
        except ValueError as e:
            return jsonify(str(e)), 400

    return jsonify([db_entry_to_dict(user, camel_case=True) for user in User.query.all()]), 200

@app.route('/datatypes', methods=['GET'])
def all_available_datatypes():
    """Returns all datatypes that are associated with a db table"""
    return jsonify(spydatatypes.keys()), 200

@app.route('/users/<user_id>/tasks', methods=['GET'])
def fetch_user_tasks(user_id):
    """Return all tasks (finished and unfinished) assigned to a user"""
    try:
        tasks = TaskAssignment.query.filter_by(user_id=user_id)
    except ValueError:
        return jsonify("Invalid userId"), 400

    return jsonify([db_entry_to_dict(task, camel_case=True) for task in tasks]), 200
