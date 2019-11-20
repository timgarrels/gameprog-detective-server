from app import db

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telegram_handle = db.Column(db.String(64), nullable=True, unique=True)


    def to_dict(self):
        return {"userId": self.user_id,
                "telegramHandle": self.telegram_handle}

    def __repr__(self):
        return '<User {}.{}>'.format(self.user_id, self.telegram_handle)