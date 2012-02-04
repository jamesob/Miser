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

  def addGoal(self, g):
    self.goals.append(g)

  def addTransactions(self, *trans):
    for t in trans:
      self.addTransaction(t)

  def addTransaction(self, trans):
    self.transactions.append(trans)

  def _buildTotalsDict(self, fromdt, todt):
    """Return a dictionary that is keyed by Transactions and valued by
    the total amount of the Transaction."""
    pairs = [(t, t.effectForPeriod(fromdt, todt)) for t in self.transactions]
    return dict(pairs)

  def totalSaved(self, fromdt, todt):
    """Return a scalar total of the net amount over a period of time."""
    return sum(self._buildTotalsDict(fromdt, todt).values()) \
        + self.initialBalance

  def goalStatus(self, fromdt, todt):
    """Return a dict keyed by Goals and valued by the difference between the
    total accumulated and the `Goal.amount`."""
    ret = {}
    tot = self.totalSaved(fromdt, todt)

    return dict([(g, tot - g.amount) for g in self.goals])

  def _buildTransDict(self, fromdt, todt, ttype):
    """Internal method used to build dictionaries of transaction simulations
    where the Transaction is of type `ttype`."""
    totalsDict = self._buildTotalsDict(fromdt, todt)
    sortedTotsList = dictToSortedList(totalsDict)

    return dict([(k,v) for k,v in totalsDict.iteritems() if type(k) == ttype])
                     
  def income(self, fromdt, todt):
    """Return a dict keyed by income Transactions and valued by their total
    amount over a period of time."""
    return self._buildTransDict(fromdt, todt, Income)
                                
  def expenses(self, fromdt, todt):
    """Return a dict keyed by expense Transactions and valued by their total
    amount over a period of time."""
    return self._buildTransDict(fromdt, todt, Expense)
                                


class Transaction(object):
  """A `rule` for recurrence, an `amount` for how much money is involved, and
  a `name` for identification. `Miser` has these."""


  def __init__(self, name, amount, on, category=None):
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
      elif recurrenceIs(rrule): # accept `dateutil.rrule`s
        self.dateRules.rrule(dateOrRule)
      elif recurrenceIs(datetime.datetime):
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

