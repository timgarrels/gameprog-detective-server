import logging
from telegram.ext import Updater, CommandHandler
from telegram import Bot
import requests

from config import Config

# Logging for the bot as stdout wont work anymore
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

code_logger = logging.getLogger("code.logger")

# Basic Bot Communication setup
updater = Updater(token=Config.BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Buttons: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#build-a-menu-with-buttons

def telegram_handle():
    return Bot(Config.BOT_TOKEN).get_me()["username"]

def start(update, context):
    try:
        auth_key = context.args[0]
        response = requests.get("http://" +     Config.SERVER_URL + "/user/register/{}".format(auth_key),
            params={"telegramHandle": update.effective_user.username})
        if response.status_code == 200:
            # Successfully registered a new user telegram handle
            context.bot.send_message(chat_id=update.effective_chat.id, text="Greetings!")
            code_logger.info("Successfull start")
        else:
            # Invalid user auth key
            context.bot.send_message(chat_id=update.effective_chat.id, text="I don't know you!")
            context.bot.send_message(chat_id=update.effective_chat.id, text="I don't speak to strangers!")
            code_logger.info("Bad request: {}".format(response.json()))

    except IndexError:
        # No Auth key
        context.bot.send_message(chat_id=update.effective_chat.id, text="Who are you?")
        context.bot.send_message(chat_id=update.effective_chat.id, text="I don't speak to people who don't introduce themselves!")
        code_logger.info("Recieved start command without auth key")

# Handlers
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

code_logger.info(msg=telegram_handle())
# Start Bot
updater.start_polling()
updater.idle()
