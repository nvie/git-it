import sys, os
import datetime
import sha
import misc, repo, log, issue, colors, git, it

def cmp_date(d1, d2):
  if d1 < d2:
    return -1
  elif d1 > d2:
    return 1
  else:
    return 0


class Gitit:
  def __init__(self):
    pass

  def itdb_exists(self):
    if git.branch_exists(it.ITDB_BRANCH):
      ls = git.full_tree(it.ITDB_BRANCH)
      abs_hold_file = os.path.join(it.TICKET_DIR, it.HOLD_FILE)
      for _, _, _, file in ls:
        if file == abs_hold_file:
          return True
      return False

  def require_itdb(self):
    """
    This method asserts that the itdb is initialized, or errors if not.
    """
    if not self.itdb_exists():
      log.printerr('itdb not yet initialized. run \'it init\' first to ' + \
                   'create a new itdb.')
      sys.exit(1)

  def init(self):
    if self.itdb_exists():
      print 'Already initialized issue database in branch \'%s\'.' % \
                                                             it.ITDB_BRANCH
      return

    # else, initialize the new .it database alongside the .git repo
    gitrepo = repo.find_git_repo()
    if not gitrepo:
      log.printerr('Not a valid Git repository.')
    else:
      parent, _ = os.path.split(gitrepo)
      ticket_dir = os.path.join(parent, it.TICKET_DIR)
      hold_file = os.path.join(ticket_dir, it.HOLD_FILE)
      misc.mkdirs(ticket_dir)
      misc.write_file_contents(hold_file, \
             'This is merely a placeholder file for git-it that prevents ' + \
             'this directory from\nbeing pruned by Git.')

      # Commit the new itdb to the repo
      curr_branch = git.current_branch()
      git.change_head_branch('git-it')
      git.command_lines('add', [hold_file])
      msg = 'Initialized empty ticket database.'
      git.command_lines('commit', ['-m', msg, hold_file])
      os.remove(hold_file)
      os.rmdir(ticket_dir)
      git.change_head_branch(curr_branch)
      abs_ticket_dir = os.path.join(repo.find_root(), it.TICKET_DIR)
      git.command_lines('reset', ['HEAD', abs_ticket_dir])
      misc.rmdirs(abs_ticket_dir)
      print 'Initialized empty ticket database.'

  def match_or_error(self, sha):
    self.require_itdb()
    files = git.full_tree(it.ITDB_BRANCH + ':' + it.TICKET_DIR)
    matches = []
    for _, _, _, path in files:
      _, file = os.path.split(path)
      if file.startswith(sha):
        matches.append(path)

    if len(matches) == 0:
      log.printerr('no such ticket')
      sys.exit(1)
    elif len(matches) > 1:
      log.printerr('ambiguous match critiria. the following tickets match:')
      for match in matches:
        _, id = os.path.split(match)
        log.printerr(id)
      sys.exit(1)
    else:
      return os.path.join(it.TICKET_DIR, matches[0])

  def edit(self, sha):
    i, rel, fullsha, match = self.get_ticket(sha)
    sha7 = misc.chop(fullsha, 7)

    # Save the contents of this ticket to a file, so it can be edited
    i.save(it.EDIT_TMP_FILE)
    timestamp1 = os.path.getmtime(it.EDIT_TMP_FILE)
    success = os.system('vim "%s"' % it.EDIT_TMP_FILE) == 0
    timestamp2 = os.path.getmtime(it.EDIT_TMP_FILE)
    if success:
      if timestamp1 < timestamp2:
        i = issue.create_from_file(it.EDIT_TMP_FILE, fullsha, rel)

        # Now, when the edit has succesfully taken place, switch branches, commit,
        # and switch back
        curr_branch = git.current_branch()
        git.change_head_branch('git-it')
        msg = 'ticket \'%s\' edited' % sha7
        i.save()
        git.command_lines('commit', ['-m', msg, i.filename()])
        git.change_head_branch(curr_branch)
        abs_ticket_dir = os.path.join(repo.find_root(), it.TICKET_DIR)
        git.command_lines('reset', ['HEAD', abs_ticket_dir])
        misc.rmdirs(abs_ticket_dir)
        print 'ticket \'%s\' edited succesfully' % sha7
        print ''
        self.list()
      else:
        print 'editing of ticket \'%s\' cancelled' % sha7
    else:
      log.printerr('editing of ticket \'%s\' failed' % sha7)

    # Remove the temporary file
    os.remove(it.EDIT_TMP_FILE)

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
      print ''
      self.list()
    except OSError, e:
      log.printerr('could not move ticket \'%s\' to \'%s\':' % (sha7, to_rel))
      log.printerr(e)

  def show(self, sha):
    i, _, fullsha, _ = self.get_ticket(sha)
    i.print_ticket(fullsha)

  def new(self):
    self.require_itdb()

    # Create a fresh ticket
    i = issue.create_interactive()

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

    # Commit the new ticket to the 'aaa' branch
    curr_branch = git.current_branch()
    git.change_head_branch('git-it')
    git.command_lines('add', [i.filename()])
    msg = '%s added ticket \'%s\'' % (i.issuer, sha7)
    git.command_lines('commit', ['-m', msg, i.filename()])
    os.remove(i.filename())
    git.command_lines('rm', ['--cached', i.filename()])
    git.change_head_branch(curr_branch)
    abs_ticket_dir = os.path.join(repo.find_root(), it.TICKET_DIR)
    git.command_lines('reset', ['HEAD', abs_ticket_dir])
    misc.rmdirs(abs_ticket_dir)
    return i

  def progress_bar(self, percentage_done, width = 32):
    blocks_done = int(percentage_done * 1.0 * width)
    format_string_done = ('%%-%ds' % blocks_done) % ''
    format_string_togo = ('%%-%ds' % (width - blocks_done)) % ''
    return '[' + colors.colors['green'] + format_string_done + \
           colors.colors['default'] + format_string_togo + '] %d%%' % \
           int(percentage_done * 100)

  def list(self, show_types = ['open']):
    self.require_itdb()
    releasedirs = filter(lambda x: x[1] == 'tree', git.tree(it.ITDB_BRANCH + \
                                                         ':' + it.TICKET_DIR))
    if len(releasedirs) == 0:
      print 'no tickets yet. use \'it new\' to add new tickets.'
      return

    print_count = 0
    for _, _, sha, rel in releasedirs:
      reldir = os.path.join(it.TICKET_DIR, rel)
      ticketfiles = git.tree(it.ITDB_BRANCH + ':' + reldir)
      tickets = [ issue.create_from_lines(git.cat_file(sha), ticket_id, rel) \
                  for _, type, sha, ticket_id in ticketfiles \
                  if type == 'blob' and ticket_id != it.HOLD_FILE \
                ]

      total = len(filter(lambda x: x.status != 'rejected', tickets)) * 1.0
      done = len(filter(lambda x: x.status not in ['open', 'rejected'], \
                                                                tickets)) * 1.0
      release_line = colors.colors['red-on-white'] + '%-16s' % rel + \
                                                       colors.colors['default']

      # Show a progress bar only when there are items in this release
      if total > 0:
        print release_line + self.progress_bar(done / total)
      else:
        print release_line

      # First, filter all types that do not need to be shown out of the list
      tickets_to_print = filter(lambda t: t.status in show_types, tickets)
      if len(tickets_to_print) > 0:
        # Then, sort the tickets by date modified
        tickets_to_print.sort(lambda x, y: cmp_date(x.date, y.date))

        # ...and finally, print them
        print colors.colors['blue-on-white'] + 'id      type    title                                                        status   date   priority' + colors.colors['default']
        #TODO: in case of no color support, we should print a line instead
        #print '------- ------- ---------------------------------------------------------------------- -------- --------- --------'
        for ticket in tickets_to_print:
          print_count += 1
          print ticket.oneline()
      else:
        print 'no open tickets for this milestone'
      print ''

    if print_count == 0:
      print 'use the -a flag to show all tickets'

  def rm(self, sha):
    match = self.match_or_error(sha)
    _, basename = os.path.split(match)
    sha7 = misc.chop(basename, 7)

    # Commit the new itdb to the repo
    curr_branch = git.current_branch()
    git.change_head_branch('git-it')
    msg = 'removed ticket \'%s\'' % sha7
    git.command_lines('commit', ['-m', msg, match])
    git.change_head_branch(curr_branch)
    abs_ticket_dir = os.path.join(repo.find_root(), it.TICKET_DIR)
    git.command_lines('reset', ['HEAD', abs_ticket_dir])
    misc.rmdirs(abs_ticket_dir)
    print 'ticket \'%s\' removed'% sha7

  def get_ticket(self, sha):
    match = self.match_or_error(sha)
    contents = git.cat_file(it.ITDB_BRANCH + ':' + match)
    parent, fullsha = os.path.split(match)
    rel = os.path.basename(parent)
    sha7 = misc.chop(fullsha, 7)
    i = issue.create_from_lines(contents, fullsha, rel)
    return (i, rel, fullsha, match)

  def finish_ticket(self, sha, new_status):
    i, _, fullsha, match = self.get_ticket(sha)
    sha7 = misc.chop(fullsha, 7)
    if i.status != 'open':
      log.printerr('ticket \'%s\' already %s' % (sha7, i.status))
      sys.exit(1)

    # Now, when the edit has succesfully taken place, switch branches, commit,
    # and switch back
    curr_branch = git.current_branch()
    git.change_head_branch('git-it')
    msg = '%s ticket \'%s\'' % (i.status, sha7)
    i.status = new_status
    i.save()
    git.command_lines('commit', ['-m', msg, match])
    git.change_head_branch(curr_branch)
    abs_ticket_dir = os.path.join(repo.find_root(), it.TICKET_DIR)
    git.command_lines('reset', ['HEAD', abs_ticket_dir])
    misc.rmdirs(abs_ticket_dir)
    print 'ticket \'%s\' %s' % (sha7, new_status)
    print ''
    self.list()

  def reopen_ticket(self, sha):
    i, _, fullsha, match = self.get_ticket(sha)
    sha7 = misc.chop(sha, 7)
    if i.status == 'open':
      log.printerr('ticket \'%s\' already open' % sha7)
      sys.exit(1)

    # Now, when the edit has succesfully taken place, switch branches, commit,
    # and switch back
    curr_branch = git.current_branch()
    git.change_head_branch('git-it')
    msg = 'ticket \'%s\' reopened' % sha7
    i.status = 'open'
    i.save()
    git.command_lines('commit', ['-m', msg, match])
    git.change_head_branch(curr_branch)
    abs_ticket_dir = os.path.join(repo.find_root(), it.TICKET_DIR)
    git.command_lines('reset', ['HEAD', abs_ticket_dir])
    misc.rmdirs(abs_ticket_dir)
    print 'ticket \'%s\' reopened' % sha7
    print ''
    self.list()


