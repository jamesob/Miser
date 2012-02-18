#!/usr/bin/python

from ..miser import dictToSortedList

class Histogram(object):
  """Takes in an `incomeDict` and `expensesDict`, dicts keyed by names and
  paired by amounts gained or spent, respectively over a period of time.
  Produces a bar graph of either.
  """


  def __init__(self, miser, fromdt, todt, numBars = 100):
    """Print a histogram of expenses."""
    def keysToString(indict):
      """Return a new dict that has converted `indict`'s keys from
      Transaction to string."""
      newD = {}
      for k, v in indict.iteritems():
        newD[k.name] = v
      return newD

    self.income = dictToSortedList(keysToString(miser.income(fromdt, todt)))
    self.expenses = dictToSortedList(keysToString(miser.expenses(fromdt, todt)))
    self.numBars = numBars
    
    sumStr = "\nProfile of expenses:"
    sumStr += self.expensesBar

    print sumStr

  def _createTextProfile(self, indict):
    """Create a bar-graph like representation of expenses and income."""

    keys = map(lambda x: x[0], indict)
    vals = map(lambda x: x[1], indict)

    outstrs = ["\n"]
    propDict = {}
    total = sum(vals)
    maxLenKey = max([len(a) for a in keys])
    maxLenVal = max([len(repr(a)) for a in vals]) 

    for k, v in indict:
      outstr = " "
      outstr += k.ljust(maxLenKey + 1)
      outstr += ("%.2f" % v).ljust(maxLenVal + 1)
      outstr += "-" * int(self.numBars * (v / total))
      outstrs.append(outstr)

    return "\n".join(outstrs)

  @property
  def incomeBar(self):
    """Return a string which is a bar-graph style profile of income."""
    return self._createTextProfile(self.income)

  @property
  def expensesBar(self):
    """Return a string which is a bar-graph style profile of expenses."""
    return self._createTextProfile(self.expenses)


