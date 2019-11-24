import requests
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# TODO: This all should probably be in env instead

class Config(object):
    # Server
    SERVER_URL = "http://localhost:5000"

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Bot
    BOT_TOKEN = "1042823918:AAG4KsDj7Epu3ol1hlUNuI953Ou88K9OL6w"
    resp = requests.get("http://api.telegram.org/bot{token}/getMe".format(token=BOT_TOKEN))
    BOT_NAME = resp.json()["result"]["username"]

