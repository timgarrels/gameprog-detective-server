from app import db
from app.models import utility


# TODO: extract data types in a enum like object
DATA_TYPES = ["CONTACT"]

class Contact(db.Model):
    """Models a stolen contact from a user"""
    __tablename__ = "contact"
    contact_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    firstname = db.Column(db.String(64), nullable=True)
    lastname = db.Column(db.String(64), nullable=True)

    def as_dict(self):
        """As sqlalchemy obj cant be parsed to json we build a custom converter"""
        return utility.dict_keys_to_camel_case(
            {c.name: getattr(self, c.name) for c in self.__table__.columns})

    def __repr__(self):
        return "<Contact {}.{} {}>".format(self.contact_id, self.firstname, self.lastname)
