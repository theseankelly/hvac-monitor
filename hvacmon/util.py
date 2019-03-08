#!/usr/bin/env python

import time
import datetime

def get_timestamp():
    """
    Gets an ISO8601 formatted timestamp.

    Returns
    -------
    string
        A timestamp formatted for ISO8601 with local zone info.
    """
    utc_offset_sec = \
        time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    timestamp = datetime.datetime.now().replace(
        tzinfo=datetime.timezone(offset=utc_offset)).isoformat()
    return timestamp
