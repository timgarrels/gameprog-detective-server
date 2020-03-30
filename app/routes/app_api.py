"""API Endpoints used by the app"""
from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
import os
from pathlib import Path

from app import app
from app import db
from app.models.game_models import User, TaskAssignment
from app.models.userdata_models import spydatatypes, AccessCode
from app.story.task_controller import task_assignment_complete
from app.models.utility import db_single_element_query, db_entry_to_dict

from config import Config


@app.route('/users/create', methods=['POST'])
def create_user():
    """Creates a new user and replies his id and register url"""
    user = User()
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "userId": user.user_id,
        "registerURL": "telegram.me/{botname}?start={token}".format(
            botname=Config.BOT_NAME, token=user.token
        )
    }), 200

@app.route('/users/<user_id>/data/image', methods=['POST'])
def receive_image(user_id):
    if 'image' not in request.files:
        return jsonify("no 'image' field found"), 400
    image = request.files['image']
    if image.filename == '':
        return jsonify("no image was sent - did you choose one?")
    extension = image.filename.split('.')[-1]
    if extension not in Config.ALLOWED_IMAGE_EXTENSIONS:
        return jsonify("invalid file extension"), 400
    user_folder = os.path.join(Config.IMAGE_UPLOAD_FOLDER, f"user_{user_id}")
    Path(user_folder).mkdir(parents=True, exist_ok=True)
    filecount = len(os.listdir(user_folder))
    filename = f"image_{filecount + 1}.{extension}"
    image.save(os.path.join(user_folder, filename))
    return jsonify("image saved successfully"), 200

@app.route('/users/<user_id>/data/<data_type>', methods=['GET', 'POST'])
def user_data_by_type(user_id, data_type):
    """Either returns all existing data (GET) or adds new data (POST)"""

    data_table = spydatatypes.get(data_type, None)
    if not data_table:
        return jsonify("No such type {}".format(data_type)), 400

    try:
        # Assert user is existing
        db_single_element_query(User, {"user_id": user_id}, "user")
    except ValueError as e:
        return jsonify(str(e)), 400

    if request.method == "GET":
        return fetch_user_data_by_type(user_id, data_table)
    elif request.method == "POST":
        return recieve_user_data(user_id, data_table)

def fetch_user_data_by_type(user_id, data_table):
    """Returns all existing user data of a specified type"""

    formatted_data = [db_entry_to_dict(entry, camel_case=True) for entry in data_table.query.filter_by(user_id=user_id)]
    return jsonify(formatted_data), 200

def recieve_user_data(user_id, data_table):
    """Common data dump point. Applies various handlers to put provided
    data into the db"""
    try:
        data_handler = data_table.userdata_post_handler
    except AttributeError:
        return jsonify("Not userdata_post_handler for this datatype!"), 400

    data_array = request.get_json()
    if not data_array:
        return jsonify("Please provide json data!"), 400

    if not isinstance(data_array, list):
        return jsonify("Please provide a data list [dict, dict, ...]"), 400

    added_data = 0
    for data_dict in data_array:
        try:
            data_handler(user_id, data_dict)
            added_data += 1
        except (KeyError, IntegrityError) as error:
            return jsonify("Data could not be added: {}".format(error)), 400
    return jsonify("Added {} new entries to db".format(added_data)), 201

@app.route('/users/<user_id>/tasks/<task_name>/finished', methods=['GET'])
def check_task_finished(user_id, task_name):
    """check if task is complete"""
    try:
        task = TaskAssignment.query.filter_by(user_id=user_id,
                                              task_name=task_name).first()
    except ValueError:
        return jsonify("Invalid request"), 400

    if not task:
        return jsonify("No such task!"), 400

    return jsonify(task_assignment_complete(task, user_id)), 200

@app.route('/users/<user_id>/fbtoken/<fbtoken>', methods=['PUT'])
def update_firebase_token(user_id, fbtoken):
    """Set a new firebase token for a user"""
    try:
        user = db_single_element_query(User, {"user_id": user_id}, "user")
    except ValueError as e:
        return jsonify([str(e)]), 400

    user.firebase_token = fbtoken
    db.session.add(user)
    db.session.commit()
    return jsonify("Updated token!"), 200

@app.route('/users/<user_id>/phonenumber/<phone>', methods=['PUT'])
def update_phonenumber(user_id, phone):
    """Set a new phone number for a user"""
    try:
        user = db_single_element_query(User, {"user_id": user_id}, "user")
    except ValueError as e:
        return jsonify([str(e)]), 400

    user.phonenumber = phone
    db.session.add(user)
    db.session.commit()
    return jsonify("Updated phonenumber!"), 200

@app.route('/users/<user_id>/telegram-code/<code>', methods=['PUT'])
def receive_access_code(user_id, code):
    try:
        access_code = AccessCode.query.get(int(user_id))
        if access_code:
            access_code.code = code
        else:
            access_code = AccessCode(
                user_id=int(user_id),
                code=code
            )
    except ValueError:
        return jsonify("Invalid userId"), 400

    db.session.add(access_code)
    db.session.commit()
    return jsonify("Received Telegram Code!"), 200