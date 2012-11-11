"""
Misc. utilities.
"""

import datetime
import operator


def to_dt(date):
    """Return a datetime from a dt."""
    return datetime.datetime.combine(date, datetime.time())


def dictToSortedList(inDict):
    return sorted(inDict.iteritems(), key=operator.itemgetter(1))

