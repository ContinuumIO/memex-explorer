"""
WSGI config for memex project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys
import subprocess


sys.path.insert(1, '/'.join(os.path.abspath(__file__).split('/')[:-2]))

# Start Solr
subprocess.call(os.path.join(sys.path[1], "runsolr"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "memex.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

