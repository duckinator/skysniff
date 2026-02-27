from functools import cache
from datetime import datetime
import json
import logging

from . import http
from .nominatim import Nominatim

class NWSApi:
    """Client for National Weather Service's weather.gov API."""

    def __init__(self):
        self.server = 'https://api.weather.gov'
        self.nominatim = Nominatim()
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _get_json(url):
        """Given a URL, fetches it and attempts to parse it as JSON."""
        result = http.get(url)
        return json.loads(result)

    @cache
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
        """Given an address (string), return a Gridpoint API URL."""
        coords = self.nominatim.address_to_coords(address)
        return self.coords_to_gridpoint_url(coords)

    def raw_forecast(self, address):
        """Given an address, return a raw numerical forecast."""
        url = self.address_to_gridpoint_url(address)
        self.logger.debug(f'weather({address}) = {url}')
        return self._get_json(url)

    def forecast(self, address):
        """Given an address, return a textual forecast."""
        url = self.address_to_gridpoint_url(address) + '/forecast'
        self.logger.debug(f'forecast({address}) = {url}')
        return NWSForecastBaseline(self._get_json(url))

    def daily(self, address):
        return self.forecast(address)

    def hourly(self, address):
        """Given an address, return a textual hourly forecast."""
        url = self.address_to_gridpoint_url(address) + '/forecast/hourly'
        self.logger.debug(f'hourly({address}) = {url}')
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
