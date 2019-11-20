import logging
from telegram.ext import Updater, CommandHandler
import requests

from config import Config

# Logging for the bot as stdout wont work anymore
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Basic Bot Communication setup
updater = Updater(token=Config.BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def is_valid_auth(auth_key):
    r = requests.get(Config.SERVER_URL + "/user/{}/register/{}".format(auth_key))
    if auth_key in user_auth_association.values():
        return True
    return False

def start(update, context):
    try:
        auth_key = context.args[0]
        if is_valid_auth(auth_key):
            # Valid user auth key

            for user, value in user_auth_association.items():
                if value == auth_key:
                    username = key
                    break

            context.bot.send_message(chat_id=update.effective_chat.id, text="Hello there, General {}".format(username))
        else:
            # Invalid user auth key
            context.bot.send_message(chat_id=update.effective_chat.id, text="I don't know you!")
            context.bot.send_message(chat_id=update.effective_chat.id, text="I don't speak to strangers!")

    except IndexError:
        # No Auth key
        context.bot.send_message(chat_id=update.effective_chat.id, text="Who are you?")
        context.bot.send_message(chat_id=update.effective_chat.id, text="I don't speak to people who don't introduce themselves!")

# Handl##ers
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# Start Bot
updater.start_polling()
updater.idle()
