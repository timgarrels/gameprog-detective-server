"""Method collection to handle story personalization"""
import re

import app.story.story as story_code
from app import db
from app.models.exceptions import DatabaseError
from app.models.personalization_model import Personalization
from app.models.utility import db_entry_to_dict


def get_user_personalization(messages, user_id):
    """creates a dict with all placeholders found in messages"""
    user_personalization = Personalization.query.get(user_id)
    if not user_personalization:
        raise DatabaseError(f"there is no personalization entry for user {user_id}")

    # set used, but still undefined placeholders
    personalization_changed = False
    for placeholder in re.findall(r"{(.*?)}", ''.join(messages)):
        if getattr(user_personalization, placeholder) is None:
            setattr(
                user_personalization,
                placeholder,
                story_code.placeholder_getters[placeholder](user_id)
            )
            personalization_changed = True
    if personalization_changed:
        db.session.add(user_personalization)
        db.session.commit()

    return db_entry_to_dict(user_personalization)

def personalize_messages(messages, user_id):
    """Fills placeholders in messages with user related data"""
    user_personalization = get_user_personalization(messages, user_id)
    return [message.format_map(user_personalization) for message in messages]

def personalize_paths(paths, user_id):
    """Fills placeholders in a paths dict with user related data"""
    user_personalization = get_user_personalization(paths.keys(), user_id)
    return {k.format_map(user_personalization): v for k, v in paths.items()}
