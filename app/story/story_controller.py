"""Game Story Implementation: Import and Pogress"""
import json
import re
from flask import jsonify

from app import db
from app.story.exceptions import UserReplyInvalid, IncompletedTaskActive
from app.models.exceptions import UserNotFoundError, UserNotRegisteredError, DatabaseError
from app.models.game_models import User, TaskAssignment
from app.models.personalization_model import Personalization
from app.models.utility import db_single_element_query, db_entry_to_dict
import app.story.story as story_code
from app.firebase_interaction import FirebaseInteraction
from config import Config

# TODO: split in parts
class StoryController():
    """Method collection to handle story progression"""

    story = None
    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    story_points = story["story_points"]
    tasks = story["tasks"]

    # --- story logic ---
    @staticmethod
    def start_story(user_id):
        """sets the users current story point to the story start"""
        StoryController.reset_tasks(user_id)
        start_point = StoryController.story["start_point"]
        StoryController.set_current_story_point(user_id, start_point)

    @staticmethod
    def get_current_story_point(user_id):
        """Returns the current story point for a given user"""
        user = StoryController._get_user(user_id)
        if not user.current_story_point:
            raise DatabaseError(f"user {user_id} has no set story point")

        return user.current_story_point

    @staticmethod
    def set_current_story_point(user_id, story_point_name):
        """Sets the current story point for a given user and activates associated tasks"""
        user = StoryController._get_user(user_id)
        user.current_story_point = story_point_name
        db.session.add(user)
        db.session.commit()

        StoryController.assign_tasks(user_id, story_point_name)

    @staticmethod
    def proceed_story(user_id, reply):
        """Updates db stored story point for given user"""
        if not StoryController.is_valid_reply(user_id, reply):
            raise UserReplyInvalid(f"'{reply}' is not a valid reply' for the current story point")
        if StoryController.get_incomplete_tasks(user_id):
            raise IncompletedTaskActive(f"user {user_id} has incompleted tasks")
        
        current_story_point = StoryController.get_current_story_point(user_id)
        next_story_point = StoryController.story_points[current_story_point]["paths"][reply]
        StoryController.set_current_story_point(user_id, next_story_point)

    # --- tasks ---
    @staticmethod
    def assign_tasks(user_id, story_point_name):
        """Assigns all tasks of a story point to a user
        Triggers app update with new tasks"""
        task_names = StoryController.story_points[story_point_name]["tasks"]
        for task_name in task_names:
            task_assignment = TaskAssignment()
            task_assignment.user_id = user_id
            task_assignment.task_name = task_name
            db.session.add(task_assignment)
            db.session.commit()

        tasks = [StoryController.task_name_to_dict(task_name) for task_name in task_names]
        FirebaseInteraction.update_tasks(user_id, tasks)

    @staticmethod
    def reset_tasks(user_id):
        for assignment in TaskAssignment.query.filter_by(user_id=user_id):
            db.session.delete(assignment)
        db.session.commit()

    @staticmethod
    def task_name_to_dict(task_name):
        """returns the task dictionary for a task name"""
        task = StoryController.tasks[task_name]
        task.update([("name", task_name)])
        return task

    @staticmethod
    def get_incomplete_tasks(user_id):
        """Returns a list of incomplete tasks of a certain user"""
        user = StoryController._get_user(user_id)

        return [task.task_name for task in user.task_assigments if not task.finished]

    @staticmethod
    def task_validation_method(task_name):
        """Gets the python validation method symbol for a sepcific task"""
        validation_method = StoryController.tasks[task_name]["validation_method"]
        return getattr(story_code, validation_method, None)

    # --- messages ---
    @staticmethod
    def personalize_messages(messages, user_id):
        """Fills placeholders in messages with user related data"""
        user_personalization = Personalization.query.get(user_id)
        if not user_personalization:
            raise DatabaseError(f"there is no personalization entry for user {user_id}")

        # set used, but still undefined placeholders
        personalization_changed = False
        for placeholder in re.findall(r"{(.*?)}", ''.join(messages)):
            if getattr(user_personalization, placeholder) is None:
                setattr(user_personalization, placeholder, story_code.placeholder_getters[placeholder](user_id))
                personalization_changed = True
        if personalization_changed:
            db.session.add(user_personalization)
            db.session.commit()
        
        return [message.format_map(db_entry_to_dict(user_personalization)) for message in messages]

    @staticmethod
    def get_possible_replies(story_point):
        """returns the possible user replies for a story point"""
        return list(StoryController.story_points[story_point]["paths"].keys())

    @staticmethod
    def get_bot_messages(story_point):
        """returns the bot messages for a story point"""
        return StoryController.story_points[story_point]["description"]

    @staticmethod
    def get_current_bot_messages(user_id):
        """Returns the current messages to be sent by the bot"""        
        story_point = StoryController.get_current_story_point(user_id)
        
        incomplete_tasks = StoryController.get_incomplete_tasks(user_id)
        if incomplete_tasks:
            return StoryController.tasks[incomplete_tasks[0]]["incomplete_message"]

        messages = StoryController.get_bot_messages(story_point)
        return StoryController.personalize_messages(messages, user_id)

    @staticmethod
    def get_current_user_replies(user_id):
        """Returns possible reply options available to the user_id in the current story state"""
        story_point = StoryController.get_current_story_point(user_id)
        return StoryController.get_possible_replies(story_point)
    
    @staticmethod
    def is_valid_reply(user_id, reply):
        """Whether a reply a user gave is possible based on his current storypoint"""
        return reply in StoryController.get_current_user_replies(user_id)

    # --- utility ---
    @staticmethod
    def _get_user(user_id):
        """returns the user DB entry for a user id"""
        user = User.query.get(user_id)
        if not user:
            raise UserNotFoundError(f"user id {user_id} not in database")
        if not user.handle:
            raise UserNotRegisteredError(f"user {user_id} has not registered yet")
        
        return user

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
                getattr(story_code, referenced_validation_method)
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
            if not story_code.placeholder_getters.get(referenced_placeholder):
                missing_placeholders.add(referenced_placeholder)

    if missing_placeholders:
        raise KeyError(
            "There are referenced, but unkown placholders: {}".format(
                missing_placeholders
            )
        )
