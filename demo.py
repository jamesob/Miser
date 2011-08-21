from miser import *

m = Miser("jobeirne")

g = Goal(amount = 16e3, # $16,000
         by = Date(2012, 8, 1)) # by Aug. 1, 2012

m.addGoal(g)

m.addTransactions(

    # Expenses
    Expense(name = "MATH315 tuition",
            amount = 1.3e3,
            on = Date(2011, 8, 29)),

    Expense(name = "netflix",
            amount = 14.,
            on = MonthlyRecurring(15)), # 15th day of the month

    # Income
    Income(name = "phase2",
           amount = 1.5e3,
           on = MonthlyRecurring(7, 22)),
)

print(m.summary(fromdt=Date(2011, 8, 20), 
                todt=Date(2012, 8, 24)))
