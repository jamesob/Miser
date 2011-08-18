from miser import *
import datetime as dt

m = Miser("jobeirne")

g = Goal(amount=16e3, # $16,000
         by=dt.date(2012, 8, 1)) # by Aug. 1, 2012

m.attachGoal(g)

bills = [Bill(name = "MATH315 tuition",
              amount = 1.3e3,
              on = dt.date(2011, 8, 29)),

         Bill(name = "netflix",
              amount = 14.,
              on = MonthlyRecurring(15))] # 15th day of the month

income = [Income(name = "phase2",
                 amount = 1.5e3,
                 on = [MonthlyRecurring(7),
                       MonthlyRecurring(22)])]

m.attachBills(bills)
m.attachIncome(income)

