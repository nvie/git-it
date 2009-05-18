import os
import datetime
import customio

def chop(s, maxlen = 20, suffix = ''):
  if len(s) > maxlen:
    return s[:maxlen-len(suffix)] + suffix
  else:
    return s

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
      ticket = customio.file_as_dict(ticket_file)
      self.title = ticket['Subject']
      self.type = ticket['Type']
      self.issuer = ticket['Issuer']
      # TODO: Implement
      #self.date = ticket['Date']
      self.date = datetime.datetime.now()
      self.body = ''
      self.prio = ticket['Priority']
      self.status = ticket['Status']
      self.assigned_to = ticket['Assigned to']
      _, self.id = os.path.split(ticket_file)

  def oneline(self, lineno = None):
    date = '%s/%s' % (self.date.month, self.date.day)
    return '%-7s %-7s %-30s %-8s %-6s %-16s' % (chop(self.id, 7), chop(self.type, 7), chop(self.title, 30, '..'), chop(self.status, 8), date, chop(self.assigned_to, 16, '..'))

  def __str__(self):
    headers = [ 'Subject: %s'     % self.title,
                'Issuer: %s'      % self.issuer,
                'Date: %s'        % self.date,
                'Type: %s'        % self.type,
                'Priority: %s'    % self.prio,
                'Status: %s'      % self.status,
                'Assigned to: %s' % self.status,
                '',
                self.body
              ]
    return os.linesep.join(headers)

