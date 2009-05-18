import os
import datetime
import colors
import misc

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
      ticket = misc.file_as_dict(ticket_file)
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
    status_colors = { 'open' : 'bold', 'closed' : 'default', 'rejected' : 'red-on-white', 'fixed' : 'green-on-white' }
    date = '%s/%s' % (self.date.month, self.date.day)
    subject = '%s%-35s%s' % (colors.colors[status_colors[self.status]], misc.chop(self.title, 30, '..'), colors.colors['default'])
    status = '%s%-8s%s' % (colors.colors[status_colors[self.status]], misc.chop(self.status, 8), colors.colors['default'])
    return '%-7s %-7s %s %s %-6s %-16s' % \
           (misc.chop(self.id, 7),
            misc.chop(self.type, 7), subject, status,
            date, misc.chop(self.assigned_to, 16, '..'))

  def __str__(self):
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
    return os.linesep.join(headers)

