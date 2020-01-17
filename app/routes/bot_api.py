"""API Endpoints used by the bot"""
from flask import request, jsonify

from app import app, db
from app.models.game_models import User
from app.story_controller import StoryController
from app.models.utility import db_single_element_query


@app.route('/users/answersForUserAndReply')
def get_answers_for_user_and_reply():
    """Return answers the bot can give dependent on a user and his choice of reply"""
    telegram_user = request.args.get("bot_handle")
    if not telegram_user:
        return jsonify(["Please provide a username"]), 400
    reply = request.args.get("reply")

    try:
        user = db_single_element_query(User, {"telegram_handle": telegram_user}, "user")
    except ValueError as e:
        return jsonify([str(e)]), 400

    # Return answers
    answers = StoryController.current_bot_messages(user.user_id, reply)
    return answers

@app.route('/users/replyOptionsForUser')
def get_reply_options_for_user():
    """Return reply options for user dependent on current story point"""
    telegram_user = request.args.get("bot_handle")
    if not telegram_user:
        return jsonify("Please provide a username"), 400

    try:
        user = db_single_element_query(User, {"telegram_handle": telegram_user}, "user")
    except ValueError as e:
        return jsonify([str(e)]), 400

    replies = StoryController.current_user_replies(user.user_id)
    return jsonify(replies), 200

@app.route('/users/register')
def register_users_telegram_handle():
    """Registeres provided telegramHandle for a user.
    Last handshake action
    Requires a valid auth token"""
    telegram_handle = request.args.get("bot_handle", None)
    user_first_name = request.args.get("firstname", None)
    telegram_start_token = request.args.get("token", None)

    if not telegram_handle:
        return jsonify("Please provide a telegramHandle"), 400
    if not user_first_name:
        return jsonify("Please provide a userFirstName"), 400
    if not telegram_start_token:
        return jsonify("Please provide a telegramStartToken"), 400

    try:
        user = db_single_element_query(
            User,
            {"telegram_start_token": telegram_start_token},
            "startToken",
            )
    except ValueError as e:
        return jsonify([str(e)]), 400

    if user.telegram_handle:
        return jsonify("Telegram already registerd for this user"), 400

    try:
        users_with_same_handle = User.query.filter_by(telegram_handle=telegram_handle).first()
    except ValueError:
        return jsonify("Invalid telegramHandle"), 400

    if users_with_same_handle:
        return jsonify("This telegramHandle is already in use by another user"), 400

    user.telegram_handle = telegram_handle
    user.first_name = user_first_name
    db.session.add(user)
    db.session.commit()
    return jsonify("Successfull register"), 200
