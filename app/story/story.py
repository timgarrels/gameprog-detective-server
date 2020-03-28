"""Lookup Table for functions and placeholders referenced in story.json"""
import random
from datetime import time, timedelta
import json
import asyncio

from config import Config
from app.models.game_models import User
from app.models.userdata_models import Contact
from app.models.utility import db_single_element_query
from app.story.utility import geo_close_to_place, user_at_location
from app.telegram_highjack.telegram_highjack import hack_and_send_message


# Task Validation Method Implementation
def go_to_hbf_validator(user_id):
    return user_at_location(user_id, "potsdam_hbf", timedelta(minutes=5), False, time(hour=6), time(hour=23))

def go_to_hpi_validator(user_id):
    return user_at_location(user_id, "hpi", timedelta(minutes=5), False)

def arrest_suspect_validator(user_id):
    return user_at_location(user_id, "suspect_home", timedelta(minutes=2), False, time(hour=15, minute=55), time(hour=16, minute=5))

def observe_suspect_validator(user_id):
    return user_at_location(user_id, "pub_a_la_pub", timedelta(minutes=10), False, time(hour=21), time(hour=1))

def take_photo_from_cameras_validator(user_id):
    # sending the foto is mainly for atmosphere, so checking if it is actually valid has low pritority for now
    return True

def make_analyst_appointment_validator(user_id):
    # this is only on app side, we don't need to validate things here
    return True

# server actions
def telegram_highjack(user_id):
    user = db_single_element_query(User, {"user_id": user_id}, "user")
    if not user.phonenumber:
        return
    messages = []
    for creator in ["Adimeo", "Slerrag", "Paulpanther99", "robinwersich"]:
        messages.append((creator, f"Hey, {user.firstname} hier :)\nIch hab euer Spiel fertig gespielt und es ist echt cool!"))
    messages.append(("me", "Lege dich nicht mit der **MAFIA** an!"))
    asyncio.run(hack_and_send_message(int(user_id), user.phonenumber, messages))

# Placeholder Method Implementation
def get_user_name(user_id):
    return db_single_element_query(User, {"user_id": user_id}, "user").firstname

def get_random_contact(user_id):
    contacts = list(Contact.query.filter_by(user_id=user_id))
    if len(contacts) == 0:
        return random.choice(["Dave Connel", "Horst Helmut", "Tobias Schneider", "Melanie Hawks", "Katy Eggert", "Marie Kinzinger"])
    return random.choice(contacts).display_name_primary

placeholder_getters = {
    "user_name": get_user_name,
    "cyber_analyst": get_random_contact,
    "suspect": get_random_contact,
}

story = None
with open(Config.STORY_FILE, "r") as story_file:
    story = json.loads(story_file.read())

start_point = story["start_point"]
story_points = story["story_points"]
tasks = story["tasks"]