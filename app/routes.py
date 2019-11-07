from app import app
from flask import Response, jsonify, request
import json
from app.models import User
from app import db

# ---------- User Creation and Info ----------
@app.route('/user/all')
def all_users():
    # TODO: jsonify does not work on this object
    return jsonify(User.query.all())

@app.route('/user/create')
def create_user():
    user = User()
    db.session.add(user)
    db.session.commit()
    return jsonify({"userID": user.user_id})

@app.route('/user/<user_id>')
def get_user(user_id):
    # TODO: jsonify does not work on this object
    try:
        user = User.query.get(int(user_id))
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userID"), 400

@app.route('/user/<user_id>/register/<telegram_handle>')
def register_users_telegram_handle(user_id, telegram_handle):
    try:
        user = User.query.get(int(user_id))
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userID"), 400
    if user.telegram_handle:
        # Telegram already registered for user
        return jsonify("Telegram already registerd for this user"), 400
    else:
        # Register user with telegram
        user.telegram_handle = telegram_handle
        db.session.add(user)
        db.session.commit()
        return jsonify(True), 200

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

