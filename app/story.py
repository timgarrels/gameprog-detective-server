"""Lookup Table for functions and placeholders referenced in story.json"""
from app import db
from app.models.userdata_models import Contact

import random


# Task Validation Method Implementation
def go_to_hpi_validator(user_id):
    if random.random() > 0.7:
        return True
    return False

def hpi_student_contact_data_validator(user_id):
    contacts = Contact.query.filter_by(user_id=user_id)
    return bool(len(contacts))

# Task Validation Lookup Table
task_validation_lookup = {"go_to_hpi_validator": go_to_hpi_validator,
                          "hpi_student_contact_data_validator": hpi_student_contact_data_validator,
}


# Placeholder Method Implementation
def placeholder_method_1(user_id):
    return "Filler"

def placeholder_method_2(user_id):
    return db.User.query.filter_by("something")[0]

# Placeholder Lookup Table
placeholder_lookup = {"placeholder_name_1": placeholder_method_1,
                      "placeholder_name_2": placeholder_method_2,
}