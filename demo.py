from miser import *
from miser.scheduling import *
from miser.views import *
import random

m = Miser("test", 
          initialBalance = 3e3)

g = Goal(name = "bankity bank bank",
         amount = 20e3, # $16,000
         by = Date(2012, 9, 1)) # by Aug. 1, 2012

m.addGoal(g)

m.addTransactions(
    # Expenses
    Expense(name = "MATH322 tuition",
            amount = 1.3e3,
            on = Date(2012, 5, 29)),
                           
    Expense(name = "netflix",
            amount = 7.,
            on = MonthlyRecurring(15)), # 15th day of the month
                            
    Expense(name = "lunch",
            amount = 6.,
            on = DailyRecurring()),
                             
    Expense(name = "dinner",
            amount = 5.,
            on = WeeklyRecurring((SA, SU, TU, WE, FR))),
                              
    Expense(name = "breakfast",
            amount = 3.,
            on = DailyRecurring()),
                              
    Expense(name = "rent+utils",
            amount = 800.,
            on = MonthlyRecurring(29)),
                                 
    # Income
    Income(name = "job",
           amount = 2e3,
           on = MonthlyRecurring((7, 22))),
)

def unforeseen():
  """Return a random value in some range to simulate unforeseen expenses."""
  return random.gauss(300., 100.)

m.addTransaction(
    Expense(name = "unforeseen",
            amount = unforeseen,
            on = MonthlyRecurring(1))
)

def investment(principal, interest):
  """A generator that simulates an investment and interest on it, compounded
  monthly."""
  while True:
    principal *= (1 + interest)
    yield principal

m.addTransaction(
    Income(name = "Investment",
           amount = investment(1000, 0.07),
           on = MonthlyRecurring(1))
)

def summary(fromdt, todt):
  args = (m, fromdt, todt)
  GoalPrinter(*args)
  Histogram(*args)

if __name__ == '__main__':
  summary(Date(2012, 2, 1), Date(2012, 8, 15))


