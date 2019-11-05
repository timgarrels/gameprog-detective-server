from flask import Blueprint, Response
from bson.json_util import dumps
from bson.objectid import ObjectId
from bson.errors import InvalidId
import global_vars

user_api = Blueprint('user_api', __name__)

@user_api.route('/create')
def create_user():
    new_user = global_vars.mongo.db.users.insert_one({})
    return Response(dumps(new_user.inserted_id), status=200,
    mimetype='application/json')

@user_api.route('/<userId>')
def get_user(userId):
    try:
        user = global_vars.mongo.db.users.find_one({"_id": ObjectId(userId)})
        return Response(dumps(user), status=200,
    mimetype='application/json')
    except InvalidId:
        return Response("Invalid userId!", status=400)

@user_api.route('/all')
def all_users():
    return Response(dumps(global_vars.mongo.db.users.find()), status=200,
    mimetype='application/json')
