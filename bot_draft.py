import logging
from telegram.ext import Updater, CommandHandler
import requests


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


TOKEN = "1042823918:AAHiTdfqEu9viydzvPagWszqNw6LiPWutKA"
SERVER_URL = "localhost:5000/"

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def is_valid_auth(auth_key):
    r = requests.get(SERVER_URL + "/user/{}/register/{}".format(auth_key))
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


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
updater.idle()
