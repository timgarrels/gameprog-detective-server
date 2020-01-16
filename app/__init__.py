"""Creates Server to provide Game API"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from config import Config

# Create the flask app and the orm
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Setup API endpoint
from app.routes.app_api import *
from app.routes.bot_api import *
from app.routes.debug_api import *

# Create all tables
db.create_all()
db.session.commit()
