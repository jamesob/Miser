#!/usr/bin/python

from __future__ import print_function

import datetime
import operator

from .transactions import Income, Expense
from .buckets import Savings, Debt

import logging
log = logging.getLogger(__name__)


class Miser(object):
    """
    Holds `Transaction`s and `Bucket`s and plays out the interaction between
    the two, effectively creating a time-series of `Day`s.
    """

    def __init__(self, name):
        self.name = name

        #: holds Transaction objects
        self.transactions = []

        #: holds Debt bucket objects
        self.debts = []

        #: holds Savings bucket objects
        self.savings = []

        #: maps dates to Day objects
        self.days = {}

    def __getitem__(self, idx):
        """Get a MiserDay object.

        Args:
            idx (datetime.date): the day to retrieve

        Returns:
            MiserDay
        """
        return self.days[idx]

    def totals(self, begin, end):
        if (begin not in self.days) or (end not in self.days):
            self.simulate(begin, end)

        maxd = max(self.days.keys())
        return self.days[maxd].jsonDict

    def simulate(self, fromd, tod):
        """Run a simulation for this Miser collection over a certain period
        of time. Takes datetime.dates."""
        earliest = min(self.days.keys() or [None])

        if not earliest or (fromd < earliest):
            self._freshSimulation(fromd, tod)
        else:
            self._continueSimulation(fromd, tod)
            self.days = {}

    def _freshSimulation(self, fromd, tod):
        """Run a Miser simulation, disregarding any previous simulation
        data."""
        log.debug("First day of simulation: %s." % fromd)

        oned = datetime.timedelta(days=1)
        buckets = self.debts + self.savings

        self._initializeBuckets()
        self.days[fromd] = Day.first(fromd, self.transactions, buckets)

        self._continueSimulation(fromd + oned, tod)

    def _initializeBuckets(self):
        """Initialize the Savings/Debt buckets to a blank state."""
        for d in self.debts:
            d.init()

        for s in self.savings:
            s.init()

    def _continueSimulation(self, fromd, tod):
        """Extend a simulation, taking advantage of existing simulation
        data."""
        oned = datetime.timedelta(days=1)
        maxd = max(self.days.keys())
        lastd = maxd

        while lastd < tod:
            currd = lastd + oned

            if currd not in self.days:
                log.debug("Simulating new Day for %s." % currd)

                newday = Day.next(self.days[lastd])
                self.days[currd] = newday
            else:
                log.debug("Using existing day for %s." % currd)

            lastd = currd
            currd += oned

    def addDebt(self, d):
        self.debts.append(d)

    def addSavings(self, s):
        self.savings.append(s)

    def addTransactions(self, *trans):
        for t in trans:
            self.addTransaction(t)

    def addTransaction(self, trans):
        self.transactions.append(trans)

    def surplus(self, fromd, tod):
        """Return the difference of income to expenses over a period of
        time."""
        return self.income(fromd, tod) + self.expenses(fromd, tod)

    def income(self, fromd, tod):
        """Return a dict keyed by income Transactions and valued by their total
        amount over a period of time."""
        tot = self.totals(fromd, tod)

        return sum(tot['income'].values())

    def expenses(self, fromd, tod):
        """Return a dict keyed by expense Transactions and valued by their
        total amount over a period of time."""
        tot = self.totals(fromd, tod)

        return sum(tot['expenses'].values())


class Day(object):
    """
    Representation of the cumulative effects of a budget up until Day.date.

    Emphasis on cumulative: a single date is not indicative of the change seen
    by one single day, but the running accumulation of effects seen up to and
    including that day since the first day considered.
    """

    def __init__(self, date, expenses=None, incomes=None, buckets=None):
        """
        Args:
            expenses (dict)
            income (dict)
            date (date)
            buckets ([Bucket, ...])
        """
        self.date = date

        #: Keyed by Transactions, valued by net cumulative effect
        self.expenses = expenses or {}
        self.incomes = incomes or {}

        self.buckets = buckets or []

        #: Keyed by Buckets, valued by Bucket.snapshots
        self.savings = {}
        self.debts = {}

    @staticmethod
    def first(date, transactions, buckets):
        """Given a date and some transactions objects, return the effects of
        the transactions and the associated bucket objects."""
        newday = Day(date, buckets=buckets)

        for t in transactions:
            transdict = None

            if isinstance(t, Income):
                transdict = newday.incomes
            elif isinstance(t, Expense):
                transdict = newday.expenses

            transdict[t] = t.simulate(date)

        newday._buildBucketSnapshots(date)

        return newday

    @staticmethod
    def next(prev):
        """Return a constructed/simulated Day object for the day after
        `prev` Day."""
        newd = prev.date + datetime.timedelta(days=1)
        newday = Day(newd, prev.expenses, prev.incomes, prev.buckets)

        for transdict in (newday.expenses, newday.incomes):
            for t in transdict:
                if transdict.get(t):
                    transdict[t] += t.simulate(newday.date)
                else:
                    transdict[t] = t.simulate(newday.date)

        newday._buildBucketSnapshots(newd)

        return newday

    def _buildBucketSnapshots(self, date):
        """Simulate Bucket activity for a day and return the snapshots. To be
        run *after* all transactions have been run."""
        bucketdict = None

        for b in self.buckets:
            b.simulate(self.date)

            if isinstance(b, Savings):
                bucketdict = self.savings
            elif isinstance(b, Debt):
                bucketdict = self.debts

            bucketdict[b] = b.snapshot(date)['amount']

    @property
    def jsonDict(self):
        return {
            'expenses': self.expenses,
            'income': self.incomes,
            'savings': self.savings,
            'debt': self.debts,
        }


def dictToSortedList(inDict):
    return sorted(inDict.iteritems(), key=operator.itemgetter(1))


def to_datetime(date_thing):
    """Convert to datetime, if possible."""
    dt = datetime

    if type(date_thing) == dt.date:
        date_thing = dt.datetime.combine(date_thing, dt.time())

    return date_thing

