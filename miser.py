#!/usr/bin/python

import datetime
import operator
from dateutil.rrule import *

class Miser(object):
    """Holds `Transactions` and evaluates their net over a given period of time.
    Can evaluate how close to budget we are."""

    def __init__(self, name):
        self.transactions = []
        self.goals = []

    def addGoal(self, g):
        self.goals.append(g)

    def addTransactions(self, *trans):
        for t in trans:
            self.transactions.append(t)
    
    def _buildTotalsDict(self, fromdt, todt):
        """Return a dictionary that is keyed by transaction names and valued by
        the total amount of the transaction."""
        totDict = {}
        for t in self.transactions:
            totDict[t.name] = t.effectForPeriod(fromdt, todt)

        return totDict

    def _totalForPeriod(self, fromdt, todt):
        return sum(self._buildTotalsDict(fromdt, todt).values())

    def summary(self, fromdt, todt):
        sumStr = "%s to %s\n" % (fromdt, todt)
        sumStr += "Total saved: %.2f" % self._totalForPeriod(fromdt, todt)

        totalsDict = self._buildTotalsDict(fromdt, todt)
        sortedTotsList = dictToSortedList(totalsDict)

        expensesDict = dict([(k,v) for k,v in totalsDict.iteritems() if v < 0])
        incomeDict = dict([(k,v) for k,v in totalsDict.iteritems() if v > 0])

        mBar = _MiserBarVisualizer(incomeDict, expensesDict)

        sumStr += "\n\nProfile of expenses:"
        sumStr += mBar.expensesBar

        return sumStr

"""
------------------
Visualizer classes
------------------
"""

class _MiserBarVisualizer(object):
    def __init__(self, incomeDict, expensesDict, numBars = 100):
        self.income = dictToSortedList(incomeDict)
        self.expenses = dictToSortedList(expensesDict)
        self.numBars = numBars
        
    def _createTextProfile(self, indict):
        """Create a bar-graph like representation of expenses and income."""

        keys = map(lambda x: x[0], indict)
        vals = map(lambda x: x[1], indict)

        outstrs = ["\n"]
        propDict = {}
        total = sum(vals)
        maxLenKey = max([len(a) for a in keys])
        maxLenVal = max([len(repr(a)) for a in vals]) 

        for k, v in indict:
            outstr = " "
            outstr += k.ljust(maxLenKey + 1)
            outstr += str(v).ljust(maxLenVal + 1)
            outstr += "-" * int(self.numBars * (v / total))
            outstrs.append(outstr)

        return "\n".join(outstrs)

    @property
    def incomeBar(self):
        return self._createTextProfile(self.income)
                                                   
    @property
    def expensesBar(self):
        return self._createTextProfile(self.expenses)
                                                   

"""
-------------------
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
---------------------------
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
-----------------
Utility functions
-----------------
"""

def Date(year, month, day):
    """Simple wrapper to turn dates into `datetime`s."""
    return datetime.datetime(year, month, day, 0, 0)

def dictToSortedList(inDict):
    return sorted(inDict.iteritems(), key=operator.itemgetter(1))

if __name__ == '__main__':
    import doctest
    doctest.testmod()

