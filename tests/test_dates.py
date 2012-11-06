#!/usr/bin/python

import unittest
import datetime

from miser.scheduling import DailyRecurring, MonthlyRecurring
from miser.utils import to_dt


class DateTests(unittest.TestCase):
    """Test date-specific functionality."""

    def test_daily(self):
        a = DailyRecurring()
        bt = a.rule.between(to_dt(datetime.date(2011, 1, 1)),
                            to_dt(datetime.date(2011, 1, 3)),
                            inc=True)
        self.assertEqual(3, len(bt))

        bt = a.rule.between(to_dt(datetime.date(2011, 1, 1)),
                            to_dt(datetime.date(2011, 1, 1)),
                            inc=True)
        self.assertEqual(1, len(bt))

    def test_monthly(self):
        a = MonthlyRecurring(1)
        date = datetime.date(2012, 11, 1)
        bt = a.rule.between(to_dt(date), to_dt(date), inc=True)

        self.assertEqual(1, len(bt))

