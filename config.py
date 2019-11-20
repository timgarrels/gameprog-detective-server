import os
basedir = os.path.abspath(os.path.dirname(__file__))

# TODO: This all should probably be in env instead

class Config(object):
    # Server
    SERVER_URL = "localhost:5000/"

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Bot
    BOT_TOKEN = "1042823918:AAHiTdfqEu9viydzvPagWszqNw6LiPWutKA"
