#!/usr/bin/env python
import forecastio
from hvacmon import util

class Weather:
    """
    Helper for obtaining weather information through the DarkSky API.

    Methods
    -------
    get_temperature()
        Gets a current temperature reading.
    """
    def __init__(self, api_key, lat, lon):
        """
        Initializes the object.

        Parameters
        ----------
        api_key : str
            Key to use with the DarkSky API.

        lat : float
            Latitude at which weather should be queried.

        lon : float
            Longitude at which weather should be queried.
        """
        self._api_key = api_key
        self._lat = lat
        self._lon = lon

    def get_temperature(self):
        """
        Gets current temperature information.

        Returns
        -------
        string
            Timestamp of measurement.

        float
            Current temperature information (deg F).
        """
        forecast = forecastio.load_forecast(
            self._api_key,
            self._lat,
            self._lon)
        temperature = forecast.currently().temperature
        timestamp = util.get_timestamp()
        return timestamp, temperature
