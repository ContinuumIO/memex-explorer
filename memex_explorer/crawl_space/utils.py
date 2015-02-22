import os
import errno


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def ensure_exists(path):
    try: 
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST: # (path exists)
            pass
        if not os.path.isdir(path):
            raise

def rm_if_exists(filename):
    try:
        os.remove(filename)
        return True
    except OSError as e:
        if e.errno != errno.ENOENT: # (no such file or directory)
            raise
        return False
