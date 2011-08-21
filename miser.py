#!/usr/bin/python

import datetime
from dateutil.rrule import *

class Miser(object):
    """Holds `Transactions` and evaluates their net over a given period of time.
    Can evaluate how close to budget we are.
 
    >>> from miser import *
    >>> m = Miser('test')
    >>> m.addTransactions(Income(name = 'job',
    ...                             amount = 1.5e3,
    ...                             on = MonthlyRecurring(7, 22)))
    >>> print(m._totalForPeriod(fromdt = Date(2011, 8, 20),
    ...                         todt = Date(2012, 8, 24)))
    37500.0

    >>> m.addTransactions(Expense(name = 'netflix',
    ...                              amount = 15,
    ...                              on = MonthlyRecurring(15)))
    >>> print(m._totalForPeriod(fromdt = Date(2011, 8, 20),
    ...                         todt = Date(2012, 8, 24)))
    37320.0

    >>> m.addTransactions(Expense(name = 'booze',
    ...                              amount = 20.,
    ...                              on = [WeeklyRecurring(MO), 
    ...                                    DailyRecurring()]))
    >>> print(m._totalForPeriod(fromdt = Date(2011, 8, 20),
    ...                         todt = Date(2012, 8, 24)))
    29920.0
        
    """

    def __init__(self, name):
        self.transactions = []
        self.goals = []

    def addGoal(self, g):
        self.goals.append(g)

    def addTransactions(self, *trans):
        for t in trans:
            self.transactions.append(t)

    def _totalForPeriod(self, fromdt, todt):
        return sum(map(lambda x: x.effectForPeriod(fromdt, todt), 
                       self.transactions))

    def summary(self, fromdt, todt):
        sumStr = "%s to %s:\n" % (fromdt, todt)
        sumStr += "Total: %.2f" % self._totalForPeriod(fromdt, todt)
        return sumStr

"""
Transaction classes
-------------------
"""

class Transaction(object):
    def __init__(self, name, amount, on):
        self.name = name
        self.dateRules = rruleset()
        self._amount = amount

        on = on if (type(on) == list) else [on]

        # merge the incoming dateRules
        for dateOrRule in on:
            if isinstance(dateOrRule, _Recurring):
                self.dateRules.rrule(dateOrRule.rule)
            elif isinstance(dateOrRule, datetime.datetime):
                self.dateRules.rdate(dateOrRule)

    @property
    def amount(self):
        return self._amount

    def effectForPeriod(self, fromdt, todt):
        """Calculate the effect of a transaction over a period of
        time specified by `fromdt` to `todt`."""
        return len(self.dateRules.between(fromdt, todt)) * self.amount

class Expense(Transaction):
    @property
    def amount(self):
        return -1. * self._amount

class Income(Transaction):
    pass

"""
Periodic occurrence classes
---------------------------
"""

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
        super(MonthlyRecurring, self).__init__(rrule(MONTHLY, bymonthday=days))

class WeeklyRecurring(_Recurring):
    def __init__(self, *days):
        super(WeeklyRecurring, self).__init__(rrule(WEEKLY, byweekday=days))

class DailyRecurring(_Recurring):
    def __init__(self, *days):
        super(DailyRecurring, self).__init__(rrule(DAILY))

class Goal(object):
    def __init__(self, amount, by):
        self.amount = amount
        self.by = by

"""
Utility functions
-----------------
"""

def Date(year, month, day):
    """Simple wrapper to turn dates into `datetime`s."""
    return datetime.datetime(year, month, day, 0, 0)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

