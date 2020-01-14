"""Game Story Implementation: Import and Pogress"""
import json

from app import db
from app.models.game_models import User, TaskAssignment
from app.models.utility import db_single_element_query
from app.story import task_validation_lookup, placeholder_lookup
from config import Config
from flask import jsonify

# TODO: temp
import requests


# TODO: split in parts
class StoryController():
    """Method collection to handle story progression"""

    story = None
    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    start_point = story["start_point"]
    story_points = story["story_points"]
    tasks = story["tasks"]

    def assign_tasks(story_point, user_id):
        for task_name in StoryController.story_points[story_point]["tasks"]:
            task_assignment = TaskAssignment()
            task_assignment.user_id = user_id
            task_assignment.task_name = task_name
            db.session.add(task_assignment)
            db.session.commit()
        # TODO: This is not the right place to implement this method
        StoryController.notify_app_task_update(user_id)

    def notify_app_task_update(user_id):
        # TODO: This is not the right place to implement this method
        # TODO: This should be in a sepearate module
        user = db_single_element_query(User, {"user_id": user_id}, "user")
        token = user.firebase_token

        tasks = []
        for assignment in user.task_assigments:
            tasks.append(StoryController._task_name_to_dict(assignment.task_name))

        resp = requests.post(
            "https://us-central1-detectivegame-1053a.cloudfunctions.net/newTasks?token={}".format(token),
            headers={'Content-type': 'application/json', 'Accept': 'text/plain'},
            data=json.dumps(tasks)
        )


    def next_story_point(user_id, last_reply):
        """Updates db stored story point for given user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("No such user")
        if not user.telegram_handle:
            raise ValueError("User has no handle")

        if not user.current_story_point:
            # Start of Game
            user.current_story_point = StoryController.start_point
            db.session.add(user)
            db.session.commit()
            StoryController.assign_tasks(StoryController.start_point, user_id)
        else:
            # Make sure reply is a valid reply
            story_point = StoryController._reply_text_to_storypoint(user.current_story_point,
                                                                   last_reply)

            user.current_story_point = story_point
            StoryController.assign_tasks(story_point, user_id)

            db.session.add(user)
            db.session.commit()

    def _reply_text_to_storypoint(current_story_point, reply_text):
        reply_dict = StoryController.story_points[current_story_point]["paths"]
        return reply_dict[reply_text]

    def _tasks_for_storypoint(story_point):
        tasks = []
        for task_name in story_point["tasks"]:
            tasks.append(StoryController._task_name_to_dict(task_name))
        return tasks

    def _task_name_to_dict(task_name):
        task = StoryController.tasks[task_name]
        task.update([("name", task_name)])
        return task

    def incomplete_tasks(user_id):
        """Returns a list of incomplete tasks of a certain user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("No such user")

        return [task.task_name for task in user.task_assigments if not task.finished]

    def personalize_messages(messages, user_id):
        user = db_single_element_query(User, {"user_id": user_id}, "user")
        user_data = {
            "user_name": user.first_name,
        }
        return [message.format(**user_data) for message in messages]

    def incomplete_message(user_id):
        """Returns the message of the first incomplete tasks of a certain user"""
        try:
            incomplete_task = StoryController.incomplete_tasks(user_id)[0]
            return StoryController.tasks[incomplete_task]["incomplete_message"]
        except IndexError:
            return ["Not incomplete tasks"]

    def task_validation_method(task_name):
        validation_method = StoryController.tasks[task_name]["validation_method"]
        return task_validation_lookup.get(validation_method, None)

    def current_bot_messages(user_id, reply):
        """Returns the current messages to be sent by the bot"""
        user = User.query.get(user_id)
        if not user:
            return jsonify(["You are not even real!"]), 200
        elif not user.telegram_handle:
            return jsonify(["I dont know you!"]), 200
        elif StoryController.incomplete_tasks(user.user_id):
            # There are incomplete tasks
            messages = StoryController.incomplete_message(user.user_id)
        elif not reply:
            return jsonify(["You are already in game! Please provide a reply"]), 200
        else:
            try:
                StoryController.next_story_point(user.user_id, reply)
            except ValueError as error:
                return jsonify([str(error)]), 400
            messages = StoryController.story_points[user.current_story_point]["description"]
        return jsonify(StoryController.personalize_messages(messages, user_id)), 200

    def current_user_replies(user_id):
        """Returns possible reply options available to the user_id in the current story state"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("No such user")
        if not user.telegram_handle:
            raise ValueError("No registerd telgram handle")

        story_point = StoryController.story_points[user.current_story_point]
        replies = list(story_point["paths"].keys())
        return jsonify(replies), 200


def validate_story():
    """Makes sure story.json is consistent"""
    validate_references()
    validate_lookups()

def validate_references():
    """Makes sure all storypoints and tasks referenced in story.json are defined in story.json"""
    missing = {"points": set(),
               "tasks": set(),
    }

    story = None
    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    existing_story_points = story["story_points"].keys()

    referenced_story_points = []
    # Start
    referenced_story_points.append(story["start_point"])
    # Actual story points
    referenced_story_points.extend(story["story_points"].keys())
    # Path Destinations
    for story_point in story["story_points"].keys():
        destinations = story["story_points"][story_point]["paths"].values()
        referenced_story_points.extend(destinations)
    
    for referenced_story_point in referenced_story_points:
        if referenced_story_point not in existing_story_points:
            missing["points"].add(referenced_story_point)

    existing_tasks = story["tasks"].keys()
    referenced_tasks = []
    # Actual tasks
    referenced_tasks.extend(story["tasks"].keys())
    # Tasks in story points
    for story_point in story["story_points"].keys():
        tasks = story["story_points"][story_point]["tasks"]
        referenced_tasks.extend(tasks)

    for referenced_task in referenced_tasks:
        if referenced_task not in existing_tasks:
            missing["tasks"].add(referenced_task)

    if len(missing["points"]):
        raise KeyError("There are referenced, but unkown storypoints: {}".format(missing["points"]))

    if len(missing["points"]):
        raise KeyError("There are referenced, but unkown tasks: {}".format(missing["tasks"]))

    print("All references in story.json found!")

def validate_lookups():
    """Makes sure all task validation and placeholder methods referenced in story.json 
    are implemented in story.py""" 
    # Assert referenced methods are implemented
    try:
        from app.story import task_validation_lookup, placeholder_lookup
    except NameError as e:
        exit("Not all references defined: {}".format(e))

    missing = {"task_validation_lookup": set(),
               "placeholder_lookup": set(),
    }

    story = None
    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    # Assert validation methods are in lookup table
    referenced_validation_methods = []

    for task in story["tasks"].keys():
        validation_method = story["tasks"][task]["validation_method"]
        referenced_validation_methods.append(validation_method)

    for referenced_validation_method in referenced_validation_methods:
        if referenced_validation_method not in task_validation_lookup.keys():
            missing["task_validation_lookup"].add(referenced_validation_method)

    if len(missing["task_validation_lookup"]):
        raise KeyError("There are referenced, but unkown task validation methods: {}".format(missing["task_validation_lookup"]))

    print("All validtion method lookups found!")
    # Assert placeholder methods are in lookup table
    # TODO: What can conatin a placeholder
