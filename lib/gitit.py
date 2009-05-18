import sys
import issue
import dircache
import issue

class Gitit:
  def __init__(self):
    pass

  def new(self):
    i = issue.Issue()
    i.date = '24/3'
    i.assigned_to = 'Vincent'
    return i

  def list(self):
    ticketdir = 'design/tickets'
    list = dircache.listdir(ticketdir)
    return [ issue.Issue(ticketdir + '/' + x) for x in list ]
