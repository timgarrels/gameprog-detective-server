from mongoengine import *

class User(Document):
    device_id = StringField(unique=True)
    telegram_handle = StringField(unique=True)