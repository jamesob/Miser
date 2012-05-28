#!/usr/bin/python

from __future__ import print_function

import datetime
import operator
import collections
from dateutil.rrule import *
from .scheduling import _Recurring


class Miser(object):
    """Holds `Transactions` and evaluates their net over a given period of time.
    Can evaluate how close to budget we are.
    """

    def __init__(self, name, initialBalance = 0):
        self.initialBalance = initialBalance
        self.name = name
        self.transactions = []
        self.goals = []

    def __getitem__(self, idx):
        """Get a MiserDay object.

        Args:
            idx (datetime.date): the day to retrieve

        Returns:
            MiserDay
        """
        exps = self.expenses(idx, idx)
        inc = self.income(idx, idx)

        return MiserDay(expenses=exps, income=inc)


    def addGoal(self, g):
        self.goals.append(g)

    def addTransactions(self, *trans):
        for t in trans:
            self.addTransaction(t)

    def addTransaction(self, trans):
        self.transactions.append(trans)

    def _buildTotalsDict(self, fromdt, todt, trans_type=None):
        """
        Return a dictionary that is keyed by Transactions and valued by
        the total amount of the Transaction.

        Args:
            fromdt (datetime.date)
            todt (datetime.date)
            trans_type (Transaction): only consider this specific type of
                transaction
        """
        trans = self.transactions

        if trans_type:
            trans = [t for t in trans if type(t) == trans_type]

        return {t: t.effectForPeriod(fromdt, todt) for t in trans}

    def totalSaved(self, fromdt, todt):
        """Return a scalar total of the net amount over a period of time."""
        return sum(self._buildTotalsDict(fromdt, todt).values()) \
                + self.initialBalance

    def goalStatus(self, fromdt, todt):
        """Return a dict keyed by Goals and valued by the difference between the
        total accumulated and the `Goal.amount`."""
        tot = self.totalSaved(fromdt, todt)
        return {g: (tot - g.amount) for g in self.goals}

    def income(self, fromdt, todt):
        """Return a dict keyed by income Transactions and valued by their total
        amount over a period of time."""
        return self._buildTotalsDict(fromdt, todt, Income)

    def expenses(self, fromdt, todt):
        """Return a dict keyed by expense Transactions and valued by their total
        amount over a period of time."""
        return self._buildTotalsDict(fromdt, todt, Expense)


class MiserDay(object):
    """
    Representation of a day; contains two dicts,

      - expenses
      - income

    both are keyed by Transaction objects and valued by their net effect.
    """

    def __init__(self, expenses=None, income=None):
        """
        Args:
            expenses (dict)
            income (dict)
        """
        self.expenses = expenses or {}
        self.income = income or {}

    @property
    def total_expenses(self):
        return sum(self.expenses.values())

    @property
    def total_income(self):
        return sum(self.income.values())

    @property
    def total(self):
        return self.total_income + self.total_expenses


class Transaction(object):
    """A `rule` for recurrence, an `amount` for how much money is involved, and
    a `name` for identification. `Miser` has these."""

    def __init__(self, name, amount, on, category=None):
        """
        :Parameters:
            - `name`
            - `amount`: Can be a scalar amount, the result of a generator, or a
            callable.
            - `on`: a `Datetime` or a `dateutil.rrule`
        """
        self.name = name
        self.category = category
        self.dateRules = rruleset()
        self._amount = amount

        on = on if isinstance(on, collections.Iterable) else [on]

        # merge the incoming dateRules
        for dateOrRule in on:
            recurrenceIs = lambda x: isinstance(dateOrRule, x)

        if recurrenceIs(_Recurring):
            self.dateRules.rrule(dateOrRule.rule)
        elif recurrenceIs(rrule):  # accept `dateutil.rrule`s
            self.dateRules.rrule(dateOrRule)
        elif recurrenceIs(datetime.datetime):
            self.dateRules.rdate(dateOrRule)
        else:
            import sys
            print("Couldn't add date rules for transaction '%s'!",
                  file=sys.stderr)

    def __repr__(self):
        return "%s: %s" % (self.__class__.__name__, self.name)

    @property
    def amount(self):
        if isinstance(self._amount, collections.Iterator):
            return self._amount.next()
        elif callable(self._amount):
            return self._amount()
        else:
            return self._amount

    def effectForPeriod(self, fromdt, todt):
        """Calculate the effect of a transaction over a period of
        time specified by `fromdt` to `todt`."""

        fromdt = to_datetime(fromdt)
        todt = to_datetime(todt)

        hits = self.dateRules.between(fromdt, todt, inc=True)

        # we must iterate in case self.amount is a generator
        amt = 0
        for i in range(len(hits)):
            amt += self.amount

        return amt

    def effectForDate(self, date):
        """Get the effect for a given datetime.date."""
        return effectForPeriod(date, date)


class Expense(Transaction):

    @property
    def amount(self):
        return -1. * super(Expense, self).amount


class Income(Transaction):
    pass


class Goal(object):

    def __init__(self, name, amount, by):
        self.name = name
        self.amount = amount
        self.by = by

"""
Utility functions
-----------------
"""


def dictToSortedList(inDict):
    return sorted(inDict.iteritems(), key=operator.itemgetter(1))


def to_datetime(date_thing):
    """Convert to datetime, if possible."""
    dt = datetime

    if type(date_thing) == dt.date:
        date_thing = dt.datetime.combine(date_thing, dt.time())

    return date_thing

if __name__ == '__main__':
    import doctest
    doctest.testmod()
