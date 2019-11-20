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

def is_valid_start_token(start_token):
    r = requests.get(Config.SERVER_URL + "/user/register?telegram_handle={handle}&telegram_start_token={token}".format(handle="Mock handle", token=start_token))
    if r.status_code == 200:
        return r, True
    return r, False

def start(update, context):
    try:
        auth_key = context.args[0]
        response, valid = is_valid_start_token(auth_key)
        if valid:
            # Valid user auth key
            context.bot.send_message(chat_id=update.effective_chat.id, text="Hello there, General Kenobi!")
            context.bot.send_message(chat_id=update.effective_chat.id, text="You were registered!")
        else:
            # Invalid user auth key
            context.bot.send_message(chat_id=update.effective_chat.id, text="I don't know you!")
            context.bot.send_message(chat_id=update.effective_chat.id, text="I don't speak to strangers!")
            context.bot.send_message(chat_id=update.effective_chat.id, text="<invalid token>")

    except IndexError:
        # No Auth key
        context.bot.send_message(chat_id=update.effective_chat.id, text="Who are you?")
        context.bot.send_message(chat_id=update.effective_chat.id, text="I don't speak to people who don't introduce themselves!")
        context.bot.send_message(chat_id=update.effective_chat.id, text="<no token>")

# Handl##ers
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# Start Bot
updater.start_polling()
updater.idle()
