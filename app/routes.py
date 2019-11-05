from app import app
from flask import Response, jsonify
from app.models import User


@app.route('/user/all')
def all_users():
    return str(User.query.all())