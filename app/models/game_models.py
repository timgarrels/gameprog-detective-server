"""Server ORM"""
from app import db
from app.models import utility
from app.models.exceptions import UserNotFoundError, UserNotRegisteredError

class User(db.Model):
    """Models a user that plays our game"""
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    handle = db.Column(db.String(64), nullable=True, unique=True)
    firstname = db.Column(db.String(64), nullable=True, unique=False)
    token = db.Column(db.String(64), nullable=False, unique=False,
                                     default=utility.create_token)
    current_story_point = db.Column(db.String(64), nullable=True, unique=False)
    firebase_token = db.Column(db.String(64), nullable=True, unique=True)
    phonenumber = db.Column(db.String(16), nullable=True)
    task_assigments = db.relationship("TaskAssignment")
    contacts = db.relationship("Contact")
    locations = db.relationship("Location")
    calendar_events = db.relationship("CalendarEvent")

    @staticmethod
    def get_user(user_id):
        """returns the user DB entry for a user id"""
        user = User.query.get(user_id)
        if not user:
            raise UserNotFoundError(f"user id {user_id} not in database")
        if not user.handle:
            raise UserNotRegisteredError(f"user {user_id} has not registered yet")

        return user

    def __repr__(self):
        return "<User {}.{}>".format(self.user_id, self.handle)

class TaskAssignment(db.Model):
    """Models an assigned (and maybe already finished) task to a user"""
    __tablename__ = "task_assignment"
    task_assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    task_name = db.Column(db.String(64))
    start_time_in_utc_seconds = db.Column(db.Integer, nullable=False)
    finished = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<TaskAssignment user:{} task:{}".format(self.user_id, self.task_id)
