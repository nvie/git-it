import sys

class Issue:
  def __init__(self):
    self.title = ''
    self.type = 'issue'
    self.author = ''
    self.date = ''
    self.body = ''
    self.prio = 3
    self.id = 1
    self.status = 'open'

  def oneline(self):
    curr = '*'
    return '%-2s %6s %25s %6s %6s %16s' % (curr, self.id, self.title, self.status, self.date, self.assigned_to)

  def __str__(self):
    return self.oneline()
