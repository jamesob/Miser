"""
Test the top-level behavior of Miser.
"""

import unittest
import datetime

from miser import (Miser,
                   Debt,
                   Savings,
                   Expense,
                   Income,
                   CompoundingPeriods)

from miser.scheduling import (MonthlyRecurring,
                              WeeklyRecurring,
                              Weekdays)


class MiserTest(unittest.TestCase):

    def setUp(self):
        self.m = Miser("tessst")
        self.now_date = datetime.datetime.utcnow().date()
        self.tomorrow_date = self.now_date + datetime.timedelta(days=1)
        self.sim_begin = datetime.date(
            year=2012,
            month=11,
            day=1)

        self.sim_end = datetime.date(
            year=2012,
            month=11,
            day=30)

        self._setUp_miser()

    def _setUp_miser(self):
        """Establish some Miser state to test on."""
        self.cc_debt = Debt(
            "cc",
            begin=self.tomorrow_date,
            rate=0.13,
            amount=100.,
            compounded=CompoundingPeriods.MONTHLY)

        self.savings = Savings(
            "stocks",
            rate=0.07,
            amount=0.,
            compounded=CompoundingPeriods.YEARLY)

        self.m.addTransactions(
            Expense("wing chun",
                    amount=100.,
                    on=MonthlyRecurring(15)),

            Expense("going out",
                    amount=20.,
                    on=WeeklyRecurring(Weekdays.SA, Weekdays.SU)),

            Expense("servicing CC debt",
                    towards=self.cc_debt,
                    amount=20.,
                    on=MonthlyRecurring(1)),

            Expense("retirement",
                    towards=self.savings,
                    amount=100.,
                    on=MonthlyRecurring(15)),

            # Income
            Income("salary",
                   amount=500.,
                   on=MonthlyRecurring(1, 15)),

        )

    def test_totals(self):
        """Test that total amounts are available and correct."""
        expected_total_expenses = (100. + (20. * 2 * 4) + 20. + 100.) * -1.
        expected_total_income = 500. * 2

        sim = self.m.simulate(self.sim_begin, self.sim_end)
        totals_dict = sim.totals

        self.assertTrue('expenses' in totals_dict)
        self.assertTrue('income' in totals_dict)
        self.assertTrue('savings' in totals_dict)
        self.assertTrue('debt' in totals_dict)

        self.assertEqual(expected_total_expenses,
                         totals_dict['expenses'])
        self.assertEqual(expected_total_income,
                         totals_dict['income'])

        self.assertGreater(
            totals_dict['savings'],
            100.)

        self.assertGreaterEqual(
            totals_dict['debt'],
            80.)

    def test_resimulation(self):
        """Ensure that asking for simulations of the same date range don't
        change totals."""
        self.m.simulate(self.sim_begin, self.sim_end)
        self.m.simulate(self.sim_begin, self.sim_end)

        self.test_totals()

