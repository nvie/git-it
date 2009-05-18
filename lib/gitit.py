import sys, os, dircache
import datetime
import customio, repo, log

class Gitit:
  def __init__(self):
    pass

  def init(self):
    db = repo.find_itdb()
    if db:
      print 'Already initialized issue database in \'.it\''
      return

    # else, initialize the new .it database alongside the .git repo
    gitrepo = repo.find_git_repo()
    if not gitrepo:
      log.printerr('Not a valid Git repository.')
    else:
      customio.mkdirs(os.path.abspath(gitrepo + '/..') + '/.it/tickets')
      print 'Initialized empty issue database in \'.it\''

  def new(self):
    i = issue.Issue()
    i.date = datetime.datetime.now()
    i.assigned_to = 'Vincent'
    return i

  def list(self):
    ticketdir = 'design/tickets'
    list = dircache.listdir(ticketdir)
    return [ issue.Issue(ticketdir + '/' + x) for x in list ]

