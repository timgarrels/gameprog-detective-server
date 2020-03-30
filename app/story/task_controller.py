"""Method collection to handle task assignment and completion"""
from datetime import datetime

import app.story.story as story_code
from app import db
from app.firebase_interaction import FirebaseInteraction
from app.models.game_models import TaskAssignment
from app.models.game_models import User
from app.story.story import tasks


def assign_tasks(user_id, task_names):
    """Assigns all tasks of a story point to a user
    Triggers app update with new tasks"""

    for task_name in task_names:
        task_assignment = TaskAssignment()
        task_assignment.user_id = user_id
        task_assignment.task_name = task_name
        task_assignment.start_time_in_utc_seconds = datetime.now().timestamp()
        db.session.add(task_assignment)
        db.session.commit()

    new_tasks = [task_name_to_dict_for_app(task_name) for task_name in task_names]
    FirebaseInteraction.update_tasks(user_id, new_tasks)

def reset_tasks(user_id):
    """removes all tasks for a user"""
    for assignment in TaskAssignment.query.filter_by(user_id=user_id):
        db.session.delete(assignment)
    db.session.commit()

def task_name_to_dict_for_app(task_name):
    """returns the task dictionary for the app for a task name"""
    task = tasks[task_name]
    app_task = {key: task[key] for key in ["description", "datatype"]}
    app_task.update([
        ("name", task_name),
        ("permissionExplanation", task.get(
            "permission_explanation",
            "Zur Überprüfung des Tasks brauchen wir die folgende Berechtigung"
            )
        )
    ])
    return app_task

def get_incomplete_tasks(user_id):
    """Returns a list of incomplete task names of a certain user"""
    user = User.get_user(user_id)
    return [task.task_name for task in user.task_assigments if not task_assignment_complete(task, user_id)]

def task_assignment_complete(task_assigment: TaskAssignment, user_id):
    """check if the given task assignment is complete and update database"""
    if not task_assigment.finished:
        validation_method_name = tasks[task_assigment.task_name]["validation_method"]
        validation_method = getattr(story_code, validation_method_name, None)
        task_assigment.finished = validation_method(user_id, task_assigment.start_time_in_utc_seconds)
        db.session.add(task_assigment)
        db.session.commit()
    return task_assigment.finished
