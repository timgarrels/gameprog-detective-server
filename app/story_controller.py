"""Game Story Implementation: Import and Pogress"""
import json
import re
from flask import jsonify

from app import db
from app.models.game_models import User, TaskAssignment
from app.models.personalization_model import Personalization
from app.models.utility import db_single_element_query, db_entry_to_dict
import app.story
from app.story import placeholder_getters
from app.firebase_interaction import FirebaseInteraction
from config import Config

# TODO: split in parts
class StoryController():
    """Method collection to handle story progression"""

    story = None
    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    start_point = story["start_point"]
    story_points = story["story_points"]
    tasks = story["tasks"]

    # TODO: A artificial stroypoint could be avoided if the bot would handle /start differently
    # Add a artifical initial storypoint
    # Which leads to the start storypoint in story.json
    # This abstracts our engine of the users sight of story.json
    # This initial storypoint is proceeded by /start
    initial_start_point = "GP_INITIAL_STARTPOINT"
    story_points[initial_start_point] = {
        "description": [],
        "paths": {
            "/start": start_point
        },
        "tasks": []
    }

    @staticmethod
    def assign_tasks(story_point, user_id):
        """Assigns all tasks of a story point to a user
        Triggers app update with new tasks"""
        task_names = StoryController.story_points[story_point]["tasks"]
        for task_name in task_names:
            task_assignment = TaskAssignment()
            task_assignment.user_id = user_id
            task_assignment.task_name = task_name
            db.session.add(task_assignment)
            db.session.commit()

        tasks = [StoryController.task_name_to_dict(task_name) for task_name in task_names]
        FirebaseInteraction.update_tasks(user_id, tasks)

    @staticmethod
    def next_story_point(user_id, last_reply):
        """Updates db stored story point for given user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("No such user")
        if not user.handle:
            raise ValueError("User has no handle")

        # Make sure reply is a valid reply
        if last_reply not in StoryController.possible_replies(user.current_story_point):
            raise KeyError("Invalid reply to proceed from {}".format(user.current_story_point))

        story_point = StoryController._reply_text_to_storypoint(user.current_story_point,
                                                                last_reply)
        user.current_story_point = story_point
        StoryController.assign_tasks(story_point, user_id)

        db.session.add(user)
        db.session.commit()

    @staticmethod
    def possible_replies(story_point):
        return StoryController.story_points[story_point]["paths"].keys()

    @staticmethod
    def _reply_text_to_storypoint(current_story_point, reply_text):
        reply_dict = StoryController.story_points[current_story_point]["paths"]
        return reply_dict[reply_text]

    @staticmethod
    def _tasks_for_storypoint(story_point):
        tasks = []
        for task_name in story_point["tasks"]:
            tasks.append(StoryController.task_name_to_dict(task_name))
        return tasks

    @staticmethod
    def task_name_to_dict(task_name):
        task = StoryController.tasks[task_name]
        task.update([("name", task_name)])
        return task

    @staticmethod
    def incomplete_tasks(user_id):
        """Returns a list of incomplete tasks of a certain user"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("No such user")

        return [task.task_name for task in user.task_assigments if not task.finished]

    @staticmethod
    def personalize_messages(messages, user_id):
        """"Fills placeholders in messages with user related data"""
        user_personalization = db_single_element_query(Personalization, {"user_id": user_id}, "personalization")

        # set used, but still undefined placeholders
        personalization_changed = False
        for placeholder in re.findall(r"{(.*?)}", ''.join(messages)):
            if getattr(user_personalization, placeholder) is None:
                setattr(user_personalization, placeholder, placeholder_getters[placeholder](user_id))
                personalization_changed = True
        if personalization_changed:
            db.session.add(user_personalization)
            db.session.commit()
        
        return [message.format_map(db_entry_to_dict(user_personalization)) for message in messages]

    @staticmethod
    def incomplete_message(user_id):
        """Returns the message of the first incomplete tasks of a certain user"""
        try:
            incomplete_task = StoryController.incomplete_tasks(user_id)[0]
            return StoryController.tasks[incomplete_task]["incomplete_message"]
        except IndexError:
            return ["Not incomplete tasks"]

    @staticmethod
    def task_validation_method(task_name):
        """Gets the python validation method symbol for a sepcific task"""
        validation_method = StoryController.tasks[task_name]["validation_method"]
        return getattr(app.story, validation_method, None)

    # TODO: This currently holds too much logic
    # TODO: It decides what to do based on reply
    # TODO: Maybe we can extract that logic?
    @staticmethod
    def current_bot_messages(user_id, reply):
        """Returns the current messages to be sent by the bot"""
        user = User.query.get(user_id)
        if not user:
            return jsonify(["You are not even real!"]), 200
        if not user.handle:
            return jsonify(["I dont know you!"]), 200
        if not reply:
            return jsonify(["You are already in game! Please provide a reply"]), 200

        if not StoryController.valid_reply(user_id, reply):
            # Bot will answer nothing to invalid replies
            return jsonify([]), 200

        if StoryController.incomplete_tasks(user.user_id):
            # There are incomplete tasks
            messages = StoryController.incomplete_message(user.user_id)
        else:
            try:
                StoryController.next_story_point(user.user_id, reply)
            except ValueError as error:
                return jsonify([str(error)]), 400
            messages = StoryController.story_points[user.current_story_point]["description"]
        return jsonify(StoryController.personalize_messages(messages, user_id)), 200

    @staticmethod
    def valid_reply(user_id, reply):
        """Whether a reply a user gave is possible based on his current storypoint"""
        return reply in StoryController.current_user_replies(user_id) or "/start" in reply

    @staticmethod
    def current_user_replies(user_id):
        """Returns possible reply options available to the user_id in the current story state"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("No such user")
        if not user.handle:
            raise ValueError("No registerd telgram handle")
        if not user.current_story_point:
            return []

        story_point = StoryController.story_points[user.current_story_point]
        replies = list(story_point["paths"].keys())
        return replies

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

    if missing["points"]:
        raise KeyError("There are referenced, but unkown storypoints: {}".format(missing["points"]))

    if missing["points"]:
        raise KeyError("There are referenced, but unkown tasks: {}".format(missing["tasks"]))

    print("All references in story.json found!")

def validate_lookups():
    """Makes sure all task validation and placeholder methods referenced in story.json
    are implemented in story.py"""

    story = None
    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    # Assert validation methods are in lookup table
    missing_validation_methods = set()

    for task in story["tasks"].values():
        referenced_validation_method = task["validation_method"]
        if referenced_validation_method not in missing_validation_methods:
            try:
                getattr(app.story, referenced_validation_method)
            except AttributeError:
                missing_validation_methods.add(referenced_validation_method)

    if missing_validation_methods:
        raise KeyError(
            "There are referenced, but unkown task validation methods: {}".format(
                missing_validation_methods
            )
        )

    print("All validtion method lookups found!")

    # Assert placeholder methods are in lookup table
    missing_placeholders = set()

    for story_point in story["tasks"].values():
        for referenced_placeholder in re.findall(r"{(.*?)}", ''.join(story_point["description"])):
            if referenced_placeholder not in missing_placeholders:
                try:
                    getattr(app.story, placeholder_getters["referenced_placeholder"])
                except (KeyError, AttributeError):
                    missing_placeholders.add(referenced_placeholder)

    if missing_placeholders:
        raise KeyError(
            "There are referenced, but unkown placholders: {}".format(
                missing_placeholders
            )
        )
