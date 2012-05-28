#!/usr/bin/python

import unittest
import random
import datetime as dt
from nose.tools import eq_
from miser import *
from miser.scheduling import *

class MiserTests(unittest.TestCase):
  """Unit test covering top-level miser behavior."""

  def setUp(self):
    self.m = Miser("test")
    self.fromdt = Date(2011, 1, 1)
    self.todt = Date(2011, 12, 31)

  def test_daily(self):
    t = Expense("lunch",
                amount = 1.,
                on = DailyRecurring(fromdt = self.fromdt,
                                    todt = self.todt))

    self.m.addTransaction(t)
    self.assertEqual(self.m.totalSaved(self.fromdt, self.todt), -365.)

  def test_weekly(self):
    t = Expense("romantic dinner with '90s winona ryder",
                amount = 100.,
                on = WeeklyRecurring(FR,
                                     fromdt = self.fromdt,
                                     todt = self.todt))

    self.m.addTransaction(t)
    self.assertEqual(self.m.totalSaved(self.fromdt, self.todt), 100. * -52.)

  def test_monthly(self):
    t = Expense("rent",
                amount = 1000.,
                on = MonthlyRecurring(1,
                                      fromdt = self.fromdt,
                                      todt = self.todt))

    self.m.addTransaction(t)
    self.assertEqual(self.m.totalSaved(self.fromdt, self.todt), 12 * -1000.)

  def test_overlap(self):
    """Two overlapping recurrence rules shouldn't step on each others' toes."""
    t = Expense("fake lunch",
                amount = 1.,
                on = (WeeklyRecurring(FR,
                                      fromdt = self.fromdt,
                                      todt = self.todt),
                      DailyRecurring(fromdt = self.fromdt,
                                     todt = self.todt)))

    self.m.addTransaction(t)
    self.assertEqual(self.m.totalSaved(self.fromdt, self.todt), -365.)

  def test_generator_amt(self):
    def somuch():
      n = 1
      while True:
        yield n
        n += 1

    fromd = Date(2011, 1, 1)
    tod = Date(2011, 1, 3)

    t = Income("",
               amount = somuch(),
               on = DailyRecurring())

    self.m.addTransaction(t)
    self.assertEqual(self.m.totalSaved(fromd, tod), sum([1, 2, 3]))

  def test_callable_amt(self):
    def getithomie():
      return random.randint(1, 10)

    fromd = Date(2011, 1, 1)
    tod = Date(2011, 1, 3)

    t = Income("callable",
               amount = getithomie,
               on = DailyRecurring())

    self.m.addTransaction(t)
    self.assertTrue(self.m.totalSaved(fromd, tod) <= 10 * 3)


class DateTests(unittest.TestCase):
  """Test date-specific functionality."""

  def test_daily(self):
    a = DailyRecurring()
    bt = a.rule.between(Date(2011, 1, 1), Date(2011, 1, 3), inc=True)
    self.assertEqual(3, len(bt))

    bt = a.rule.between(Date(2011, 1, 1), Date(2011, 1, 1), inc=True)
    self.assertEqual(1, len(bt))


def test_daily_amounts():
    """Test to see that all transactions are distributed over days."""
    weekly_amt = 70.
    m = Miser("test")
    week = a_week()

    m.addTransaction(
        Expense("some weekly expense",
                amount=weekly_amt,
                on=WeeklyRecurring(FR)))

    for day in week:
        print m[day].expenses
        # eq_(m[day].total_expenses, weekly_amt / 7)

    assert False


def a_week():
    """
    Return a week of dates, starting from today.

    Returns:
        A list of datetime.dates.
    """
    week = []
    one_day = dt.timedelta(days=1)
    today = dt.date.today()

    for i in range(7):
        week.append(today)
        today += one_day

    return week

if __name__ == '__main__':
  unittest.main()
