import random
import string

from app import db

def create_telegram_start_token():
    alphabet = []
    alphabet.extend(string.ascii_letters)
    alphabet.extend(string.digits)
    return ''.join(random.choice(alphabet) for i in range(64))

def dict_keys_to_camel_case(d):
    converted_dict = {}
    for key, value in d.items():
        converted_dict[snake_to_camel_case(key)] = value
    return converted_dict

def snake_to_camel_case(s):
    # TODO: This has a few bugs:
    # abcAbc -> Abcabc instead of AbcAbc
    # abc__abc -> Abc_Abc
    # But suffices for Model key transfrom for now
    return ''.join(x.capitalize() or '_' for x in s.split('_'))

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telegram_handle = db.Column(db.String(64), nullable=True, unique=True)
    telegram_start_token = db.Column(db.String(64), nullable=False, unique=False, default=create_telegram_start_token)


    def as_dict(self):
        return dict_keys_to_camel_case({c.name: getattr(self, c.name) for c in self.__table__.columns})

    def __repr__(self):
        return "<User {}.{}>".format(self.id, self.telegram_handle)

class Contact(db.Model):
    __tablename__ = "contact"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    firstname = db.Column(db.String(64), nullable=True)
    lastname = db.Column(db.String(64), nullable=True)

    def as_dict(self):
        return dict_keys_to_camel_case({c.name: getattr(self, c.name) for c in self.__table__.columns})

    def __repr__(self):
        return "<Contact {}.{} {}".format(self.id, self.firstname, self.lastname)
