"""Bot Component of the Gameprog Seminar Project 'Detective Game'"""


import logging
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters

from config import Config
import telegram_interaction


def main():
    """Creates a running bot instance with logging and basic game message handlers"""
    # Logging for the bot as stdout wont work anymore
    # TODO: logger object to log in other script files
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Basic Bot Communication setup
    updater = Updater(token=Config.BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register \start command handler
    start_handler = CommandHandler('start', telegram_interaction.start_command_callback)
    dispatcher.add_handler(start_handler)

    # Register all purpose text handler
    text_handler = MessageHandler(Filters.all, telegram_interaction.reply)
    dispatcher.add_handler(text_handler)

    # Start Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
