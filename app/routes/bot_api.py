"""API Endpoints used by the bot"""
from flask import request, jsonify

from app import app, db
from app.story.exceptions import UserReplyInvalid
from app.models.exceptions import DatabaseError
from app.models.game_models import User
from app.models.personalization_model import Personalization
from app.story.story_controller import StoryController
from app.models.utility import db_single_element_query, db_entry_to_dict


@app.route('/users/<user_id>/story/current-story-point/description')
def get_current_story_point_description(user_id):
    """Provides description for the users current story point"""
    try:
        return jsonify(StoryController.get_current_story_point_description(user_id)), 200
    except DatabaseError as e:
        return jsonify(f"Error: {e.args[0]}"), 400

@app.route('/users/<user_id>/story/proceed')
def try_to_proceed_story(user_id):
    """Tries to react to a provided reply by proceeding the story.
    Returns the new bot messages"""
    reply = request.args.get("reply")
    if not reply:
        return jsonify("Error: please provide a reply"), 400
    
    try:
        messages = StoryController.proceed_story(user_id, reply)
        valid_reply = True
    except UserReplyInvalid:
        messages = []
        valid_reply = False
    except DatabaseError as e:
        return jsonify(f"Error: {e.args[0]}"), 400

    return jsonify({
        "validReply": valid_reply,
        "newMessages": messages,
    }), 200

@app.route('/users/<user_id>/story/current-story-point/user-replies')
def get_user_replies(user_id):
    """Return reply options for user dependent on the current story point"""
    try:
        return jsonify(StoryController.get_current_user_replies(user_id)), 200
    except DatabaseError as e:
        return jsonify(f"Error: {e.args[0]}"), 400

@app.route('/users/register')
def register_users_handle():
    """Registeres provided chat handle for a user.
    Last handshake action
    Requires a valid auth token"""
    handle = request.args.get("handle", None)
    firstname = request.args.get("firstname", None)
    token = request.args.get("token", None)

    if not handle:
        return jsonify("Please provide a handle"), 400
    if not firstname:
        return jsonify("Please provide a firstname"), 400
    if not token:
        return jsonify("Please provide a token"), 400

    try:
        user = db_single_element_query(
            User,
            {"token": token},
            "token",
            )
    except ValueError as e:
        return jsonify([str(e)]), 400

    if user.handle:
        return jsonify("Chat already registerd for this user"), 400

    try:
        user_with_same_handle = User.query.filter_by(handle=handle).first()
    except ValueError:
        return jsonify("Invalid handle"), 400

    if user_with_same_handle:
        return jsonify("This hanlde is already in use by another user"), 400

    user.handle = handle
    user.firstname = firstname
    db.session.add(user)

    user_personalization = Personalization()
    user_personalization.user_id = user.user_id
    db.session.add(user_personalization)

    db.session.commit()

    StoryController.start_story(user.user_id)

    return jsonify("Successfull register"), 200
