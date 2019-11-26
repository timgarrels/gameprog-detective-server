import requests
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Server
    SERVER_URL = "http://0.0.0.0:5000"

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Bot
    BOT_TOKEN_ENV_VAR = "GP_TELEGRAM_BOT_TOKEN"
    try:
        BOT_TOKEN = os.environ[BOT_TOKEN_ENV_VAR]
    except KeyError:
        print("You did not set {}".format(BOT_TOKEN_ENV_VAR))
        exit()
    resp = requests.get("http://api.telegram.org/bot{token}/getMe".format(token=BOT_TOKEN))
    BOT_NAME = resp.json()["result"]["username"]

    STORY_FILE = os.path.join(basedir, "story.json")
