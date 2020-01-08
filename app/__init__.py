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

# Create the datatypes we can spy on
# TODO: Extract this to somewhere else?
# TODO: Use enum like object here
from app.models.userdata_models import Spydatatype
for i, handleable_datatype in enumerate(Spydatatype.handler_association.keys()):
    spydatatype = Spydatatype()
    spydatatype.name = handleable_datatype
    try:
        db.session.add(spydatatype)
        db.session.commit()
    except IntegrityError:
        # Can fail due to multiple initializations
        # Would violate NULL constraint of spydatatype.name
        pass
