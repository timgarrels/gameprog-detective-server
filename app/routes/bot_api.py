"""API Endpoints used by the bot"""
from flask import request, jsonify

from app import app, db
from app.models.game_models import User
from app.story_controller import StoryController
from app.models.utility import db_single_element_query


@app.route('/users/<user_id>/story/proceed')
def try_to_proceed_story(user_id):
    """Tries to react to a provided reply by proceeding the story
    Returns bot-answers in any case"""
    reply = request.args.get("reply")
    if not reply:
        return jsonify(["Please provide a reply"]), 400

    # Return answers
    answers = StoryController.current_bot_messages(user_id, reply)
    return answers

@app.route('/users/<user_id>/story/user-replies')
def get_user_replies(user_id):
    """Return reply options for user dependent on the current story point"""
    replies = StoryController.current_user_replies(user_id)
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
    user.current_story_point = StoryController.initial_start_point
    db.session.add(user)
    db.session.commit()
    return jsonify("Successfull register"), 200
