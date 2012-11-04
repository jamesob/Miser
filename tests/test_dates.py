#!/usr/bin/python

import unittest
import datetime

from miser.scheduling import DailyRecurring
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

