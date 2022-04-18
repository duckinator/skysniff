#!/usr/bin/env python3

from functools import lru_cache as memoize
from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus
from datetime import datetime
import json
import sys

__author__ = 'Ellen Dash'
__version__ = '0.0.1'


class Nominatim:
    """Client for OpenStreetMap's Nominatim API."""

    # Throughout this class, a "Place" refers to
    #    https://wiki.openstreetmap.org/wiki/Key:place
    # Basically: a building, postcode, city, county, country, etc.

    def __init__(self, endpoint=None):
        if endpoint is None:
            endpoint = 'https://nominatim.openstreetmap.org/search.php'
        self.endpoint = endpoint

    @memoize()
    def address_to_places(self, address):
        """Given an address (string), returns a list of Places."""
        query = urlencode({
            'q': address,
            'format': 'json',
        }, quote_via=quote_plus)
        url = self.endpoint + '?' + query
        result = urlopen(url).read().decode()
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


class NWSApi:
    """Client for National Weather Service's weather.gov API."""

    def __init__(self):
        self.server = 'https://api.weather.gov'
        self.nominatim = Nominatim()

    @staticmethod
    def _get_json(url):
        """Given a URL, fetches it and attempts to parse it as JSON."""
        result = urlopen(url).read().decode()
        return json.loads(result)

    @memoize()
    def coords_to_gridpoint_url(self, coords):
        """Given (lat, long) coordinates, returns a Gridpoint API URL."""
        latitude, longitude = coords
        result = self._get_json(f'https://api.weather.gov/points/{latitude},{longitude}')
        properties = result['properties']
        grid_id = properties['gridId']
        grid_x = properties['gridX']
        grid_y = properties['gridY']
        return f'{self.server}/gridpoints/{grid_id}/{grid_x},{grid_y}'

    def address_to_gridpoint_url(self, address):
        """Given an address (string), return a Girdpoint API URL."""
        coords = self.nominatim.address_to_coords(address)
        return self.coords_to_gridpoint_url(coords)

    def raw_forecast(self, address):
        """Given an address, return a raw numerical forecast."""
        url = self.address_to_gridpoint_url(address)
        print(f'weather({address}) = {url}')
        return self._get_json(url)

    def forecast(self, address):
        """Given an address, return a textual forecast."""
        url = self.address_to_gridpoint_url(address) + '/forecast'
        print(f'forecast({address}) = {url}')
        return NWSForecastBaseline(self._get_json(url))

    def hourly(self, address):
        """Given an address, return a textual hourly forecast."""
        url = self.address_to_gridpoint_url(address) + '/forecast/hourly'
        print(f'hourly({address}) = {url}')
        return NWSForecastHourly(self._get_json(url))


class NWSForecastDefault:
    """Takes a `forecast` and provides functionality for rendering."""
    def __init__(self, forecast):
        self.forecast = forecast
        self.context = forecast.get('@context', None)
        self.geometry = forecast.get('geometry', None)
        self.properties = forecast.get('properties', None)
        self.type = forecast.get('type', None)

    @staticmethod
    def parse_time(datetime_str):
        """Given a date/time string, return an equivalent datetime` object."""
        return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')

    def render_debug(self):
        """Pretty-print the forecast."""
        import pprint  # pylint: disable=import-outside-toplevel
        return pprint.pformat(self.forecast, indent=4)

    def render_text(self):
        """Return a string explaining the forecast."""
        raise NotImplementedError


class NWSForecastBaseline(NWSForecastDefault):
    """NWS' baseline forecast."""

    def render_text(self, days=4):
        """Returns a string explaining the baseline forecast."""
        result = ""

        properties = self.properties
        periods = properties['periods']
        for i in range(0, days):
            period = periods[i]
            # TODO: Normalize the name, because changing shit like
            #       'Saturday' -> 'Independence Day' is annoying imo
            name = period['name']
            detailed_forecast = period['detailedForecast']

            start_time = self.parse_time(period['startTime'])
            # end_time = self.parse_time(period['endTime'])

            acceptable_modifiers = [
                'Overnight',
                'This Afternoon',
                'Tonight',
            ]

            if name in acceptable_modifiers:
                header = name
            else:
                modifier = ''
                if name.endswith(' Night'):
                    modifier = ' Night'
                header = start_time.strftime(f'%A{modifier} (%B %d)')

            result += header + "\n"
            result += ('-' * len(header)) + "\n"
            result += detailed_forecast
            if i != 6:
                result += "\n\n"

        return result


class NWSForecastHourly(NWSForecastDefault):
    """NWS' hourly forecast."""

    def render_text(self):
        """Return a string explaining the hourly forecast."""
        properties = self.properties
        periods = properties['periods']

        result = ""
        for i in range(0, 12):
            period = periods[i]

            start_time = self.parse_time(period['startTime'])
            temp = period['temperature']
            temp_unit = period['temperatureUnit']
            wind_speed = period['windSpeed']
            short_forecast = period['shortForecast']

            result += f"{start_time.strftime('%I%p')} {temp}°{temp_unit}, {short_forecast}, winds {wind_speed}\n"
        return result
