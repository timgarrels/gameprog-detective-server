"""Game Story Implementation: Import and Pogress"""
import json
import re
from flask import jsonify

from app import db
from app.story.exceptions import UserReplyInvalid, StoryPointInvalid
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
    def set_current_story_point(user_id, story_point_name, reset_tasks=False):
        """Sets the current story point for a given user and activates associated tasks"""
        if story_point_name not in StoryController.story_points.keys():
            raise StoryPointInvalid(f"story point {story_point_name} does not exist")
        if reset_tasks:
            StoryController.reset_tasks(user_id)
        user = StoryController._get_user(user_id)
        user.current_story_point = story_point_name
        db.session.add(user)
        db.session.commit()

        StoryController.assign_tasks(user_id, story_point_name)

    @staticmethod
    def proceed_story(user_id, reply):
        """Updates story point for given user and returns new bot messages and user replies"""
        if not StoryController.is_valid_reply(user_id, reply):
            raise UserReplyInvalid(f"'{reply}' is not a valid reply' for the current story point")

        incomplete_tasks = StoryController.get_incomplete_tasks(user_id)
        if incomplete_tasks:
            messages = StoryController.tasks[incomplete_tasks[0]]["incomplete_message"]
        else:
            current_story_point = StoryController.get_current_story_point(user_id)
            personalized_paths = StoryController.personalize_paths(StoryController.story_points[current_story_point]["paths"], user_id)
            next_story_point = personalized_paths[reply]
            StoryController.set_current_story_point(user_id, next_story_point)
            messages = StoryController.get_story_point_description(next_story_point)

        return StoryController.personalize_messages(messages, user_id)

    # --- tasks ---
    @staticmethod
    def assign_tasks(user_id, story_point_name):
        """Assigns all tasks of a story point to a user
        Triggers app update with new tasks"""
        task_names = StoryController.story_points[story_point_name]["tasks"]
        if not task_names:
            return
        
        for task_name in task_names:
            task_assignment = TaskAssignment()
            task_assignment.user_id = user_id
            task_assignment.task_name = task_name
            db.session.add(task_assignment)
            db.session.commit()

        tasks = [StoryController.task_name_to_dict_for_app(task_name) for task_name in task_names]
        FirebaseInteraction.update_tasks(user_id, tasks)

    @staticmethod
    def reset_tasks(user_id):
        """removes all tasks for a user"""
        for assignment in TaskAssignment.query.filter_by(user_id=user_id):
            db.session.delete(assignment)
        db.session.commit()

    @staticmethod
    def task_name_to_dict_for_app(task_name):
        """returns the task dictionary for the app for a task name"""
        task = StoryController.tasks[task_name]
        app_task = {key: task[key] for key in ["description", "datatype"]}
        app_task.update([
            ("name", task_name),
            ("permissionExplanation", task.get("permission_explanation", "Zur Überprüfung des Tasks brauchen wir die folgende Berechtigung"))
        ])
        return app_task

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
    def get_user_personalization(messages, user_id):
        """creates a dict with all placeholders found in messages"""
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
        
        return db_entry_to_dict(user_personalization)

    @staticmethod
    def personalize_messages(messages, user_id):
        """Fills placeholders in messages with user related data"""
        user_personalization = StoryController.get_user_personalization(messages, user_id)
        return [message.format_map(user_personalization) for message in messages]

    @staticmethod
    def personalize_paths(paths, user_id):
        """Fills placeholders in a paths dict with user related data"""
        user_personalization = StoryController.get_user_personalization(paths.keys(), user_id)
        return {k.format_map(user_personalization): v for k, v in paths.items()}

    @staticmethod
    def get_story_point_description(story_point):
        """returns the description for a given story point"""
        return StoryController.story_points[story_point]["description"]

    @staticmethod
    def get_possible_replies(story_point):
        """returns the possible user replies for a story point"""
        return list(StoryController.story_points[story_point]["paths"].keys())

    @staticmethod
    def get_current_story_point_description(user_id):
        """returns the personalized current story description for a user"""
        story_point = StoryController.get_current_story_point(user_id)
        messages = StoryController.get_story_point_description(story_point)
        return StoryController.personalize_messages(messages, user_id)

    @staticmethod
    def get_current_user_replies(user_id):
        """Returns possible reply options available to the user_id in the current story state"""
        story_point = StoryController.get_current_story_point(user_id)
        replies = StoryController.get_possible_replies(story_point)
        return StoryController.personalize_messages(replies, user_id)
    
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
