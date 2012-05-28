#!/usr/bin/python

from dateutil.rrule import *
import datetime


def Date(year, month, day):
    """Simple wrapper to turn dates into `datetime`s."""
    return datetime.datetime(year, month, day, 0, 0)


class _Recurring(object):
    """Decide how often a `Transaction` occurs. `Transaction` has these."""

    # hack that allows miser to behave properly for past date ranges
    way_old_date=Date(2005, 1, 1)

    def __init__(self, frequency, **kwargs):
        """
        :Parameters:
            * `frequency`: a `dateutil` constant that defines this recurrence,
              e.g. `DAILY`, `WEEKLY`
            * `kwargs`: are valid arguments for `dateutil.rrule`s.
        """
        kwargs['dtstart'] = kwargs['dtstart'] or self.way_old_date
        self.rule = rrule(frequency, **kwargs)


class YearlyRecurring(_Recurring):

    def __init__(self, month, day, fromdt=None, todt=None):
        super(YearlyRecurring, self).__init__(YEARLY,
                                              bymonth=month,
                                              bymonthday=day,
                                              dtstart=fromdt,
                                              until=todt)


class MonthlyRecurring(_Recurring):

    def __init__(self, days, fromdt=None, todt=None):
        super(MonthlyRecurring, self).__init__(MONTHLY, bymonthday=days,
                                               dtstart=fromdt,
                                               until=todt)


class WeeklyRecurring(_Recurring):

    def __init__(self, days, fromdt=None, todt=None):
        super(WeeklyRecurring, self).__init__(WEEKLY, byweekday=days,
                                              dtstart=fromdt,
                                              until=todt)


class DailyRecurring(_Recurring):

    def __init__(self, fromdt=None, todt=None):
        super(DailyRecurring, self).__init__(DAILY,
                                             dtstart=fromdt,
                                             until=todt)
