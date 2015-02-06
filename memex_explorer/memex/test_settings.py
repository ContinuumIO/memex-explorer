"""
Test settings for memex project.

"""
import warnings
import builtins


# Use default settings, overriding only those deemed necessary
from .settings import *


# Ignore (particular) warnings
# ============================

# RuntimeWarning:
#   SQLite received a naive datetime (2012-11-02 11:20:15.156506) while time zone support is active.
# http://stackoverflow.com/questions/11708821/django-ipython-sqlite-complains-about-naive-datetime
warnings.filterwarnings("ignore", category=builtins.RuntimeWarning, module='django.db.backends.sqlite3.base', lineno=63)
