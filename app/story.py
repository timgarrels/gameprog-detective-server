"""Lookup Table for functions and placeholders referenced in story.json"""
import random
from app import db, app
from app.models.game_models import User
from app.models.userdata_models import Contact
from app.models.utility import db_single_element_query


# Task Validation Method Implementation
def go_to_hpi_validator(user_id):
    # TODO: Implement location check
    # Geopy
    # geonames.org
    # Find nearby populated place / reverse geocoding
    # Webservice Type : REST
    # Url : api.geonames.org/findNearbyPlaceName?
    # Parameters : lat,lng,
    return True

def hpi_student_contact_data_validator(user_id):
    contacts = Contact.query.filter_by(user_id=user_id)
    return bool(len(list(contacts)))

# Placeholder Method Implementation
def get_user_name(user_id):
    return db_single_element_query(User, {"user_id": user_id}, "user").firstname

def get_random_contact(user_id):
    contacts = list(Contact.query.filter_by(user_id=user_id))
    if len(contacts) == 0:
        return "Kevin"
    return random.choice(contacts).firstname

placeholder_getter = {
    "user_name": get_user_name,
    "mafia_boss": get_random_contact,
}