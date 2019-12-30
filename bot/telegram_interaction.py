"""Bot talking to a telegram user"""
import random
from telegram import ReplyKeyboardMarkup, KeyboardButton
import time

import server_interaction as server


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
    answers = server.get_answers(update.effective_user, update.message)
    # We can not reply if we did not get at least one answer for the reply keyboard
    if answers:
        if filler:
            send_filler(update, context)
        # All messages require a text, even the reply markups. So reserve one answer for that markup
        keyboard_message_text = answers.pop()

        for answer in answers:
            delay_answer(answer, update, context)

        reply_options = sorted(server.get_new_user_reply_options(update.effective_user))
        if reply_options:
            reply_keyboard = ReplyKeyboardMarkup([
                [KeyboardButton(reply_option) for reply_option in reply_options]
            ])
            delay_reply_keyboard(reply_keyboard,
                                 keyboard_message_text, update, context)
        else:
            debug_string = "You are out of luck, the server did not provide further interaction..."
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=debug_string,
                                     reply_markup=ReplyKeyboardMarkup([[KeyboardButton(" ")]]))
    else:
        pass
        # context.bot.send_message(chat_id=update.effective_chat.id,
        #                          text="The server did not provide any answers at all")

# --------- Register handshake ---------

def start_command_callback(update, context):
    """ Provides logic to handle a newly started chat with a user """
    user = update.effective_user
    chat_id = update.effective_chat.id

    # TODO: What does this do?
    # Nothing should happen if a user types "\start" if he is already registered
    if not server.user_already_registerd(user.username):
        try:
            auth_key = context.args[0]
            valid, response_text = server.try_to_register_user(auth_key, user.username)
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
