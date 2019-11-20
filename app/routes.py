from app import app
from flask import Response, jsonify, request
import json
from app.models import User, Contact
from app import db
import subprocess
from datetime import datetime


# Git Webhook (Re-)Deployment
@app.route('/update', methods=['POST'])
def redeploy():
    try:
        subprocess.Popen(['git', 'pull'])
        subprocess.Popen(['echo', str(datetime.now()), '>>', 'logs/last_pull'])
        subprocess.Popen(['./restart.sh'])
    except Exception as e:
        return jsonify(e), 400
    return jsonify("Successfull Redeploy"), 200

# ---------- User Creation and Info ----------
@app.route('/user/all')
def all_users():
    return jsonify({"userIds": [id[0] for id in User.query.with_entities(User.id).all()]})

@app.route('/user/create')
def create_user():
    user = User()
    db.session.add(user)
    db.session.commit()
    return jsonify({"userId": user.id,
                    "registerURL": "telegram.me/{botname}?start={token}".format(botname=Config.BOT_NAME, token=user.telegram_start_token)})

@app.route('/user/<user_id>')
def get_user(user_id):
    # TODO: jsonify does not work on this object
    try:
        user = User.query.get(int(user_id))
        if user:
            return jsonify(user.as_dict()), 200
        else:
            return jsonify("No such user"), 400
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400

@app.route('/user/register')
def register_users_telegram_handle():
    telegram_handle = request.args.get("telegramHandle", None)
    telegram_start_token = request.args.get("TelegramStartToken", None)

    if not telegram_handle:
        return jsonify("Please provide a telegram_handle"), 400
    if not telegram_start_token:
        return jsonify("Please provivde a telegram_start_token"), 400

    try:
        user = User.query.filter_by(telegram_start_token=telegram_start_token).first()
    except ValueError:
        return jsonify("Invalid telegram_start_token"), 400

    if not user:
        return jsonify("No user with such token"), 400

    if user.telegram_handle:
        return jsonify("Telegram already registerd for this user"), 400

    user.telegram_handle = telegram_handle
    db.session.add(user)
    db.session.commit()
    return jsonify("Successfull register"), 200

# ---------- User Data Dump ----------
@app.route('/user/<user_id>/data', methods=['POST'])
def recieve_user_data(user_id):

    def contact_handler(contact):
        # TODO: Create a palce for handlers and extract this one
        if "firstname" not in contact or "lastname" not in contact:
            # Corrupt data
            return False
        else:
            contact = Contact(user_id=int(user_id),
                        firstname=contact.get("firstname"),
                        lastname=contact.get("lastname"))
            db.session.add(contact)
            db.session.commit()
        return True

    # TODO: Refactor data control flow
    datatype_handlers = {"contacts": contact_handler}
    json_data = request.get_json()

    if not json_data:
        return jsonify("Please provide data!"), 400

    data_origin = json_data.get("origin", None)
    data = json_data.get("data", {})

    if not data_origin:
        return jsonify("Please specify the data <origin>"), 400

    if data_origin not in ["app", "bot"]:
        return jsonify("I only take data <origin>ating from app or bot"), 400

    try:
        user = User.query.get(int(user_id))
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400

    if not user:
        return jsonify("No such user"), 400

    for datatype, value_list in data.items():
        # TODO: Handle data
        handled_types = {}
        if datatype in datatype_handlers.keys():
            handled_types[datatype] = 0

            for value in value_list:
                if datatype_handlers[datatype](value):
                    handled_types[datatype] += 1

    return jsonify("Added {} to db".format(handled_types)), 200

@app.route('/user/<user_id>/data/<datatype>')
def get_data_by_type(user_id, datatype):
    datatype_to_db_col = {"contacts": Contact}

    if datatype_to_db_col.get(datatype, None):
        contacts = datatype_to_db_col[datatype].query.filter_by(user_id=int(user_id)).all()
        return jsonify([contact.as_dict() for contact in contacts]), 200
    return jsonify("not implemented yet"), 400
