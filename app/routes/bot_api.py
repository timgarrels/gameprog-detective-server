"""API Endpoints used by the bot"""
from flask import request, jsonify

from app import app, db
from app.story.exceptions import UserReplyInvalid, IncompletedTaskActive
from app.models.exceptions import DatabaseError
from app.models.game_models import User
from app.models.personalization_model import Personalization
from app.story.story_controller import StoryController
from app.models.utility import db_single_element_query, db_entry_to_dict


@app.route('/users/<user_id>/story/bot-messages')
def get_bot_messages(user_id):
    """Provides the current messages for the bot"""
    try:
        messages = StoryController.get_current_bot_messages(user_id)
    except DatabaseError as e:
        return jsonify(f"Error: {e.args[0]}"), 400
    
    return jsonify(messages), 200

@app.route('/users/<user_id>/story/proceed')
def try_to_proceed_story(user_id):
    """Tries to react to a provided reply by proceeding the story"""
    reply = request.args.get("reply")
    if not reply:
        return jsonify("Error: please provide a reply"), 400

    try:
        StoryController.proceed_story(user_id, reply)
    except UserReplyInvalid:
        return jsonify({"validReply": False, "messagesUpdated": False}), 200
    except IncompletedTaskActive:
        return jsonify({"validReply": True, "messagesUpdated": True}), 200
    except DatabaseError as e:
        return jsonify(f"Error: {e.args[0]}"), 400
    
    return jsonify({"validReply": True, "messagesUpdated": True}), 200

@app.route('/users/<user_id>/story/user-replies')
def get_user_replies(user_id):
    """Return reply options for user dependent on the current story point"""
    try:
        replies = StoryController.get_current_user_replies(user_id)
    except DatabaseError as e:
        return jsonify(f"Error: {e.args[0]}"), 400
    
    return jsonify(replies), 200

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

    StoryController.start_story(user_id)

    return jsonify("Successfull register"), 200
