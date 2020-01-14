import requests
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True

    BOT_TOKEN_ENV_VAR = "GP_TELEGRAM_BOT_TOKEN"
    try:
        BOT_TOKEN = os.environ[BOT_TOKEN_ENV_VAR]
    except KeyError:
        print("You did not set {}".format(BOT_TOKEN_ENV_VAR))
        exit()

    FIREBASE_URL_ENV_VAR = "GP_FIREBASE_URL"
    try:
        FIREBASE_URL = os.environ[FIREBASE_URL_ENV_VAR]
    except KeyError:
        print("You did not set {}".format(FIREBASE_URL_ENV_VAR))
        exit()

    try:
        resp = requests.get("http://api.telegram.org/bot{token}/getMe".format(token=BOT_TOKEN))
        BOT_NAME = resp.json()["result"]["username"]
    except requests.exceptions.ConnectionError:
        print("No connecion, bot name will be set to default <andy abbot>")
        BOT_NAME = "andy abbot"
    except KeyError:
        exit("Bot Name could not be parsed from telegram api. Maybe the bot token is out of date?")

    STORY_FILE = os.path.join(basedir, "app/story.json")
