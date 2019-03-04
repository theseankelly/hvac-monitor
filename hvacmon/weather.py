#!/usr/bin/env python
import forecastio
import os
from hvacmon import util

def get_temperature():
    """
    Returns current temperature information through the DarkSky.

    API key and lat/long are exposed as environment variables:
    - DARKSKY_API_KEY
    - HVACMON_LAT
    - HVACMON_LON

    Returns
    -------
    string
        Timestamp of measurement

    float
        Current temperature information (deg F)
    """
    forecast = forecastio.load_forecast(
        os.environ['DARKSKY_API_KEY'],
        os.environ['HVACMON_LAT'],
        os.environ['HVACMON_LON'])
    temperature = forecast.currently().temperature
    timestamp = util.get_timestamp()
    return timestamp, temperature
