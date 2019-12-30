import requests
import os

print("-----------")
# TODO: We need a centralized config for both modules
print("THIS CONFIG IS A COPY; ITS TERRIBLE")
print("-----------")
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
    try:
        resp = requests.get("http://api.telegram.org/bot{token}/getMe".format(token=BOT_TOKEN))
        BOT_NAME = resp.json()["result"]["username"]
    except requests.exceptions.ConnectionError:
        print("No connecion, bot name will be set to default <andy abbot>")
        BOT_NAME = "andy abbot"

    STORY_FILE = os.path.join(basedir, "story.json")
