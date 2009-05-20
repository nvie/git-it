import os, errno, dircache
import log

def chop(s, maxlen = 20, suffix = ''):
  if len(s) > maxlen:
    return s[:maxlen-len(suffix)] + suffix
  else:
    return s

def mkdirs(newdir):
  return os.system('mkdir -p "%s"' % newdir) == 0

def rmdirs(dir):
  if not os.path.exists(dir):
    return True

  if not os.path.isdir(dir):
    log.printerr('\'%s\': not a directory' % dir)
    return False

  # First, remove all children of dir
  ls = dircache.listdir(dir)
  ok = True
  for file in ls:
    full = os.path.join(dir, file)
    if os.path.isdir(full):
      if not rmdirs(full):
        ok = False
    else:
      try:
        os.remove(full)
      except OSError, e:
        log.printerr('could not remove file \'%s\'' % full)
        ok = False

  # Finally, remove the empty dir itself
  if ok:
    try:
      os.rmdir(dir)
    except OSError, e:
      log.printerr('could not remove directory \'%s\'' % dir)
      ok = False
  return ok

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

