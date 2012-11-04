"""
Misc. utilities.
"""

import datetime


def to_dt(date):
    """Return a datetime from a dt."""
    return datetime.datetime.combine(date, datetime.time())

