"""Server ORM"""
from app import db
from app.models import utility


class User(db.Model):
    """Models a user that plays our game"""
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telegram_handle = db.Column(db.String(64), nullable=True, unique=True)
    first_name = db.Column(db.String(64), nullable=True, unique=False)
    telegram_start_token = db.Column(db.String(64), nullable=False, unique=False,
                                     default=utility.create_telegram_start_token)
    current_story_point = db.Column(db.String(64), nullable=True, unique=False)
    requested_data_types = db.relationship("RequestedDatatype")
    task_assigments = db.relationship("TaskAssignment")

    def __repr__(self):
        return "<User {}.{}>".format(self.user_id, self.telegram_handle)

class TaskAssignment(db.Model):
    """Models an assigned (and maybe already completed) task to a user"""
    __tablename__ = "task_assignment"
    task_assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    task_name = db.Column(db.String(64))
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<TaskAssignment user:{} task:{}".format(self.user_id, self.task_id)