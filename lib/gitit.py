import sys, os, dircache
import datetime
import sha
import misc, repo, log, issue, colors

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
      parent, _ = os.path.split(gitrepo)
      itdir = os.path.join(parent, '.it')
      misc.mkdirs(os.path.join(itdir, 'tickets'))
      misc.mkdirs(os.path.join(itdir, 'tmp'))
      print 'Initialized empty issue database in \'.it\''

  def match_or_error(self, sha):
    itdb = repo.find_itdb()
    if not itdb:
      log.printerr('Issue database not yet initialized')
      log.printerr('Run \'it init\' to initialize now')
      return

    ticketdir = os.path.join(itdb, 'tickets')
    releases = dircache.listdir(ticketdir)
    matches = []
    for rel in releases:
      reldir = os.path.join(ticketdir, rel)
      files = dircache.listdir(reldir)
      for file in files:
        if file.startswith(sha):
          matches.append(os.path.join(reldir, file))

    if len(matches) == 0:
      log.printerr('no matching ticket')
      sys.exit(1)
    elif len(matches) > 1:
      log.printerr('ambiguous match critiria. the following tickets match:')
      for match in matches:
        log.printerr('- %s' % match)
      sys.exit(1)
    else:
      return os.path.join(ticketdir, matches[0])

  def edit(self, sha):
    match = self.match_or_error(sha)
    _, basename = os.path.split(match)
    sha7 = misc.chop(basename, 7)
    if os.system('vim "%s"' % match) == 0:
      print 'ticket \'%s\' edited succesfully' % sha7
      self.list()
    else:
      log.printerr('editing of ticket \'%s\' failed' % sha7)

  def show(self, sha):
    match = self.match_or_error(sha)
    i = issue.Issue(match)
    print i.__str__()

  def new(self):
    i = issue.Issue()
    i.issuer = '%s <%s>' % (os.popen('git config user.name').read().strip(), os.popen('git config user.email').read().strip())

    # Create a new temporary file to edit a new ticket
    itdb = repo.find_itdb()
    workfile = os.path.join(itdb, 'tmp', 'new_ticket')
    self.store_ticket(i.__str__(), workfile)

    # Has editing taken place?
    timestamp1 = os.path.getmtime(workfile)
    if os.system('vim "%s"' % workfile) != 0:
      log.printerr('editing failed')
      return
    timestamp2 = os.path.getmtime(workfile)
    if timestamp2 <= timestamp1:
      log.printerr('editing cancelled. no new ticket added.')
      return

    # TODO: Add a check here to see whether all info is filled in correctly!
    i = issue.Issue(workfile)

    s = sha.new()
    s.update(i.__str__())
    s.update(os.getlogin())
    s.update(datetime.datetime.now().__str__())
    filename = os.path.join(itdb, 'tickets', s.hexdigest())
    self.store_ticket(i.__str__(), filename)
    #os.system('git add "%s"' % itdb)
    #os.system('git commit -m "added ticket \'%s\'" "%s"' % (i.title, itdb))
    return i

  def store_ticket(self, ticket_content, filename):
    f = open(filename, 'w')
    try:
      f.write(ticket_content)
    finally:
      f.close

  def progress_bar(self, percentage_done, width = 32):
    blocks_done = int(percentage_done * 1.0 * width)
    format_string_done = ('%%-%ds' % blocks_done) % ''
    format_string_togo = ('%%-%ds' % (width - blocks_done)) % ''
    return '[' + colors.colors['green'] + format_string_done + colors.colors['default'] + format_string_togo + '] %d%%' % int(percentage_done * 100)

  def list(self):
    itdb = repo.find_itdb()
    if not itdb:
      log.printerr('Issue database not yet initialized')
      log.printerr('Run \'it init\' to initialize now')
      return
    ticketdir = os.path.join(itdb, 'tickets')
    releasedirs = dircache.listdir(ticketdir)
    for releasedir in releasedirs:
      fullreleasedir = os.path.join(ticketdir, releasedir)
      ticketfiles = dircache.listdir(fullreleasedir)
      tickets = [ issue.Issue(os.path.join(fullreleasedir, t)) for t in ticketfiles ]
      total = len(tickets) * 1.0
      done = len(filter(lambda x: x.status != 'open', tickets)) * 1.0
      print colors.colors['red-on-white'] + '%-16s' % releasedir + colors.colors['default'] + self.progress_bar(done / total)
      if len(tickets) > 0:
        print colors.colors['blue-on-white'] + 'id      type    title                                                                  status   date   assigned-to' + colors.colors['default']
        #TODO: in case of no color support, we should print a line instead
        #print '------- ------- ---------------------------------------------------------------------- -------- ------ --------------------------------'
        for lineno, ticket in enumerate(tickets):
          print ticket.oneline(lineno + 1)
        print ''
      else:
        print 'no issues'

  def rm(self, sha):
    match = self.match_or_error(sha)
    _, basename = os.path.split(match)
    sha7 = misc.chop(basename, 7)
    if os.system('rm "%s"' % match) == 0:
      print 'ticket \'%s\' removed'% sha7
    else:
      log.printerr('error removing ticket \'%s\'' % sha7)
      sys.exit(1)

