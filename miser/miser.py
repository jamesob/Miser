#!/usr/bin/python

from __future__ import print_function

import datetime

from .transactions import Transaction, Income, Expense
from .buckets import Savings, Debt

import logging
log = logging.getLogger(__name__)


class Miser(object):
    """
    Entrypoint for adding `Transaction`s and playing out their effect over a
    period of time. Delivers a time-series of `Day`s as returned in a
    `Simulation` object.
    """

    def __init__(self, name):
        self.name = name

        #: holds Transaction objects
        self.transactions = []

    def simulate(self, fromd, tod, exclude_trans=None):
        """
        Run a Miser simulation, disregarding any previous simulation
        data.

        Kwargs:
            exclude_trans ([Transaction, ...]): exclude a list of transactions
                from this simulation
        """
        log.debug("First day of simulation: %s." % fromd)
        trans = self.transactions

        if exclude_trans:
            trans = self._transWithExclusion(exclude_trans)

        return Simulation.fromFirstDay(Day.first(fromd, trans), tod)

    def _transWithExclusion(self, to_exclude):
        """Return a list of self.transactions with `to_exclude` excluded."""
        return [t for t in self.transactions if t not in to_exclude]

    def addTransactions(self, *trans):
        for t in trans:
            self.addTransaction(t)

    def addTransaction(self, trans):
        self.transactions.append(trans)


class Simulation(object):
    """Represents a budget simulation; holds a series of `Day`s and provides
    various statistics."""

    def __init__(self, days):
        #: holds Debt bucket objects
        self.debts = days[0].debts.keys() if days else []

        #: holds Savings bucket objects
        self.savings = days[0].savings.keys() if days else []

        #: maps dates to Day objects
        self.days = {d.date: d for d in days}

    def __getitem__(self, idx):
        """
        Get a Day object.

        Args:
            idx (datetime.date): the day to retrieve
        """
        return self.days[idx]

    @staticmethod
    def fromFirstDay(day, tod):
        """From a first Day, return a Simulation fully extended to date
        `tod`. Assumes the same transactions, same buckets, etc."""
        sim = Simulation([day])
        sim.extend(tod)

        return sim

    def extend(self, tod):
        """
        Extend a simulation, taking advantage of existing simulation
        data.

        Args:
            tod (date): date to extend the simulation to (inclusive)
        """
        oned = datetime.timedelta(days=1)
        maxd = max(self.days.keys())
        lastd = maxd

        while lastd < tod:
            currd = lastd + oned

            if currd not in self.days:
                log.debug("Simulating new Day for %s." % currd)

                newday = Day.next(self.days[lastd])
                self.days[currd] = newday

            lastd = currd
            currd += oned

    @property
    def earliest_dt(self):
        """Return the earliest datetime we have a day for in this
        simulation."""
        return min(self.days.keys())

    @property
    def latest_dt(self):
        """Return the latest datetime we have a day for in this simulation."""
        return max(self.days.keys())

    @property
    def numDays(self):
        """Return the number of days covered by this simulation."""
        return (self.latest_dt - self.earliest_dt).days

    @property
    def surplus(self):
        """Return the difference of income to expenses over a period of
        time."""
        return self.income + self.expenses

    @property
    def income(self):
        """Return a dict keyed by income Transactions and valued by their total
        amount over a period of time."""
        tot = self.totals
        return tot['income']

    @property
    def expenses(self):
        """Return a dict keyed by expense Transactions and valued by their
        total amount over a period of time."""
        tot = self.totals
        return tot['expenses']

    @property
    def totals(self):
        """Return totals for a period. If no period specified, return totals
        based on the latest day simulated."""
        return {k: sum(v.values()) for k, v in self.latestJson.items()}

    @property
    def latestDay(self):
        """Return the latest Day in this simulation."""
        return self.days[max(self.days.keys())]

    @property
    def latestJson(self):
        """Return the JSON for the latest Day in this simulation."""
        return self.latestDay.jsonDict

    @property
    def scalarJson(self):
        """
        Return a dict containing composite totals of various kinds.

        Returns:
            {
              'outflow': total of expenses not towards Saving buckets,
              'interest': total of interest accumulated on Saving buckets,
              'inflow': total income plus total Saving buckets interest,
              'towardsSavings': total of expenses towards Saving buckets,
              'towardsDebt': total of expenses towards Debt buckets,
              'income': total income,
              'livingExpenses': total of expenses not towards any buckets,

              'numDays': number of days this simulation covers,
              'numYears': number of years this simulation covers,
            }
        """
        day = self.latestDay

        outflow = sum([v for k, v in day.expenses.items()
                       if not k.isTowardsSavings])
        livingExpenses = sum([v for k, v in day.expenses.items()
                              if not k.towards])

        income = sum(day.incomes.values())
        interest = sum([b.interestAccrued
                        for b in day.savings.keys()])
        inflow = income + interest

        towardsSavings = sum([v for k, v in day.expenses.items()
                              if k.isTowardsSavings])
        towardsDebt = sum([v for k, v in day.expenses.items()
                           if k.isTowardsDebt])

        return {
            'outflow': outflow,
            'inflow': inflow,
            'towardsSavings': towardsSavings,
            'towardsDebt': towardsDebt,
            'income': income,
            'interest': interest,
            'livingExpenses': livingExpenses,
        }


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
    def first(date, transactions):
        """Given a date and some transactions objects, return the effects of
        the transactions and the associated bucket objects."""
        buckets = Transaction.all_buckets(transactions)

        for b in buckets:
            b.init()

        newday = Day(date, buckets=buckets)

        for t in transactions:
            if isinstance(t, Income):
                newday.incomes[t] = t.simulate(date)
            elif isinstance(t, Expense):
                newday.expenses[t] = t.simulate(date)

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
        for b in self.buckets:
            b.simulate(self.date)

            if isinstance(b, Savings):
                self.savings[b] = b.snapshot(date)['amount']
            elif isinstance(b, Debt):
                self.debts[b] = b.snapshot(date)['amount']

    @property
    def jsonDict(self):
        return {
            'expenses': self.expenses,
            'income': self.incomes,
            'savings': self.savings,
            'debt': self.debts,
        }


