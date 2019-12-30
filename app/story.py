"""Game Story Implementation: Import and Pogress"""
import json

from app import db
from app.models.models import User
from config import Config

class StoryController():
    """Method collection to handle story progression"""

    story = None
    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    start_point = story["story_start_point"]
    story_graph = story["story_graph"]
    story_content = story["story_content"]

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
        else:
            # Make sure reply is a valid reply
            reply_name = StoryController._reply_text_to_reply_name(user.current_story_point,
                                                                   last_reply)

            next_point = StoryController.story_graph[user.current_story_point][reply_name]
            user.current_story_point = next_point
            db.session.add(user)
            db.session.commit()

    def _reply_text_to_reply_name(current_story_point, reply_text):
        reply_dict = StoryController.story_content[current_story_point]["user_replies"]
        for name, text in reply_dict.items():
            if text == reply_text:
                return name
        raise ValueError("Invalid user reply")

    def current_bot_messages(user_id):
        """Returns the current messages to be sent by the bot"""
        user = User.query.get(user_id)
        if not user:
            return ["You are not even real!"]
        if not user.telegram_handle:
            return ["I dont know you!"]

        messages = StoryController.story_content[user.current_story_point]["messages"]
        return messages

    def current_user_replies(user_id):
        """Returns possible reply options available to the user_id in the current story state"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("No such user")
        if not user.telegram_handle:
            raise ValueError("No registerd telgram handle")

        story_point = StoryController.story_content[user.current_story_point]
        replies = list(story_point["user_replies"].values())
        return replies
