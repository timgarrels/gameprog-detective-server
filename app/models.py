from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegam_handle = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<User {}.{}>'.format(self.id, self.telegam_handle)    