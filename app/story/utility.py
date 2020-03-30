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

def user_at_location(
    user_id, place, lower_datetime_bound: int,
    time_window: (time, time) = (time.min, time.max), wait_time: timedelta=timedelta(0),
):
    """Utility method for any location task.
    Checks whether a user was/stayed at a place during/for a given timespan before now during a certain time period.
    :param place: key of places
    :param lower_datetime_bound: only take gps data after this timestamp (UTC seconds) into account
    :param time_window_: time of day window in which the location visit must have happened
    :param wait_time: the time the user has to wait at place. None, if no wait required"""
    relevant_locations = Location.query \
        .filter_by(user_id=user_id) \
        .filter(Location.time_in_utc_seconds >= lower_datetime_bound) \
        .order_by(Location.time_in_utc_seconds) \
        .all()
    
    waited_since = None
    for location in relevant_locations:
        location_datetime = datetime.fromtimestamp(location.time_in_utc_seconds)
        location_valid = \
            geo_close_to_place(location.latitude, location.longitude, place) and \
            time_between(location_datetime.time(), *time_window)
        if location_valid:
            waited_since = waited_since or location_datetime
            time_waited = location_datetime - waited_since
            if time_waited >= wait_time:
                return True
        else:
            waited_since = None
    return False
