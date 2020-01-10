"""Game Story Implementation: Import and Pogress"""
import json
import random

from app import db
from app.models.game_models import User, TaskAssignment
from app.models.userdata_models import Contact
from app.models.utility import db_single_element_query
from config import Config
from flask import jsonify

class StoryController():
    """Method collection to handle story progression"""

    story = None
    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    start_point = story["start_storypoint"]
    story_points = story["story_points"]
    tasks = story["tasks"]

    def assign_tasks(story_point, user_id):
        for task_name in StoryController.story_points[story_point]["tasks"]:
            task_assignment = TaskAssignment()
            task_assignment.user_id = user_id
            task_assignment.task_name = task_name
            db.session.add(task_assignment)
            db.session.commit()

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

        return [task.task_name for task in user.task_assigments]

    def personalize_messages(messages, user_id):
        user = db_single_element_query(User, {"user_id": user_id}, "user")
        #contacts = Contact.query.filter_by(user_id=user_id)
        user_data = {
            "user_name": user.first_name,
            #"random_contact": random.choice(contacts)
        }
        return [message.format(**user_data) for message in messages]

    def incomplete_message(user_id):
        """Returns the message of the first incomplete tasks of a certain user"""
        try:
            incomplete_task = StoryController.incomplete_tasks(user_id)[0]
            return StoryController.tasks[incomplete_task]["incomplete_message"]
        except IndexError:
            return ["Not incomplete tasks"]

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
