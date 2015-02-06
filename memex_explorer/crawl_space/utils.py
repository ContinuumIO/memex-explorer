import os
import errno

def join(*args):
    return os.path.join(*args)

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def rm_if_exists(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT: # (no such file or directory)
            raise