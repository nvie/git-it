import os

def find_git_repo():
  cwd = os.getcwd()
  while cwd != '/':
    gitrepo = cwd + '/.git'
    if os.path.isdir(gitrepo):
      return gitrepo
    cwd = os.path.abspath(cwd + '/..')
  return None

