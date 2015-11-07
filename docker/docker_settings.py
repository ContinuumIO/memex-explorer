"""
Django settings for memex project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from common_settings import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0#t((zq66&3*87djaltu-pn34%0p!*v_332f2p!$2i)w5y17f8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

INSTALLED_APPS += ('debug_toolbar',)

MEDIA_ROOT = os.path.join(BASE_DIR, 'resources')
PROJECT_PATH = os.path.join(MEDIA_ROOT, "projects")
DEPLOYMENT = False

VIRTUAL_HOST = os.environ.get('VIRTUAL_HOST', 'localhost')
PROTOCOL = 'https'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}

# ddt is treated as an external service for now

EXTERNAL_APP_LOCATIONS = {
    'bokeh-server': '/bokeh',
    'ddt': PROTOCOL + '://' + VIRTUAL_HOST + ':8084',
    'tad': '/tad',
    'kibana': '/kibana',
}
