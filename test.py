#!/usr/bin/python

import unittest
from miser import *

class Tests(unittest.TestCase):

    def setUp(self):
        self.m = Miser("test")
        self.fromdt = Date(2011, 1, 1)
        self.todt = Date(2011, 12, 31)

    def test_daily(self):
        t = Expense(name = "lunch",
                    amount = 1.,
                    on = DailyRecurring(fromdt = self.fromdt,
                                        todt = self.todt))

        self.m.addTransaction(t)
        self.assertEqual(self.m._totalForPeriod(self.fromdt, self.todt), 
                         -365.)

    def test_weekly(self):
        t = Expense(name = "romantic dinner with '90s winona ryder",
                    amount = 100.,
                    on = WeeklyRecurring(FR, # friiiday, it's friiiday
                                         fromdt = self.fromdt,
                                         todt = self.todt))

        self.m.addTransaction(t)
        self.assertEqual(self.m._totalForPeriod(self.fromdt, self.todt), 
                         100. * -52.)

    def test_monthly(self):
        t = Expense(name = "rent",
                    amount = 1000.,
                    on = MonthlyRecurring(1,
                                          fromdt = self.fromdt,
                                          todt = self.todt))

        self.m.addTransaction(t)
        self.assertEqual(self.m._totalForPeriod(self.fromdt, self.todt), 
                         12 * -1000.)
                                     
    def test_overlap(self):
        """Two overlapping recurrence rules shouldn't step on each others'
        toes."""
        t = Expense(name = "fake lunch",
                    amount = 1.,
                    on = (WeeklyRecurring(FR,
                                          fromdt = self.fromdt,
                                          todt = self.todt),
                          DailyRecurring(fromdt = self.fromdt, 
                                         todt = self.todt)))

        self.m.addTransaction(t)
        self.assertEqual(self.m._totalForPeriod(self.fromdt, self.todt), 
                         -365.)
                                     
if __name__ == '__main__':
    unittest.main()
