"""API Endpoints used by the bot"""
from flask import request, jsonify

from app import app, db
from app.models.game_models import User
from app.models.personalization_model import Personalization
from app.story_controller import StoryController
from app.models.utility import db_single_element_query, as_dict


@app.route('/user/answersForUserAndReply')
def get_answers_for_user_and_reply():
    """Return answers the bot can give dependent on a user and his choice of reply"""
    telegram_user = request.args.get("telegramUser")
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

@app.route('/user/replyOptionsForUser')
def get_reply_options_for_user():
    """Return reply options for user dependent on current story point"""
    telegram_user = request.args.get("telegramUser")
    if not telegram_user:
        return jsonify("Please provide a username"), 400

    try:
        user = db_single_element_query(User, {"telegram_handle": telegram_user}, "user")
    except ValueError as e:
        return jsonify([str(e)]), 400

    replies = StoryController.current_user_replies(user.user_id)
    return jsonify(replies), 200

@app.route('/user/register')
def register_users_telegram_handle():
    """Registeres provided telegramHandle for a user.
    Last handshake action
    Requires a valid auth token"""
    telegram_handle = request.args.get("telegramHandle", None)
    user_firstname = request.args.get("userFirstName", None)
    telegram_start_token = request.args.get("telegramStartToken", None)

    if not telegram_handle:
        return jsonify("Please provide a telegramHandle"), 400
    if not user_firstname:
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
    user.firstname = user_firstname
    db.session.add(user)

    user_personalization = Personalization()
    user_personalization.user_id = user.user_id
    db.session.add(user_personalization)

    db.session.commit()
    return jsonify("Successfull register"), 200

# TODO: This should be in debug_api.py
# But bot.py is currently using this endpoint to check whether he should react to a \start command
@app.route('/user/byTelegramHandle')
def get_user_by_telegram_handle():
    """User Lookup by telegram handle"""
    telegram_handle = request.args.get("telegramHandle")
    if not telegram_handle:
        return jsonify("Please provide a telegramHandle"), 400

    try:
        user = db_single_element_query(User, {"telegram_handle": telegram_handle}, "user")
    except ValueError as e:
        return jsonify([str(e)]), 400

    return jsonify(as_dict(user, camel_case=True)), 200
