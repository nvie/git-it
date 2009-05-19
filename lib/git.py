#
# Python Git library
#
import os

def current_branch():
  return filter(lambda x: x[1], branch_all())[0][0]

def branch_all():
  branches = command_lines('branch', ['-a'])
  arr = []
  for b in branches:
    current = b[0:2] == '* '
    arr.append((b[2:], current))
  return arr

def full_tree(branch):
  raws = command_lines('ls-tree', ['-r', branch])
  objs = []
  for line in raws:
    meta, file = line.split('\t', 1)
    mode, type, sha = meta.split(' ', 2)
    objs.append((mode, type, sha, file))
  return objs

def command_lines(subcmd, opts = []):
  output = os.popen('git %s %s' % (subcmd, ' '.join(opts))).read()
  if output.endswith(os.linesep):
    output = output[:-len(os.linesep)]
  return output.split(os.linesep)

if __name__ == '__main__':
  print full_tree(current_branch())
