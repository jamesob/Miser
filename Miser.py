#!/usr/bin/python

import datetime
from dateutil.rrule import *

class Calendar(object):
    """Holds `Transactions` and evaluates their net over a given period of time.
    Can evaluate how close to budget we are."""

    def __init__(self):
        pass

class Transaction(object):
    def __init__(self, amount, dateRules):
        self._amount = amount
        self.dateRules = dateRules

    @property
    def amount(self):
        return self._amount

class Expense(Transaction):
    def amount(self):
        return -1. * self._amount

class Income(Transaction):
    pass

class _Recurring(object):
    def __init__(self, rule):
        """
        :Parameters:
            * `rules`: a list of `dateutil.rrule`s.
        """
        self.rule = rule

    def rulesToList(fromdt, todt):
        """Takes the object's rule and generates a list between a period of time
        specified by `fromdt` and `todt`."""
        return list(self.rule.between(fromdt, todt))

class MonthlyRecurring(_Recurring):
    def __init__(self, *days):
        self.__init__(rrule(MONTHLY, bymonthday=days))


class WeeklyRecurring(_Recurring):
    def __init__(self, *days):
        self.__init__(rrule(WEEKLY, byweekday=days))

class DailyRecurring(_Recurring):
    def __init__(self, *days):
        self.__init__(rrule(DAILY))

class Goal(object):
    def __init__(self, amount, by):
        self.amount = amount
        self.by = by

def date(year, month, day):
    """Simple wrapper to turn dates into `datetime`s."""
    return datetime.datetime(year, month, day, 0, 0)
