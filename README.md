## Get rich: be Miserly

Miser is a Python library that can be used for writing scripts that'll help you
project costs and figure out how to accumulate money. It is in super-secret
alpha stealth mode, so it's not packaged properly, lacks tests, and is not
extraordinarily user-friendly. Yet.

## Example

Here's a simple usage:

```python
from miser import *

# instantiate a Miser instance
m = Miser("sample")

# set a goal
g = Goal(amount = 16e3, # $16,000
         by = Date(2012, 8, 1)) # by Aug. 1, 2012

m.addGoal(g)

m.addTransactions(

    # Expenses
    Expense(name = "MATH315 tuition",
            amount = 1.3e3,
            on = Date(2011, 8, 29)), # non-recurring
                        
    Expense(name = "netflix",
            amount = 7.,
            on = MonthlyRecurring(15)), # 15th day of the month
                                 
    Expense(name = "weekly beer",
            amount = 10.,
            on = WeeklyRecurring(FR)), # every week on Friday
                                  
    Expense(name = "lunch",
            amount = 6.,
            on = WeeklyRecurring((MO, TU, TH))),
                                   
    Expense(name = "debt",
            amount = 4e3,
            on = Date(2011, 8, 29)),
                                  
    # Income
    Income(name = "job",
           amount = 1.5e3,
           on = MonthlyRecurring((7, 22))),
)

# Print a simulation of the year
print(m.summary(fromdt=Date(2011, 8, 20), 
                todt=Date(2012, 9, 1)))                   
```

which produces


    2011-08-20 00:00:00 to 2012-09-01 00:00:00
    Total saved: 30604.00

    Profile of expenses:

     debt            -4000.0 ----------------------------------------------------------
     MATH315 tuition -1300.0 ------------------
     lunch           -972.0  --------------
     weekly beer     -540.0  -------
     netflix         -84.0   -

