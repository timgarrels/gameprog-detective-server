from app import app
from flask import Response, jsonify
from app.models import User
from app import db


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
    
