import os, errno

def chop(s, maxlen = 20, suffix = ''):
  if len(s) > maxlen:
    return s[:maxlen-len(suffix)] + suffix
  else:
    return s

# Shamelessly borrowed from The Python Cookbook
def mkdirs(newdir, mode=0777):
  try:
    os.makedirs(newdir, mode)
  except OSError, err:
    # Reraise the error unless it's about an already existing directory
    if err.errno != errno.EEXIST or not os.path.isdir(newdir):
      raise

def read_file_contents(filename):
  try:
    f = open(filename, 'r')
    return f.read()
  except OSError, e:
    log.printerr('Unable to read file \'%s\'' % filename)
    return None

def write_file_contents(filename, contents):
  try:
    f = open(filename, 'w')
    f.write(contents)
    f.close()
    return True
  except OSError, e:
    log.printerr('Unable to write file \'%s\'' % filename)
    return False

