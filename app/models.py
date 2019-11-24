"""Server ORM"""
import random
import string

from app import db

def create_telegram_start_token():
    """Returns a random 64-len string"""
    alphabet = []
    alphabet.extend(string.ascii_letters)
    alphabet.extend(string.digits)
    return ''.join(random.choice(alphabet) for i in range(64))

def dict_keys_to_camel_case(dictionary):
    """Converts all keys in provided dict to camelCase"""
    converted_dict = {}
    for key, value in dictionary.items():
        converted_dict[snake_to_camel_case(key)] = value
    return converted_dict

def snake_to_camel_case(name):
    """snake_case String to camelCasse"""
    name = list(name)
    while "_" in name:
        idx = name.index("_")
        if idx + 1 < len(name):
            name[idx + 1] = name[idx + 1].capitalize()
        del name[idx]
    return ''.join(name)

class User(db.Model):
    """Models a user that plays our game"""
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telegram_handle = db.Column(db.String(64), nullable=True, unique=True)
    telegram_start_token = db.Column(db.String(64), nullable=False, unique=False,
                                     default=create_telegram_start_token)


    def as_dict(self):
        """As sqlalchemy obj cant be parsed to json we build a custom converter"""
        return dict_keys_to_camel_case(
            {c.name: getattr(self, c.name) for c in self.__table__.columns})

    def __repr__(self):
        return "<User {}.{}>".format(self.user_id, self.telegram_handle)

class Contact(db.Model):
    """Models a stolen contact from a user"""
    __tablename__ = "contact"
    contact_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    firstname = db.Column(db.String(64), nullable=True)
    lastname = db.Column(db.String(64), nullable=True)

    def as_dict(self):
        """As sqlalchemy obj cant be parsed to json we build a custom converter"""
        return dict_keys_to_camel_case(
            {c.name: getattr(self, c.name) for c in self.__table__.columns})

    def __repr__(self):
        return "<Contact {}.{} {}".format(self.contact_id, self.firstname, self.lastname)
