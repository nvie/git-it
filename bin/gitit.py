import sys
import issue

class Gitit:
  def __init__(self):
    pass

  def new(self):
    i = issue.Issue()
    i.date = '24/3'
    i.assigned_to = 'Vincent'
    return i
