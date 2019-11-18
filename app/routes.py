from app import app
from flask import Response, jsonify, request
import json
from app.models import User
from app import db

# ---------- User Creation and Info ----------
@app.route('/user/all')
def all_users():
    return jsonify({"userIds": [id[0] for id in User.query.with_entities(User.user_id).all()]})

@app.route('/user/create')
def create_user():
    user = User()
    db.session.add(user)
    db.session.commit()
    return jsonify({"userId": user.user_id})

@app.route('/user/<user_id>')
def get_user(user_id):
    # TODO: jsonify does not work on this object
    try:
        user = User.query.get(int(user_id))
        return jsonify(user.to_dict()), 200
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400

@app.route('/user/<user_id>/register/<telegram_handle>')
def register_users_telegram_handle(user_id, telegram_handle):
    try:
        user = User.query.get(int(user_id))
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400
    if user.telegram_handle:
        # Telegram already registered for user
        return jsonify("Telegram already registerd for this user"), 400
    else:
        # Register user with telegram
        user.telegram_handle = telegram_handle
        db.session.add(user)
        db.session.commit()
        return jsonify("Successfull register"), 200

# ---------- User Data Dump ----------
@app.route('/user/<user_id>/data', methods=['POST'])
def recieve_user_data(user_id):

    data = request.get_json()

    if not data:
        return jsonify("Please provide data!"), 400

    data_origin = data.get("origin", None)
    data_type = data.get("type", None)

    if not data_origin:
        return jsonify("Please specify the data <origin>"), 400
    if not data_type:
        return jsonify("Please provide a <type>"), 400

    if data_origin not in ["app", "bot"]:
        return jsonify("I only take data <origin>ating from app or bot"), 400

    if data_type not in ["contact"]:
        return jsonify("I only handle contact data"), 400

    return data["first_name"], 200