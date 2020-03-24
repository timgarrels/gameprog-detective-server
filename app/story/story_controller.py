"""Game Story Implementation: Import and Pogress"""
import re

import app.story.story as story_code
import app.story.personalizer as personalizer
import app.story.task_controller as task_controller
from app import db
from app.models.exceptions import DatabaseError
from app.models.game_models import User
from app.story.exceptions import StoryPointInvalid, UserReplyInvalid
from app.story.story import story, story_points, tasks


class StoryController():
    """Method collection to handle story progression"""

    @staticmethod
    def start_story(user_id):
        """sets the users current story point to the story start"""
        task_controller.reset_tasks(user_id)
        start_point = story["start_point"]
        StoryController.set_current_story_point(user_id, start_point)

    @staticmethod
    def get_current_story_point(user_id):
        """Returns the current story point for a given user"""
        user = User.get_user(user_id)
        if not user.current_story_point:
            raise DatabaseError(f"user {user_id} has no set story point")

        return user.current_story_point

    @staticmethod
    def set_current_story_point(user_id, story_point_name, reset_tasks=False):
        """Sets the current story point for a given user and activates associated tasks"""
        if story_point_name not in story_points.keys():
            raise StoryPointInvalid(f"story point {story_point_name} does not exist")
        if reset_tasks:
            task_controller.reset_tasks(user_id)
        user = User.get_user(user_id)
        user.current_story_point = story_point_name
        db.session.add(user)
        db.session.commit()

        new_tasks = story_points[story_point_name]["tasks"]
        if new_tasks:
            task_controller.assign_tasks(user_id, new_tasks)

    @staticmethod
    def proceed_story(user_id, reply):
        """Updates story point for given user and returns new bot messages and user replies"""
        if not StoryController.is_valid_reply(user_id, reply):
            raise UserReplyInvalid(f"'{reply}' is not a valid reply' for the current story point")

        incomplete_tasks = task_controller.get_incomplete_tasks(user_id)
        if incomplete_tasks:
            messages = tasks[incomplete_tasks[0]]["incomplete_message"]
        else:
            current_story_point = StoryController.get_current_story_point(user_id)
            personalized_paths = personalizer.personalize_paths(
                story_points[current_story_point]["paths"], user_id
            )
            next_story_point = personalized_paths[reply]
            StoryController.set_current_story_point(user_id, next_story_point)
            messages = StoryController.get_story_point_description(next_story_point)

        return personalizer.personalize_messages(messages, user_id)

    @staticmethod
    def get_story_point_description(story_point):
        """returns the description for a given story point"""
        return story_points[story_point]["description"]

    @staticmethod
    def get_possible_replies(story_point):
        """returns the possible user replies for a story point"""
        return list(story_points[story_point]["paths"].keys())

    @staticmethod
    def get_current_story_point_description(user_id):
        """returns the personalized current story description for a user"""
        story_point = StoryController.get_current_story_point(user_id)
        messages = StoryController.get_story_point_description(story_point)
        return personalizer.personalize_messages(messages, user_id)

    @staticmethod
    def get_current_user_replies(user_id):
        """Returns possible reply options available to the user_id in the current story state"""
        story_point = StoryController.get_current_story_point(user_id)
        replies = StoryController.get_possible_replies(story_point)
        return personalizer.personalize_messages(replies, user_id)

    @staticmethod
    def is_valid_reply(user_id, reply):
        """Whether a reply a user gave is possible based on his current storypoint"""
        return reply in StoryController.get_current_user_replies(user_id)

def validate_story():
    """Makes sure story.json is consistent"""
    validate_references()
    validate_lookups()

def validate_references():
    """Makes sure all storypoints and tasks referenced in story.json are defined in story.json"""
    missing = {"points": set(),
               "tasks": set(),
               }

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
