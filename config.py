import requests
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Server
    _SERVER_URL_ENV_VAR = "GP_SERVER_URL"
    try:
        SERVER_URL = os.environ[_SERVER_URL_ENV_VAR]
    except KeyError:
        print("You did not set {}".format(_SERVER_URL_ENV_VAR))
        exit()

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True

    # Bot
    BOT_TOKEN_ENV_VAR = "GP_TELEGRAM_BOT_TOKEN"
    try:
        BOT_TOKEN = os.environ[BOT_TOKEN_ENV_VAR]
    except KeyError:
        print("You did not set {}".format(BOT_TOKEN_ENV_VAR))
        exit()
    try:
        resp = requests.get("http://api.telegram.org/bot{token}/getMe".format(token=BOT_TOKEN))
        BOT_NAME = resp.json()["result"]["username"]
    except requests.exceptions.ConnectionError:
        print("No connecion, bot name will be set to default <andy abbot>")
        BOT_NAME = "andy abbot"

    STORY_FILE = os.path.join(basedir, "app/story.json")
