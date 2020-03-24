""""Script to check story.json and story.py on missing references"""
from config import Config
import app.story.story as story_code

import json
import re


def validate_story():
    """Makes sure story.json is consistent"""
    validate_references()
    validate_lookups()

def validate_references():
    """Makes sure all storypoints and tasks referenced in story.json are defined in story.json"""
    missing = {"points": set(),
               "tasks": set(),
               }

    story = None
    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    existing_story_points = story["story_points"].keys()

    referenced_story_points = []
    # Start point
    referenced_story_points.append(story["start_point"])
    # Actual story points
    referenced_story_points.extend(story["story_points"].keys())
    # Path Destinations
    for story_point in story["story_points"].keys():
        destinations = story["story_points"][story_point]["paths"].values()
        referenced_story_points.extend(destinations)

    # Find missing storypoints
    for referenced_story_point in referenced_story_points:
        if referenced_story_point not in existing_story_points:
            missing["points"].add(referenced_story_point)

    existing_tasks = story["tasks"].keys()
    referenced_tasks = []
    # Actual tasks
    referenced_tasks.extend(story["tasks"].keys())
    # Tasks in story points
    for story_point in story["story_points"].keys():
        tasks = story["story_points"][story_point]["tasks"]
        referenced_tasks.extend(tasks)
    # Find missing tasks
    for referenced_task in referenced_tasks:
        if referenced_task not in existing_tasks:
            missing["tasks"].add(referenced_task)

    if missing["points"]:
        raise KeyError("There are referenced, but unkown storypoints: {}".format(missing["points"]))

    if missing["points"]:
        raise KeyError("There are referenced, but unkown tasks: {}".format(missing["tasks"]))

    print("All references in story.json found!")

def validate_lookups():
    """Makes sure all task validation and placeholder methods referenced in story.json
    are implemented in story.py"""

    story = None
    with open(Config.STORY_FILE, "r") as story_file:
        story = json.loads(story_file.read())

    # Assert validation methods are in lookup table
    missing_validation_methods = set()

    for task in story["tasks"].values():
        referenced_validation_method = task["validation_method"]
        if referenced_validation_method not in missing_validation_methods:
            try:
                getattr(story_code, referenced_validation_method)
            except AttributeError:
                missing_validation_methods.add(referenced_validation_method)

    if missing_validation_methods:
        raise KeyError(
            "There are referenced, but unkown task validation methods: {}".format(
                missing_validation_methods
            )
        )

    print("All validtion method lookups found!")

    # Assert placeholder methods are in lookup table
    missing_placeholders = set()

    for story_point in story["tasks"].values():
        for referenced_placeholder in re.findall(r"{(.*?)}", ''.join(story_point["description"])):
            if not story_code.placeholder_getters.get(referenced_placeholder):
                missing_placeholders.add(referenced_placeholder)

    if missing_placeholders:
        raise KeyError(
            "There are referenced, but unkown placholders: {}".format(
                missing_placeholders
            )
        )

if __name__ == "__main__":
    validate_story()
