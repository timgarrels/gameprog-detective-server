from app import app
from flask import Response, jsonify, request
import json
from app.models import User, Contact
from app import db

# ---------- User Creation and Info ----------
@app.route('/user/all')
def all_users():
    return jsonify({"userIds": [id[0] for id in User.query.with_entities(User.id).all()]})

@app.route('/user/create')
def create_user():
    user = User()
    db.session.add(user)
    db.session.commit()
    return jsonify({"userId": user.id})

@app.route('/user/<user_id>')
def get_user(user_id):
    # TODO: jsonify does not work on this object
    try:
        user = User.query.get(int(user_id))
        return jsonify(user.as_dict()), 200
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

    def contact_handler(contact):
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
