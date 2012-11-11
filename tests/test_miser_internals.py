#!/usr/bin/python

import unittest
import random
import datetime

from miser import Miser, Expense, Income
from miser.scheduling import (DailyRecurring,
                              WeeklyRecurring,
                              MonthlyRecurring,
                              Weekdays)


class MiserTests(unittest.TestCase):
    """Unit test covering top-level miser behavior."""

    def setUp(self):
        self.m = Miser("test")
        self.fromd = datetime.date(2011, 1, 1)
        self.tod = datetime.date(2011, 12, 31)

    def test_daily(self):
        t = Expense("lunch",
                    amount=1.,
                    on=DailyRecurring(begin=self.fromd,
                                      end=self.tod))

        self.m.addTransaction(t)
        sim = self.m.simulate(self.fromd, self.tod)

        self.assertEqual(sim.surplus, -365.)

    def test_weekly(self):
        t = Expense("dindin",
                    amount=100.,
                    on=WeeklyRecurring(Weekdays.FR,
                                       begin=self.fromd,
                                       end=self.tod))

        self.m.addTransaction(t)
        sim = self.m.simulate(self.fromd, self.tod)

        self.assertEqual(sim.surplus, 100. * -52.)

    def test_monthly(self):
        t = Expense("rent",
                    amount=1000.,
                    on=MonthlyRecurring(1,
                                        begin=self.fromd,
                                        end=self.tod))

        self.m.addTransaction(t)
        sim = self.m.simulate(self.fromd, self.tod)

        self.assertEqual(sim.surplus, 12 * -1000.)

    def test_overlap(self):
        """Two overlapping recurrence rules shouldn't step on each others'
        toes."""
        t = Expense("fake lunch",
                    amount=1.,
                    on=(WeeklyRecurring(Weekdays.FR,
                                        begin=self.fromd,
                                        end=self.tod),
                        DailyRecurring(begin=self.fromd,
                                       end=self.tod)))

        self.m.addTransaction(t)
        sim = self.m.simulate(self.fromd, self.tod)

        self.assertEqual(sim.surplus, -365.)

    def test_generator_amt(self):
        def somuch():
            n = 1
            while True:
                yield n
                n += 1

        fromd = datetime.date(2011, 1, 1)
        tod = datetime.date(2011, 1, 3)

        t = Income("",
                   amount=somuch(),
                   on=DailyRecurring())

        self.m.addTransaction(t)
        sim = self.m.simulate(fromd, tod)

        self.assertEqual(sim.surplus, sum([1, 2, 3]))

    def test_callable_amt(self):
        def monay():
            return random.randint(1, 10)

        fromd = datetime.date(2011, 1, 1)
        tod = datetime.date(2011, 1, 3)

        t = Income("callable",
                   amount=monay,
                   on=DailyRecurring())

        self.m.addTransaction(t)
        sim = self.m.simulate(fromd, tod)

        self.assertTrue(sim.surplus <= 10 * 3)

