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

def file_as_dict(filename):
  """
  Read a file as a series of lines representing dictionary entries in the
  format of "key: value" (that is: key, colon, value)
  """
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

