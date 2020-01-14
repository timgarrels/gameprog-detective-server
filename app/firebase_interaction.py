from app.models.utility import db_single_element_query
from app.models.game_models import User
from config import Config

import requests
import json


class FirebaseInteraction():

    def execute_call(relative_url, user_id, data):
        """Builds the full and token-authorized firebase url
        and posts teh given data object as json"""
        try:
            user = db_single_element_query(User, {"user_id": user_id}, "user")
        except ValueError as e:
            return jsonify(str(e)), 400

        resp = requests.post(
            url=Config.FIREBASE_URL + relative_url + "?token={}".format(user.firebase_token),
            headers={'Content-type': 'application/json', 'Accept': 'text/plain'},
            data=json.dumps(data)
        )
        return resp


    def update_tasks(user_id, tasks):
        """Sends the whole task list of a user to the app"""
        endpoint = "/newTasks"
        FirebaseInteraction.execute_call(endpoint, user_id, tasks)
