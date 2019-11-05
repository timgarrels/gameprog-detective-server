from flask import Flask
from flask_pymongo import PyMongo
from user_api import user_api
import global_vars

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/detective-game"
global_vars.mongo = PyMongo(app)

app.register_blueprint(user_api, url_prefix='/user')

