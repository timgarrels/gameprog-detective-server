"""API Endpoints used by the app"""
from flask import jsonify, request

from app import app
from app import db
from app.models.game_models import User, TaskAssignment
from app.models.userdata_models import Contact
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
    return jsonify(tasks), 200


@app.route('/user/<user_id>/fetchBackgroundDataRequests')
def fetch_background_data_requests(user_id):
    """Return all data types we want to spy from a user account"""
    try:
        user = User.query.filter_by(user_id=user_id).first()
    except ValueError:
        return jsonify("Invalid userId"), 400

    if not user:
        return jsonify("No user with such Id"), 400

    return user.requested_data_types

# ---------- User Data Dump ----------
@app.route('/user/<user_id>/data', methods=['POST'])
def recieve_user_data(user_id):
    """Common data dump point. Applies various handlers to put provided
    data into the db"""

    # TODO: Needs refactor (data control flow, handler architecture)

    def contact_handler(contact):
        """Handler to put a single contact into the db"""
        # TODO: Create a palce for handlers and extract this one
        # Maybe the import of userdata_models together with the
        # game_models import is a hint to another abstraction possiblity?
        # Handlers should live in their DB model instance
        if "firstname" in contact and "lastname" in contact:
            contact = Contact(user_id=int(user_id),
                              firstname=contact.get("firstname"),
                              lastname=contact.get("lastname"))
            db.session.add(contact)
            db.session.commit()
            return True
        return False

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
