from functools import cache
from urllib.parse import urlencode, quote_plus
import json

from . import http

class Nominatim:
    """Client for OpenStreetMap's Nominatim API."""

    # Throughout this class, a "Place" refers to
    #    https://wiki.openstreetmap.org/wiki/Key:place
    # Basically: a building, postcode, city, county, country, etc.

    def __init__(self, endpoint=None):
        if endpoint is None:
            endpoint = 'https://nominatim.openstreetmap.org/search'
        self.endpoint = endpoint

    @cache
    def address_to_places(self, address):
        """Given an address (string), returns a list of Places."""
        query = urlencode({
            'q': address,
            'format': 'json',
        }, quote_via=quote_plus)
        url = self.endpoint + '?' + query
        result = http.get(url)
        return json.loads(result)

    @staticmethod
    def place_to_coords(place):
        """Given a Place, returns (latitude, longitude)."""
        return (place['lat'], place['lon'])

    def address_to_coords(self, address):
        """Given a Place, returns a set of coordinates."""
        # TODO: Maybe do better than just picking the first item?
        places = self.address_to_places(address)
        return self.place_to_coords(places[0])

