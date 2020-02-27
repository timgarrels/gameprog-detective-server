import requests
from datetime import datetime, timedelta, time
from xml.etree import ElementTree
from geopy.distance import distance

from app.models.game_models import User
from app.models.userdata_models import Location
from app.models import utility


def geo_at_street(lat, lon, street):
    """Finds the closest address for given lat and lon and checks whether street is part of that adress
    Note: The API is really picky, and the gras behind the HPI is not part of the HPI anymore."""
    api_url = "https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}"
    url = api_url.format(lat=lat, lon=lon)
    resp = requests.get(url)
    root = ElementTree.fromstring(resp.content)
    for child in root:
        if child.tag == "result":
            if street in child.text:
                return True
    return False

places = {
    "hpi": {
        "coords": (52.394061, 13.131768),
        "radius": 230,
    },
    "potsdam_hbf": {
        "coords": (52.391735, 13.066694),
        "radius": 150,
    },
    "suspect_home": {
        "coords": (52.387768, 13.125900),
        "radius": 30,
    },
    "pub_a_la_pub": {
        "coords": (52.395616, 13.056481),
        "radius": 20,
    },
}
def geo_close_to_place(lat, lon, place):
    """Checks whether coords are in predefined radius to predefined place"""
    place_dict = places.get(place, None)
    if not place_dict:
        raise ValueError("No such place: {}".format(place))
    d = distance(place_dict["coords"], (lat, lon)).m
    if d < place_dict["radius"]:
        return True
    return False

def time_between(time, start, end):
    """returns if time is between start and end and takes over-midnight timespans into account"""
    if end > start:
        return start <= time and time <= end
    else:
        return start <= time or time <= end

def user_at_location(user_id, place, timespan: timedelta, waited: bool, time_window_start: time=time.min, time_window_end: time=time.max):
    """Utility method for any location task.
    Checks whether a user was/stayed at a place during/for a given timespan before now during a certain time period.
    place : key of places
    timespan : timespan before now in which user had to be at locations once or had to wait at location
    waited: if the user only had to be at location once during timespan or if he had to wait the whole time
    time_window_start/end: time of day window in which the location visit must have happened"""
    lower_time_barrier = (datetime.now() - timespan).timestamp()
    recent_locations = Location.query.filter_by(user_id=user_id).filter(Location.time_in_utc_seconds >= lower_time_barrier).all()

    locations_valid = \
        [geo_close_to_place(location.latitude, location.longitude, place) and \
        time_between(datetime.fromtimestamp(location.time_in_utc_seconds).time(), time_window_start, time_window_end) \
        for location in recent_locations]
    if waited:
        return bool(recent_locations) and all(locations_valid)
    else:
        return any(locations_valid)
