from app import app
from flask import Response, jsonify, request
import json
from app.models import User
from app import db
import os
import string
import random


# ---------- Utility ----------
@app.route('/bot/name')
def bot_name():
    """Returns the name (telegram_handle) of the bot"""
    # TODO: How does the server talk to the bot-module to retrieve the name?
    return "TODO"

# ---------- User Creation----------
@app.route('/user/create')
def create_user():
    """Called by the app to start register handshake.
    Adds a new user entry to the db, creates a telegram auth token and returns the new user_id and the token"""
    user = User()
    user.telegram_start_token = "".join(random.choice(string.ascii_letters) for i in range(64))
    db.session.add(user)
    db.session.commit()
    return jsonify({"userID": user.user_id,
                    "startToken": user.telegram_start_token})

@app.route('/user/register/<telegram_start_token>')
def register_users_telegram_handle(telegram_start_token):
    """Called by the bot to complete register handshake
        A Telegram Handle has to be provided in the get params.
        Said Telegram Handle will be associated with the user_id for provided auth token"""

    provided_telegram_handle = request.args.get("telegramHandle")
    user = User.query.filter_by(telegram_start_token=telegram_start_token).first()

    if not user:
        # Not user with specified auth_token
        return jsonify("Auth token invalid"), 400

    if not provided_telegram_handle:
        # No Handle provided to register
        return jsonify("Please provide a telegramHandle as parameter"), 400
    
    if user.telegram_handle:
        # User already registered with other handle
        return jsonify("Token already claimed"), 400

    user.telegram_handle = provided_telegram_handle
    db.session.add(user)
    db.session.commit()
    return jsonify("Registration succesfull"), 200

# ---------- User Data Dump ----------
@app.route('/user/<user_id>/data', methods=['POST'])
def recieve_user_data(user_id):
    data = request.get_json()
    if data.get('type') == 'contact':
        return "CONTACT READING NOT IMPLEMENTED YET"
    elif not data.get('type', None):
        return "Please provide a tpye"
    elif data.get('type') != 'contact':
        return "I only take 'contact' as type"
    return "Did not understand"

