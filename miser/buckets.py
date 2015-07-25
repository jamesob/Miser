"""
Buckets represent stateful collections of $$$, like savings or debts.
"""

import abc
import math

import logging
log = logging.getLogger(__name__)


__all__ = ['Savings', 'Debt', 'CompoundingPeriods']


class CompoundingStrategy(object):
    """Represents a strategy for compounding interest based on a certain
    periodicity."""

    __meta__ = abc.ABCMeta

    def __init__(self, rate):
        self.rate = rate

    @abc.abstractmethod
    def interestForDay(self, amount):
        pass

    @staticmethod
    def strategy(const):
        """Return a CompoundingStrategy given a constant."""
        strategies = CompoundingStrategy.__subclasses__()

        for strategy in strategies:
            if strategy.const == const:
                return strategy

        log.warning("No strategy found for const '%s'." % const)

        return strategy


class Monthly(CompoundingStrategy):

    const = 'monthly'

    def interestForDay(self, amount):
        """This is kind of a hack; only provides approximate interest values
        since we're using an average days-per-month count."""
        daily_rate = ((1 + self.rate) ** (1. / 30)) - 1

        return (amount * daily_rate)


class Yearly(CompoundingStrategy):

    const = 'yearly'

    def interestForDay(self, amount):
        yearly = ((1 + self.rate) ** (1. / 365)) - 1
        return (amount * yearly)


class Daily(CompoundingStrategy):

    const = 'daily'

    def interestForDay(self, amount):
        return (amount * self.rate)


class Continuously(CompoundingStrategy):

    const = 'continuously'

    def interestForDay(self, amount):
        return (amount * (math.e ** (self.rate * (1 / 365.)))) - amount


class CompoundingPeriods(object):
    """A list of constants indicating how often interest can be compounded."""
    MONTHLY = Monthly.const
    YEARLY = Yearly.const
    CONTINUOUSLY = Continuously.const
    DAILY = Daily.const


class Bucket(object):
    """Stateful collection of money, optionally subject to interest."""

    __meta__ = abc.ABCMeta

    def __init__(self,
                 name,
                 amount,
                 rate=0.00,
                 compounded=None,
                 begin=None):
        """
        :Parameters:
            - name: description of the bucket
            - amount: initial magnitude of money the bucket represents
            - rate (float): interest rate, defaults to 0.00
            - compounded (CompoundingPeriods): periodicity of interest
                compounding. defaults to None
            - begin (date): when this Bucket should be introduced. defaults to
                None
        """
        self.name = name
        self.amount = amount
        self.rate = rate
        self.compounded = compounded
        self.begin = begin

        self._principal = self.amount
        self.interestAccrued = 0.0
        self._dateLastSeen = None

        self._compounding = CompoundingStrategy.strategy(compounded)(rate)

    def init(self):
        """Reinitialize this Bucket to be as it was on __init__."""
        self.amount = self._principal
        self.interestAccrued = 0.0

    def simulate(self, date):
        """Simulate a day passing. This mostly facilitates compounding of
        interest, etc."""
        if not self.isEffective(date):
            log.debug(
                "Bucket %s isn't effective yet; skipping simulation." %
                self
            )
            return

        interest = self._compounding.interestForDay(self.amount)

        self.interestAccrued += interest
        self.amount += interest

        log.debug("Added interest (%s) to bucket %s."
                  % (interest, self))

    def isEffective(self, date):
        """Return whether or not to consider this bucket yet."""
        return (not self.begin) or (self.begin <= date)

    def inc(self, amount):
        """
        Increase the amount in this bucket.

        NB: This may be increasing Debt, which means adding a negative amount.
        """
        self.amount += amount

    def snapshot(self, date):
        """Return the current state of this bucket (dict)."""
        return {
            'amount': self.amount if self.isEffective(date) else 0.,
        }

    def __repr__(self):
        return ("%s(%s, %s, rate=%s, compounded=%s, begin=%s)"
                % (self.__class__.__name__,
                   self.name,
                   self.amount,
                   self.rate,
                   self.compounded,
                   self.begin))

    __str__ = __repr__
    __unicode__ = __repr__


class Savings(Bucket):

    pass


class Debt(Bucket):

    def __init__(self, *args, **kwargs):
        super(Debt, self).__init__(*args, **kwargs)

        self.amount *= -1.
