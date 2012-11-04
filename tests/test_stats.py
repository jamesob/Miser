#!/usr/bin/python

"""
Integration test for Statistics view.
"""

import james_nyc as j
from miser.views.statistics import Statistics


m = j.makeMiser()
s = Statistics(m)

s.pprint_monthly_percentages()

percs = s.monthly_percentages
assert len(percs) == 2
