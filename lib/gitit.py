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
      log.printerr('no such ticket')
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
      # TODO: Add a check here to assert validity of the edit
      print 'ticket \'%s\' edited succesfully' % sha7
      self.list()
    else:
      log.printerr('editing of ticket \'%s\' failed' % sha7)

  def mv(self, sha, to_rel):
    match = self.match_or_error(sha)
    src_rel, basename = os.path.split(match)
    sha7 = misc.chop(basename, 7)
    to_rel_abs = os.path.abspath(os.path.join(src_rel, '..', to_rel))
    if not os.path.isdir(to_rel_abs):
      log.printerr('no such release \'%s\'' % to_rel)
      return
    if to_rel_abs == src_rel:
      log.printerr('ticket \'%s\' already in \'%s\'' % (sha7, to_rel))
      return

    try:
      os.rename(match, os.path.join(to_rel_abs, basename))
      print 'ticket \'%s\' moved to release \'%s\'' % (sha7, to_rel)
      self.list()
    except OSError, e:
      log.printerr('could not move ticket \'%s\' to \'%s\':' % (sha7, to_rel))
      log.printerr(e)

  def show(self, sha):
    match = self.match_or_error(sha)
    i = issue.Issue(match)
    print i.__str__()

  def new(self):
    i = issue.create_interactive()

    # Create a new temporary file to edit a new ticket
    itdb = repo.find_itdb()

    # Generate a SHA1 id
    s = sha.new()
    s.update(i.__str__())
    s.update(os.getlogin())
    s.update(datetime.datetime.now().__str__())
    i.id = s.hexdigest()

    # Save the ticket to disk
    i.save()
    _, ticketname = os.path.split(i.filename())
    sha7 = misc.chop(ticketname, 7)
    print 'new ticket \'%s\' saved' % sha7
    return i

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

      total = len(filter(lambda x: x.status != 'rejected', tickets)) * 1.0
      done = len(filter(lambda x: x.status not in ['open', 'rejected'], tickets)) * 1.0
      release_line = colors.colors['red-on-white'] + '%-16s' % releasedir + colors.colors['default']

      # Show a progress bar only when there are items in this release
      if total > 0:
        print release_line + self.progress_bar(done / total)
      else:
        print release_line

      if len(tickets) > 0:
        print colors.colors['blue-on-white'] + 'id      type    title                                                        status   date   assigned-to' + colors.colors['default']
        #TODO: in case of no color support, we should print a line instead
        #print '------- ------- ---------------------------------------------------------------------- -------- ------ --------------------------------'
        for lineno, ticket in enumerate(tickets):
          print ticket.oneline(lineno + 1)
      else:
        print 'no issues'
      print ''

  def rm(self, sha):
    match = self.match_or_error(sha)
    _, basename = os.path.split(match)
    sha7 = misc.chop(basename, 7)
    if os.system('rm "%s"' % match) == 0:
      print 'ticket \'%s\' removed'% sha7
    else:
      log.printerr('error removing ticket \'%s\'' % sha7)
      sys.exit(1)

  def finish_ticket(self, sha, new_status):
    match = self.match_or_error(sha)
    _, basename = os.path.split(match)
    sha7 = misc.chop(basename, 7)
    i = issue.Issue(match)
    if i.status != 'open':
      log.printerr('ticket \'%s\' already %s' % (sha7, i.status))
      sys.exit(1)
    i.status = new_status
    i.save()
    print 'ticket \'%s\' %s' % (sha7, new_status)
    self.list()

  def reopen_ticket(self, sha):
    match = self.match_or_error(sha)
    _, basename = os.path.split(match)
    sha7 = misc.chop(basename, 7)
    i = issue.Issue(match)
    if i.status == 'open':
      log.printerr('ticket \'%s\' already open' % sha7)
      sys.exit(1)
    i.status = 'open'
    i.save()
    print 'ticket \'%s\' reopened' % sha7
    self.list()


