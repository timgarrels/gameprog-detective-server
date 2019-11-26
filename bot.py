"""Bot Component of the Gameprog Seminar Project 'Detective Game'"""


import logging
import random
import time
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
from telegram import ReplyKeyboardMarkup, KeyboardButton
import requests

from config import Config

# --------- Uitility ---------
def get_answers(user, message):
    """This is the first main part of the bot.
    It asks the server for an answer depending on a telegram user and a send message"""
    response = requests.get(Config.SERVER_URL + "/user/answersForUserAndMessage?telegramUser={username}&message={msg}".format(username=user.username, msg=message.text))
    if response.status_code == 200:
        return response.json()
    logging.debug("The Server did not provide answers for username {username} and message {message}".format(
            username=user.username, message=message.text))
    logging.debug("Server Reply: {}".format(response.text))
    return []

def get_new_user_reply_options(user):
    """This i the second main part of the bot.
    It asks the server for replys depending on a telegram user.
    As the server knows the gamestate of that user it can provide individual replys"""

    response = requests.get(Config.SERVER_URL + "/user/replyOptionsForUser?telegramUser={username}".format(username=user.username))
    if response.status_code == 200:
        return response.json()
    logging.debug("The Server did not provide rep   ly options for username {username}".format(
        username=user.username))
    return []

def delay_answer(answer, update, context):
    """Sends a message delayed"""
    time.sleep(len(answer) * 0.04)
    context.bot.send_message(chat_id=update.effective_chat.id, text=answer)

def delay_reply_keyboard(reply_keyboard, keyboard_message_text, update, context):
    """Sends a message with a keyboard delayed"""
    time.sleep(len(keyboard_message_text) * 0.1)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=keyboard_message_text, reply_markup=reply_keyboard)

def send_filler(update, context):
    """We need to remove the old repy keyboard.
    Telegram API does not allow us to replace the keyboard with an empty one
    without a message send. Removing (not replacing) the keyboard would be possible,
    but makes the screen of the user jump up and down.
    This function chooses a filler like "I see" from a list (which should
    contain a lot of __small__ filler statements) and sends
    an empty keyboard to remove old keyboard"""
    # TODO: This is a hacky solution, but I did not find a better one
    # after exploring OneTimeKeyboards
    # Needs further discussion
    # Tim Garrels, 23_Nov_2019
    filler = random.choice(["I see", "If you say so", "Mh", "Ah"])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=filler, reply_markup=ReplyKeyboardMarkup([[KeyboardButton(" ")]]))

# ---------- Communication ----------
def reply(update, context, filler=True):
    """Proceesd the user in the story. Replys to message send by the player with API provided
    answers and displays new buttons"""
    answers = get_answers(update.effective_user, update.message)
    # We can not reply if we did not get at least one answer for the reply keyboard
    if answers:
        if filler:
            send_filler(update, context)
        # All messages require a text, even the reply markups. So reserve one answer for that markup
        keyboard_message_text = answers.pop()

        for answer in answers:
            delay_answer(answer, update, context)

        reply_options = sorted(get_new_user_reply_options(update.effective_user))
        if reply_options:
            reply_keyboard = ReplyKeyboardMarkup([
                [KeyboardButton(reply_option) for reply_option in reply_options]
            ])
            delay_reply_keyboard(reply_keyboard,
                                 keyboard_message_text, update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="You are out of luck, the server did not provide further interaction...")
    else:
        pass
        # context.bot.send_message(chat_id=update.effective_chat.id,
        #                          text="The server did not provide any answers at all")

# --------- Register handshake ---------
def try_to_register_user(start_token, user_handle):
    """ Calls register API endpoint to register the handle that provided a token.
    Returns True and response text if the register process was successfull (status 200),
    False and response text otherwise"""
    response = requests.get(Config.SERVER_URL + "/user/register?telegramHandle={handle}&telegramStartToken={token}".format(
            handle=user_handle, token=start_token))
    if response.status_code == 200:
        return True, response.text
    return False, response.text

def start_command_callback(update, context):
    """ Provides logic to handle a newly started chat with a user """
    user = update.effective_user
    chat_id = update.effective_chat.id

    try:
        auth_key = context.args[0]
        valid, response_text = try_to_register_user(auth_key, user.username)
        if valid:
            # Valid user auth key
            context.bot.send_message(chat_id=chat_id, text="Always nice to see new faces")
            reply(update, context, filler=False)
        else:
            # Invalid user auth key
            context.bot.send_message(chat_id=chat_id, text="I don't know you!")
            context.bot.send_message(chat_id=chat_id, text="I don't speak to strangers!")
            context.bot.send_message(chat_id=chat_id,
                                     text="Server Response:\n{}".format(response_text))

    except IndexError:
        # No Auth key
        context.bot.send_message(chat_id=update.effective_chat.id, text="Who are you?")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I don't speak to people who don't introduce themselves!")
        context.bot.send_message(chat_id=update.effective_chat.id, text="<no token>")


def main():
    """Creates a running bot instance with logging and basic game message handlers"""
    # Logging for the bot as stdout wont work anymore
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Basic Bot Communication setup
    updater = Updater(token=Config.BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher


    # Register \start command handler
    start_handler = CommandHandler('start', start_command_callback)
    dispatcher.add_handler(start_handler)

    # Register all purpose text handler
    text_handler = MessageHandler(Filters.all, reply)
    dispatcher.add_handler(text_handler)

    # Start Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
