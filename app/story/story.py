"""Lookup Table for functions and placeholders referenced in story.json"""
import random
from datetime import datetime, timedelta
from app.models.game_models import User
from app.models.userdata_models import Contact, Location
from app.models.utility import db_single_element_query
from app.story.utility import geo_close_to_place


# Task Validation Method Implementation
def go_to_hbf_validator(user_id):
    location_valid_duration = timedelta(minutes=1)
    lower_time_barrier = (datetime.utcnow() - location_valid_duration).timestamp()
    recent_locations = Location.query.filter(Location.time_in_utc_seconds >= lower_time_barrier).all()

    return any(geo_close_to_place(location.latitude, location.longitude, "potsdam_hbf") for location in recent_locations)

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
