#!/usr/bin/python

from __future__ import print_function

import datetime
import operator
import collections
from dateutil.rrule import *


class Miser(object):
    """Holds `Transactions` and evaluates their net over a given period of time.
    Can evaluate how close to budget we are."""

    def __init__(self, name):
        self.name = name
        self.transactions = []
        self.goals = []

    def addGoal(self, g):
        self.goals.append(g)

    def addTransactions(self, *trans):
        for t in trans:
            self.addTransaction(t)

    def addTransaction(self, trans):
        self.transactions.append(trans)

    
    def _buildTotalsDict(self, fromdt, todt):
        """Return a dictionary that is keyed by transaction names and valued by
        the total amount of the transaction."""
        totDict = {}
        for t in self.transactions:
            totDict[t.name] = t.effectForPeriod(fromdt, todt)

        return totDict

    def _totalForPeriod(self, fromdt, todt):
        return sum(self._buildTotalsDict(fromdt, todt).values())

    def _goalsMetStr(self, fromdt, todt, totalSaved):
        retStr = ""
        for g in self.goals:
            if totalSaved >= g.amount:
                retStr += "Goal '%s' met with %.2f to spare!\n" \
                            % (g.name, totalSaved - g.amount)
            else:
                retStr += "Goal '%s' not met by %.2f. Womp.\n" \
                            % (g.name, g.amount - totalSaved)
        return retStr
                                       
    def goalsMet(self, fromdt, todt):
        """Which of your goals did you meet?"""
        print(self._goalsMetStr(fromdt, todt, 
                                self._totalForPeriod(fromdt, todt)))

    def summary(self, fromdt, todt):
        totalSaved = self._totalForPeriod(fromdt, todt) 
        sumStr = "%s: %s to %s\n" % (self.name, fromdt, todt)
        sumStr += "Total saved: %.2f" % totalSaved
        
        sumStr += "\n\nGoals:\n"
        sumStr += self._goalsMetStr(fromdt, todt, totalSaved)

        totalsDict = self._buildTotalsDict(fromdt, todt)
        sortedTotsList = dictToSortedList(totalsDict)

        expensesDict = dict([(k,v) for k,v in totalsDict.iteritems() if v < 0])
        incomeDict = dict([(k,v) for k,v in totalsDict.iteritems() if v > 0])

        mBar = _MiserBarVisualizer(incomeDict, expensesDict)

        sumStr += "\nProfile of expenses:"
        sumStr += mBar.expensesBar

        return sumStr

"""
Visualizer classes
------------------
"""

class _MiserBarVisualizer(object):
    """Takes in an `incomeDict` and `expensesDict`, dicts keyed by names and
    paired by amounts gained or spent, respectively over a period of time.
    Produces a bar graph of either."""

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
Transaction classes
-------------------
"""

class Transaction(object):
    """A `rule` for recurrence, an `amount` for how much money is involved, and
    a `name` for identification. `Miser` has these."""

    def __init__(self, name, amount, on):
        self.name = name
        self.dateRules = rruleset()
        self._amount = amount

        on = on if isinstance(on, collections.Iterable) else [on]

        # merge the incoming dateRules
        for dateOrRule in on:
            if isinstance(dateOrRule, _Recurring):
                self.dateRules.rrule(dateOrRule.rule)
            elif isinstance(dateOrRule, rrule): # accept `dateutil.rrule`s
                self.dateRules.rrule(dateOrRule)
            elif isinstance(dateOrRule, datetime.datetime):
                self.dateRules.rdate(dateOrRule)
            else:
                import sys
                print("Couldn't add date rules for transaction '%s'!",
                      file = sys.stderr)

    @property
    def amount(self):
        return self._amount

    def effectForPeriod(self, fromdt, todt):
        """Calculate the effect of a transaction over a period of
        time specified by `fromdt` to `todt`."""
        oneday = datetime.timedelta(1)
        # have to compensate for rrule.between being exclusive
        return len(self.dateRules.between(fromdt - oneday, todt + oneday)) \
                 * self.amount

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

"""
Goal
----
"""

class Goal(object):
    def __init__(self, name, amount, by):
        self.name = name
        self.amount = amount
        self.by = by

"""
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

