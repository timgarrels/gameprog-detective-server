""""Script to check story.json and story.py on missing references"""
from config import Config
import app.story.story as story_code
from app.story.story import start_point, story_points, tasks

import json
import re


def validate_story():
    """Makes sure story.json is consistent"""
    validate_references()
    validate_lookups()

def validate_references():
    """Makes sure all storypoints and tasks referenced in story.json are defined in story.json"""
    missing = {
        "points": set(),
        "tasks": set(),
    }

    existing_story_points = story_points.keys()
    referenced_story_points = []
    # referenced start point
    referenced_story_points.append(start_point)
    # referenced path destinations
    for story_point in story_points.values():
        destinations = story_point["paths"].values()
        referenced_story_points.extend(destinations)

    # find referenced, but undefined story points
    for referenced_story_point in referenced_story_points:
        if referenced_story_point not in existing_story_points:
            missing["points"].add(referenced_story_point)

    existing_tasks = tasks.keys()
    referenced_tasks = []
    # referenced tasks in story points
    for story_point in story_points.values():
        referenced_tasks.extend(story_point.get("tasks", []))

    # find referenced, but undefined tasks
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

    # Assert validation methods are in lookup table
    missing_validation_methods = set()

    for task in tasks.values():
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

    for story_point in story_points.values():
        for referenced_placeholder in re.findall(
            r"{(.*?)}", ''.join(story_point["description"]) + ''.join(story_point["paths"].keys())
        ):
            if not story_code.placeholder_getters.get(referenced_placeholder):
                missing_placeholders.add(referenced_placeholder)

    if missing_placeholders:
        raise KeyError(
            "There are referenced, but unkown placholders: {}".format(
                missing_placeholders
            )
        )
    print("All placeholder references found!")

if __name__ == "__main__":
    validate_story()
