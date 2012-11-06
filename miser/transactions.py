"""
Transaction objects move money around within miser.
"""

from __future__ import print_function

import datetime
import collections
from .utils import to_dt
from dateutil.rrule import rrule, rruleset
from .scheduling import _Recurring


class Transaction(object):
    """A `rule` for recurrence, an `amount` for how much money is involved, and
    a `name` for identification. `Miser` has these."""

    #: multiply any represented amounts by this, e.g. -1. for Expense
    amountMultiplier = 1.

    def __init__(self, name, amount, on, towards=None, tags=None):
        """
        :Parameters:
            - `name`: description of the transaction

            - `amount`: Can be a scalar amount, the result of a generator, or a
                callable.

            - `on`: a `Datetime` or a `_Recurring` subclass.

            - `towards`: A Bucket-type object, e.g. Savings, that this
                transaction directly affects.
        """
        self.name = name
        self.tags = tags
        self.towards = towards
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
        amt = None

        if isinstance(self._amount, collections.Iterator):
            amt = self._amount.next()
        elif callable(self._amount):
            amt = self._amount()
        else:
            amt = self._amount

        return (amt * self.amountMultiplier)

    def _effectForDate(self, date):
        """Calculate the effect of a transaction for a date."""
        hit = self.dateRules.between(to_dt(date), to_dt(date), inc=True)
        return self.amount if hit else 0.

    def simulate(self, date):
        """
        Get the effect for a given datetime.date. Also affect any associated
        linked buckets (found via `self.towards`).

        Returns:
            float. Effect in currency.
        """
        amt = self._effectForDate(date)

        if amt and self.towards:
            # reverse amount: expense -> adding to bucket
            self.towards.inc(-1. * amt)

        return amt


class Expense(Transaction):
    """Outflow of money."""

    amountMultiplier = -1.


class Income(Transaction):
    """Inflow of money."""

    pass

