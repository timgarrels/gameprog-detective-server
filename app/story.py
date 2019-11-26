import json

from app import db
from config import Config

class StoryController(object):

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
            return -1
        if not user.telegram_handle:
            return -1
        
        if not user.current_story_point:
            # Start of Game
            user.current_story_point = StoryController.start_point
            db.session.add(user)
            db.session.commit()
        else:
            next_point = StoryController._getReplyToPointDict(user.current_story_point).get(last_reply, None)
            if not next_point:
                return -1
            user.current_story_point = next_point
            db.session.add(user)
            db.session.commit()
            
    
    def _getReplyToPointDict(current_story_point):
        # TODO: Undefined Behavior if a reply is defined two times for a story point
        point_reply_dict = StoryController.story_content[current_story_point]["user_replies"]
        reply_point_dict = {}
        for key, value in point_reply_dict.items():
            reply_point_dict[value] = key
        return reply_point_dict

    def current_bot_messages(user_id):
        """Returns the current messages to be sent by the bot"""
        user = User.query.get(user_id)
        if not user:
            return ["You are not even real!"]
        if not user.telegram_handle:
            return ["I dont know you!"]

        return ["Mock Message 1", "Mock Message 2"]

    def current_user_replies(user_id):
        """Returns possible reply options available to the user_id in the current story state"""
        user = User.query.get(user_id)
        if not user:
            return [" "]
        if not user.telegram_handle:
            return [" "]
        
        return ["Mock Reply Option 1", "Mock Reply Option 2"]