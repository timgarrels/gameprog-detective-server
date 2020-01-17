"""API Endpoints used by the app"""
from flask import jsonify, request

from app import app
from app import db
from app.models.game_models import User, TaskAssignment
from app.models.userdata_models import spydatatypes
from app.story_controller import StoryController
from app.models.utility import db_single_element_query

from config import Config


@app.route('/users/create')
def create_user():
    """Creates a new user and replies his id and register url"""
    user = User()
    db.session.add(user)
    db.session.commit()
    return jsonify({"userId": user.user_id,
                    "registerURL": "telegram.me/{botname}?start={token}".format(
                        botname=Config.BOT_NAME, token=user.token)})

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

    formatted_data = [entry.as_dict() for entry in data_table.query.filter_by(user_id=user_id)]
    return jsonify(formatted_data), 200

def recieve_user_data(user_id, data_table):
    """Common data dump point. Applies various handlers to put provided
    data into the db"""

    try:
        data_handler = data_table.userdata_post_handler
    except AttributeError:
        return jsonify("Not userdata_post_handler for this datatype!"), 400

    json_data = request.get_json()
    if not json_data:
        return jsonify("Please provide json data!"), 400

    data_origin = json_data.get("origin", None)
    data = json_data.get("data", [])

    if not data_origin:
        return jsonify("Please specify the data <origin>"), 400

    if data_origin not in ["app", "bot"]:
        return jsonify("I only take data <origin>ating from app or bot"), 400

    if not data:
        return jsonify("Please provide data!"), 400

    if not isinstance(data, list):
        return jsonify("Please provide a data list [dict, dict, ...]"), 400

    added_data = 0
    for data_dict in data:
        try:
            data_handler(user_id, data_dict)
            added_data += 1
        except KeyError as error:
            return jsonify("Data could not be added: {}".format(error)), 400
    return jsonify("Added {} new entries to db".format(added_data)), 200

@app.route('/users/<user_id>/tasks/<task_name>/finished')
def is_task_finished(user_id, task_name):
    """Check whether a task is finished by a user"""
    try:
        task = TaskAssignment.query.filter_by(user_id=user_id,
                                              task_name=task_name).first()
    except ValueError:
        return jsonify("Task not assigned yet"), 400

    if not task:
        return jsonify("No such task!"), 400

    validation_method = StoryController.task_validation_method(task_name)
    if not validation_method:
        return jsonify("No such task {}".format(task_name)), 400

    finished = validation_method(user_id)
    task.finished = finished
    db.session.add(task)
    db.session.commit()

    return jsonify(finished), 200

@app.route('/users/<user_id>/fbtoken/<fbtoken>')
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
