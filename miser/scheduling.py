#!/usr/bin/python

from dateutil import rrule
import datetime

import logging
log = logging.getLogger(__name__)


class Weekdays(object):
    """Constants indicating weekdays."""
    MO = rrule.MO
    TU = rrule.TU
    WE = rrule.WE
    TH = rrule.TH
    FR = rrule.FR
    SA = rrule.SA
    SU = rrule.SU


class _Recurring(object):
    """Decide how often a `Transaction` occurs. `Transaction` has these."""

    # hack that allows miser to behave properly for past date ranges
    way_old_date = datetime.date(2011, 1, 1)

    def __init__(self, frequency, **kwargs):
        """
        :Parameters:
            * `frequency`: a `dateutil` constant that defines this recurrence,
              e.g. `DAILY`, `WEEKLY`
            * `kwargs`: are valid arguments for `dateutil.rrule`s.
        """
        kwargs['dtstart'] = kwargs['dtstart'] or self.way_old_date
        kwargs['cache'] = True
        self.rule = rrule.rrule(frequency, **kwargs)


class YearlyRecurring(_Recurring):

    def __init__(self, month, day, begin=None, end=None):
        super(YearlyRecurring, self).__init__(rrule.YEARLY,
                                              bymonth=month,
                                              bymonthday=day,
                                              dtstart=begin,
                                              until=end)


class MonthlyRecurring(_Recurring):

    def __init__(self, *days, **kwargs):
        super(MonthlyRecurring, self).__init__(rrule.MONTHLY,
                                               bymonthday=days,
                                               dtstart=kwargs.get('begin'),
                                               until=kwargs.get('end'))


class WeeklyRecurring(_Recurring):

    def __init__(self, *days, **kwargs):
        super(WeeklyRecurring, self).__init__(rrule.WEEKLY,
                                              byweekday=days,
                                              dtstart=kwargs.get('begin'),
                                              until=kwargs.get('end'))


class DailyRecurring(_Recurring):

    def __init__(self, begin=None, end=None):
        super(DailyRecurring, self).__init__(rrule.DAILY,
                                             dtstart=begin,
                                             until=end)

