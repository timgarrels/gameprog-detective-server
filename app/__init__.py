"""Creates Server to provide Game API"""
# TODO: The use of init code is discouraged
# Also, app is a cyclic import app, app.routes, app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

# Create the flask app and the orm
# TODO: Should 'app', 'db' and 'migrate' be uppercase? Do we need 'migrate'?
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Setup API endpoint
from app.routes.app_api import *
from app.routes.bot_api import *
from app.routes.debug_api import *
