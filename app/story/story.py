"""Lookup Table for functions and placeholders referenced in story.json"""
import random
from datetime import time, timedelta
from app.models.game_models import User
from app.models.userdata_models import Contact
from app.models.utility import db_single_element_query
from app.story.utility import geo_close_to_place, user_at_location


# Task Validation Method Implementation
def go_to_hbf_validator(user_id):
    return user_at_location(user_id, "potsdam_hbf", timedelta(minutes=5), False)

def take_photo_from_cameras_validator(user_id):
    return True

# Placeholder Method Implementation
def get_user_name(user_id):
    return db_single_element_query(User, {"user_id": user_id}, "user").firstname

def get_random_contact(user_id):
    contacts = list(Contact.query.filter_by(user_id=user_id))
    if len(contacts) == 0:
        return "Kevin"
    return random.choice(contacts).firstname

placeholder_getters = {
    "user_name": get_user_name,
    "mafia_boss": get_random_contact,
}
