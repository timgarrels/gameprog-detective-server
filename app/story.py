"""Lookup Table for functions and placeholders referenced in story.json"""
from app import db, app
from app.models.game_models import User
from app.models.userdata_models import Contact
from app.models.utility import db_single_element_query

import random


# Task Validation Method Implementation
def go_to_hpi_validator(user_id):
    # TODO: Implement location check
    return True

def hpi_student_contact_data_validator(user_id):
    contacts = Contact.query.filter_by(user_id=user_id)
    return bool(len(list(contacts)))

# Task Validation Lookup Table
task_validation_lookup = {"go_to_hpi_validator": go_to_hpi_validator,
                          "hpi_student_contact_data_validator": hpi_student_contact_data_validator,
}

# Placeholder Method Implementation
def assign_user_name(user_id):
    return db_single_element_query(User, {"user_id": user_id}, "user").firstname

def assign_random_contact(user_id):
    contacts = list(Contact.query.filter_by(user_id=user_id))
    if len(contacts) == 0:
        return "Kevin"
    return random.choice(contacts).firstname

# Placeholder Lookup Table
placeholder_assigner = {
    "user_name": assign_user_name,
    "mafia_boss": assign_random_contact,
}
