"""API Endpoints to get and reset data"""
import subprocess
import os
from flask import jsonify
from datetime import datetime

from app import app, db
from app.models.game_models import User, TaskAssignment
from app.models.userdata_models import Contact, spydatatypes
from app.models.utility import db_single_element_query
from app.story_controller import StoryController

# ---------- Git Webhook (Re-)Deployment ----------
@app.route('/update')
def redeploy():
    """Hook to redeploy prod server via github webhook
    Performs a git pull and a restart of server"""
    FNULL = open(os.devnull, 'w')
    try:
        # Make sure server is up to date
        subprocess.Popen(['git', 'pull'], stdout=FNULL)
        # Make sure there are no local changes on server
        subprocess.Popen(['git', 'reset', '--hard'], stdout=FNULL)
        # Log the pull
        with open('logs/last_pull', 'w+') as pull_log:
            pull_log.write(str(datetime.now()))
        # Restart the server
        subprocess.Popen(['./manage.sh', 'restart'], stdout=FNULL)
    except Exception as exception:
        return jsonify(str(exception)), 400
    return jsonify("Successfull Redeploy"), 200

# ---------- Display/Edit User Info ----------
@app.route('/user/<user_id>')
def get_user(user_id):
    """Returns a user dict"""
    try:
        user = User.query.get(int(user_id))
        if user:
            return jsonify(user.as_dict()), 200
        else:
            return jsonify("No such user"), 400
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400

@app.route('/user/<user_id>/reset')
def reset_user(user_id):
    """Resets users to 'before register' state"""
    try:
        user = User.query.get(int(user_id))
        if user:
            user.telegram_handle = None
            user.current_story_point = None
            db.session.add(user)

            for assignment in TaskAssignment.query.filter_by(user_id=user.user_id):
                db.session.delete(assignment)

            db.session.commit()

            return jsonify("User was reset"), 200
        else:
            return jsonify("No such user"), 400
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400

@app.route('/user/all')
def all_users():
    """Lists all created users"""
    users = User.query.with_entities(User.user_id).all()
    return jsonify({"userIds": [user_id[0] for user_id in users]}), 200

@app.route('/user/<user_id>/data/<datatype>')
def get_data_by_type(user_id, datatype):
    """Tries to fetch a specific datattype from the db"""
    datatype_to_db_col = {"contacts": Contact}

    if datatype_to_db_col.get(datatype, None):
        contacts = datatype_to_db_col[datatype].query.filter_by(user_id=int(user_id)).all()
        return jsonify([contact.as_dict() for contact in contacts]), 200
    return jsonify("not implemented yet"), 400


@app.route('/data/types')
def all_available_datatypes():
    return jsonify(spydatatypes.keys()), 200

@app.route('/user/<user_id>/task/all')
def fetch_user_tasks(user_id):
    """Return all tasks (finished and unfinished) assigned to a user"""
    try:
        tasks = TaskAssignment.query.filter_by(user_id=user_id)
    except ValueError:
        return jsonify("Invalid userId"), 400

    task_dicts = []
    for task in tasks:
        task_dict = StoryController._task_name_to_dict(task.task_name)
        task_dict.update([("finished", task.finished)])
        task_dicts.append(task_dict)
    return jsonify(task_dicts), 200