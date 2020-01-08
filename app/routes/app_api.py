"""API Endpoints used by the app"""
from flask import jsonify, request

from app import app
from app import db
from app.models.game_models import User, TaskAssignment
from app.models.userdata_models import Contact, Spydatatype
from app.story import StoryController

from config import Config


@app.route('/user/create')
def create_user():
    """Creates a new user and replies his id and register url"""
    user = User()
    db.session.add(user)
    db.session.commit()
    return jsonify({"userId": user.user_id,
                    "registerURL": "telegram.me/{botname}?start={token}".format(
                        botname=Config.BOT_NAME, token=user.telegram_start_token)})


@app.route('/user/<user_id>/fetchUserTasks')
def fetch_user_tasks(user_id):
    """Return all tasks (completed and uncompleted) assigned to a user"""
    try:
        tasks = TaskAssignment.query.filter_by(user_id=user_id)
    except ValueError:
        return jsonify("Invalid userId"), 400

    task_dicts = []
    for task in tasks:
        task_dict = StoryController._task_name_to_dict(task.task_name)
        task_dict.update([("completed", task.completed)])
        task_dicts.append(task_dict)
    return jsonify(task_dicts), 200


@app.route('/user/<user_id>/fetchBackgroundDataRequests')
def fetch_background_data_requests(user_id):
    """Return all data types we want to spy from a user account"""
    # TODO: The following creation of a user object with all fail checks is used a lot
    # and should be extracted into a method
    try:
        user = User.query.filter_by(user_id=user_id).first()
    except ValueError:
        return jsonify("Invalid userId"), 400

    if not user:
        return jsonify("No user with such Id"), 400

    return jsonify([request.as_dict() for request in user.requested_data_types]), 400

@app.route('/user/<user_id>/data/<data_type>', methods=['GET', 'POST'])
def user_data_by_type(user_id, data_type):
    """Either returns all existing data (GET) or adds new data (POST)"""

    if request.method == "GET":
        return fetch_user_data_by_type(user_id, data_type)
    elif request.method == "POST":
        return recieve_user_data(user_id, data_type)

def fetch_user_data_by_type(user_id, data_type):
    """Returns all existing user data of a specified type"""
    try:
        spydata_type = Spydatatype.query.filter_by(name=data_type).first()
    except ValueError:
        return jsonify("Invalid datatype"), 400

    if not spydata_type:
        return jsonify("No such datatype"), 400

    if not db_type_table:
        return jsonify("No such type {}".format(data_type)), 400

    formatted_data = [entry.as_dict() for entry in db_type_table.query.filter_by(user_id=user_id)]
    return jsonify(formatted_data), 200

def recieve_user_data(user_id, data_type):
    """Common data dump point. Applies various handlers to put provided
    data into the db"""
    try:
        data_handler = Spydatatype.handler_association.get(data_type)
    except KeyError:
        return jsonify("No such datatype {}".format(data_type)), 400
    except AttributeError:
        return jsonify("No handler for datatype {}".format(data_type)), 400

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
        return jsonify("Please provide data!"), d400

    if type(data) is not list:
        return jsonify("Please provide a data list [dict, dict, ...]"), 400

    added_data = 0
    for data_dict in data:
        try:
            data_handler(user_id, data_dict)
            update_requested_datatype(datatype, user_id)
            added_data += 1
        except KeyError as error:
            return jsonify("Data could not be added: {}".format(error)), 400
    return jsonify("Added {} new entries to db".format(added_data)), 200

# TODO
def update_requested_datatype(datatype, user_id):
    """Removes user -> datatype association in """

@app.route('/user/<user_id>/task/<task_id>/finished')
def is_task_finished(user_id, task_id):
    """Check whether a task is completed by a user"""
    # TODO: Is this endpoint necessary?
    # The app is "woken up", then checks all tasks it nows for a single user
    # Couldn't the app just request all tasks for a user, with the completed flags contained in the answer?

    try:
        task = TaskAssignment.query.filter_by(user_id=user_id,
                                              task_id=task_id).first()
    except ValueError:
        return jsonify("Task not assigned yet"), 400

    if not task:
        return jsonify("No such task!"), 400

    # TODO: Call tasks validate function to check whether task is completed by now
    # completed = task.validate_function(user)
    # update_task_status(user, task, completed)

    return task.completed

@app.route('/user/<user_id>/clues')
def get_clues(user_id):
    """Return all clues available to a user"""
    # TODO: Mock up
    return jsonify([{
        "personalized": True,
        "text": "Hello World",
        "name": "bla"
        }])
