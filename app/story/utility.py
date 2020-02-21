import requests
from xml.etree import ElementTree
from geopy.distance import distance

from app.models.game_models import User
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
    }
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
