#!/usr/bin/python

class GoalPrinter(object):

  def __init__(self, miser, fromdt, todt):
    """Print the total saved and the goals met."""
    self.miser = miser
    print self.summary(fromdt, todt)

  def _goalsMetStr(self, fromdt, todt, totalSaved):
      """Return a string containing information about goals met over a certain
      period of time."""
      retStr = ""
      goals = self.miser.goalStatus(fromdt, todt)

      for g, diff in goals.iteritems():
        if diff > 0:
          retStr += "Goal '%s' met with %.2f to spare!\n" % (g.name, diff)
        else:
          retStr += "Goal '%s' not met by %.2f. Womp.\n" % (g.name, diff)

      return retStr

  def summary(self, fromdt, todt):
      """Print out a summary of various budget information over a period of
      time."""
      totalSaved = self.miser.totalSaved(fromdt, todt)
      sumStr = "%s: %s to %s\n" % (self.miser.name, fromdt, todt)
      sumStr += "Total saved: %.2f" % totalSaved

      sumStr += "\n\nGoals:\n"
      sumStr += self._goalsMetStr(fromdt, todt, totalSaved)

      return sumStr


class RetirementPrinter(object):

    def __init__(self, miser, fromdt, todt):
        self.miser = miser
        self.fromdt = fromdt
        self.todt = todt

        print self._retirementSummary()

    def _retirementSummary(self):
        days = (self.fromdt - self.todt).days
        savings = self.miser.totalSaved(self.fromdt, self.todt)
        expenses = sum(self.miser.expenses(self.fromdt, self.todt).values())

        spy = (savings / days) * 365
        epy = (expenses / days) * 365 * -1

        def years_needed(int_rate):
            return (epy / int_rate) / spy

        sumStr = "Total needed to retire (4% yield): {}\n".format(
            years_needed(0.04))
        sumStr += "Total needed to retire (6% yield): {}\n".format(
            years_needed(0.06))
        sumStr += "Total needed to retire (8% yield): {}\n".format(
            years_needed(0.08))

        return sumStr
