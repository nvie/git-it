import datetime

def file_as_dict(filename):
  f = open(filename, 'r')
  dict = {}
  try:
    lines = f.read().split('\n')
    for line in lines:
      pos = line.find(':')
      if pos >= 0:
        key = line[:pos].strip()
        val = line[pos+1:].strip()
        dict[key] = val
  finally:
    f.close()
  return dict

class Issue:
  def __init__(self, ticket_file = None):
    self.title = 'new ticket'
    self.type = 'issue'
    self.issuer = ''
    self.date = datetime.datetime.now()
    self.body = ''
    self.prio = 3
    self.id = '000000'
    self.status = 'open'
    self.assigned_to = 'nobody'

    # Now, read the ticket file if given
    if ticket_file is not None:
      ticket = file_as_dict(ticket_file)
      self.title = ticket['Subject']
      self.type = ticket['Type']
      self.issuer = ticket['Issuer']
      self.date = ticket['Date']
      self.body = ''
      self.prio = ticket['Priority']
      self.id = ticket_file
      self.status = ticket['Status']
      self.assigned_to = ticket['Assigned to']

  def oneline(self, lineno = None):
    curr = '*'
    if lineno:
      id = lineno
    else:
      id = '?'
    return '%s %4s %-30s %-8s %-6s %-16s' % (curr, id, self.title, self.status, self.date, self.assigned_to)

  def __str__(self):
    return self.oneline()
