#!/usr/bin/env python

from datetime import datetime

def get_timestamp(t = None):
    """
    Gets an ISO8601 formatted timestamp (UTC).

    Parameters
    ----------
    t : datetime.datetime, optional
        UTC timestamp to format. If not specified, current time is obtained.

    Returns
    -------
    string
        A timestamp formatted for ISO8601 in UTC.
    """
    if t is None:
        t = datetime.utcnow()

    timestamp = t.replace(
        tzinfo=None).isoformat(
            "T", "microseconds")
    return timestamp
