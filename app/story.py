"""Lookup Table for functions and placeholders referenced in story.json"""
from app import db
from app.models.userdata_models import Contact


# Task Validation Method Implementation
def go_to_hpi_validator(user_id):
    # TODO: Implement location check
    return True

def hpi_student_contact_data_validator(user_id):
    contacts = Contact.query.filter_by(user_id=user_id)
    return bool(len(list(contacts)))

# Placeholder Method Implementation
def placeholder_method_1(user_id):
    return "Filler"

def placeholder_method_2(user_id):
    return db.User.query.filter_by("something")[0]
