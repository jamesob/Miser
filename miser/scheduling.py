#!/usr/bin/python

from dateutil.rrule import *

class _Recurring(object):
    """Decide how often a `Transaction` occurs. `Transaction` has these."""


    def __init__(self, frequency, **kwargs):
        """
        :Parameters:
            * `frequency`: a `dateutil` constant that defines this recurrence,
              e.g. `DAILY`, `WEEKLY`
            * `kwargs`: are valid arguments for `dateutil.rrule`s.
        """
        self.rule = rrule(frequency, **kwargs)

class MonthlyRecurring(_Recurring):


    def __init__(self, days, fromdt = None, todt = None):
        super(MonthlyRecurring, self).__init__(MONTHLY, bymonthday=days,
                                               dtstart = fromdt,
                                               until = todt)

class WeeklyRecurring(_Recurring):


    def __init__(self, days, fromdt = None, todt = None):
        super(WeeklyRecurring, self).__init__(WEEKLY, byweekday=days,
                                              dtstart = fromdt,
                                              until = todt)

class DailyRecurring(_Recurring):


    def __init__(self, fromdt = None, todt = None):
        super(DailyRecurring, self).__init__(DAILY,
                                             dtstart = fromdt,
                                             until= todt)
     
