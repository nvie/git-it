import os
import datetime
import colors
import misc
import repo

def not_empty(s):
  return s.strip() != ''

def ask_for_pattern(message, pattern = None):
  input = raw_input(message)
  if pattern:
    while not pattern(input):
      input = raw_input(message)
  return input

def create_interactive():
  # First, do some checks to error early
  fullname = os.popen('git config user.name').read().strip()
  email = os.popen('git config user.email').read().strip()
  if not fullname:
    log.printerr('author name not set. use "git config [--global] user.name \'John Smith\'" to set the fullname')
    return
  if not fullname:
    log.printerr('author name not set. use "git config [--global] user.name \'John Smith\'" to set the fullname')
    return

  i = Issue()
  i.title = ask_for_pattern('Title: ', not_empty)

  type_dict = { 'i': 'issue', 't': 'task', 'f': 'feature', 'b': 'bug' }
  type_string = ask_for_pattern('Type [(b)ug, (f)eature, (i)ssue, (t)ask]: ', lambda x: not_empty(x) and x.strip() in 'bfit')
  i.type = type_dict[type_string]

  prio_string = ask_for_pattern('Priority [(1)high, (2)medium, (3)low]: ', lambda x: x.strip() in '123')
  if prio_string == '':
    i.prio = 2
  else:
    i.prio = int(prio_string)
  i.release = ask_for_pattern('Release: ').strip()
  if i.release == '':
    i.release = 'uncategorized'
  #i.body = ask_for_multiline_pattern('Describe the ticket:\n')
  i.status = 'open'
  i.date = datetime.datetime.now()
  i.issuer = '%s <%s>' % (fullname, email)
  return i

def file_as_dict(filename):
  """
  Read a file as a series of lines representing dictionary entries in the
  format of "key: value" (that is: key, colon, value)
  """

class Issue:
  # How each status is visually printed
  status_colors = { 'open': 'bold', \
                    'closed': 'default', \
	'rejected': 'red-on-white', \
	'fixed': 'green-on-white' }

  def __init__(self, ticket_file = None):
    self.title = ''
    self.type = 'issue'
    self.issuer = ''
    self.date = datetime.datetime.now()
    self.body = ''
    self.prio = 3
    self.id = '000000'
    self.status = 'open'
    self.assigned_to = '-'
    self.release = 'uncategorized'

    # Now, read the ticket file if given
    if ticket_file is not None:
      f = open(ticket_file, 'r')
      ticket = {}
      ticket[None] = ''
      try:
        lines = f.read().split('\n')
        for line in lines:
          if line.strip() == '' or line[0] == '#':
            continue
          pos = line.find(':')
          if pos >= 0:
            key = line[:pos].strip()
            val = line[pos+1:].strip()
            ticket[key] = val
          else:
            ticket[None] += line + os.linesep
      finally:
        f.close()

      self.title = ticket['Subject']
      self.type = ticket['Type']
      self.issuer = ticket['Issuer']
      # TODO: Implement
      #self.date = ticket['Date']
      self.date = datetime.datetime.now()
      self.body = ticket[None]
      self.prio = ticket['Priority']
      self.status = ticket['Status']
      self.assigned_to = ticket['Assigned to']
      dir, self.id = os.path.split(ticket_file)
      _, self.release = os.path.split(dir)

  def oneline(self, lineno = None):
    date = '%s/%s' % (self.date.month, self.date.day)
    subject = '%s%-60s%s' % (colors.colors[self.status_colors[self.status]], misc.chop(self.title, 60, '..'), colors.colors['default'])
    status = '%s%-8s%s' % (colors.colors[self.status_colors[self.status]], misc.chop(self.status, 8), colors.colors['default'])
    return '%-7s %-7s %s %s %-6s %-32s' % \
           (misc.chop(self.id, 7),
            misc.chop(self.type, 7), subject, status,
            date, misc.chop(self.assigned_to, 32, '..'),
           )

  def __str__(self):
    headers = [ 'Subject: %s'     % self.title,
                'Issuer: %s'      % self.issuer,
                'Date: %s'        % self.date,
                'Type: %s'        % self.type,
                'Priority: %s'    % self.prio,
                'Status: %s'      % self.status,
                'Assigned to: %s' % self.assigned_to,
                'Release: %s'     % self.release,
                '',
                self.body
              ]
    return os.linesep.join(headers)

  def print_ticket_field(self, field, value, color_field = None, color_value = None):
    if not color_field:
      color_field = 'red-on-white'
    if not color_value:
      color_value = 'default'
    print '%s%s:%s %s%s%s' % (colors.colors[color_field], field, colors.colors['default'], \
                              colors.colors[color_value], value, colors.colors['default'])

  def print_ticket(self):
    self.print_ticket_field('Subject', self.title)
    self.print_ticket_field('Issuer', self.issuer)
    self.print_ticket_field('Date', self.date)
    self.print_ticket_field('Type', self.type)
    self.print_ticket_field('Priority', self.prio)
    self.print_ticket_field('Status', self.status, None, self.status_colors[self.status])
    self.print_ticket_field('Assigned to', self.assigned_to)
    self.print_ticket_field('Release', self.release)
    print ''
    print self.body

  def filename(self):
    itdb = repo.find_itdb()
    if not itdb:
      log.printerr('Issue database not yet initialized')
      log.printerr('Run \'it init\' to initialize now')
      return
    file = os.path.join(itdb, 'tickets', self.release, self.id)
    return file

  def save(self, file = None):
    headers = [ 'Subject: %s'     % self.title,
                'Issuer: %s'      % self.issuer,
                'Date: %s'        % self.date,
                'Type: %s'        % self.type,
                'Priority: %s'    % self.prio,
                'Status: %s'      % self.status,
                'Assigned to: %s' % self.assigned_to,
                '',
                self.body
              ]
    contents = os.linesep.join(headers)

    # If an explicit file name is not given, calculate the default
    if file is None:
      file = self.filename()

    # Write the file
    dir, _ = os.path.split(file)
    if not os.path.isdir(dir):
      misc.mkdirs(dir)
    f = open(file, 'w')
    try:
      f.write(contents)
    finally:
      f.close

