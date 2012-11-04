"""
Buckets represent stateful collections of $$$, like savings or debts.
"""

import abc


class CompoundingPeriods(object):
    """A list of constants indicating how often interest can be compounded."""
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    CONTINUOUSLY = 'continuously'


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
        self._interestAccrued = 0.0
        self._dateLastSeen = None

    def init(self):
        """Reinitialize this Bucket to be as it was on __init__."""
        self.amount = self._principal
        self._interestAccrued = 0.0

    def simulate(self, date):
        """Simulate a day passing. This mostly facilitates compounding of
        interest, etc."""
        if not self.isEffective(date):
            return

    def isEffective(self, date):
        """Return whether or not to consider this bucket yet."""
        return self.begin and (self.begin > date)

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


class Savings(Bucket):

    pass


class Debt(Bucket):

    def __init__(self, *args, **kwargs):
        super(Debt, self).__init__(*args, **kwargs)

        self.amount *= -1.


