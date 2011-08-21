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

    Expense(name = "MATH322 tuition",
            amount = 1.3e3,
            on = Date(2012, 1, 29)),
                            
    Expense(name = "PHYS tuition",
            amount = 1.3e3,
            on = Date(2012, 5, 29)),
                             
    Expense(name = "netflix",
            amount = 7.,
            on = MonthlyRecurring(15)), # 15th day of the month
                              
    Expense(name = "lunch",
            amount = 6.,
            on = WeeklyRecurring(MO, TU, TH)),
                               
    Expense(name = "groceries",
            amount = 25.,
            on = WeeklyRecurring(SA)),
                               
    Expense(name = "rent+utils",
            amount = 700.,
            on = MonthlyRecurring(29)),
                                
    Expense(name = "gas",
            amount = 40.,
            on = MonthlyRecurring(29)),
                                    
    Expense(name = "debt",
            amount = 4e3,
            on = Date(2011, 8, 29)),
                                
    Expense(name = "weekly beer",
            amount = 10.,
            on = WeeklyRecurring(FR)),
                                    
    # Income
    Income(name = "phase2",
           amount = 1.5e3,
           on = MonthlyRecurring(7, 22)),
)

print(m.summary(fromdt=Date(2011, 8, 20), 
                todt=Date(2012, 9, 1)))
