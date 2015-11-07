"""
Common Django settings for memex explorer project (both dev and deploy)

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import logging
import os
import sys

from django.conf import global_settings

from local_settings import *
from supervisor_services import check_process_state

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VIRTUAL_HOST = os.environ.get('VIRTUAL_HOST', 'localhost')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0#t((zq66&3*87djaltu-pn34%0p!*v_332f2p!$2i)w5y17f8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'base',
    'task_manager',
    'rest_framework',
)

EXPLORER_APPS = (
    'crawl_space',
)

INSTALLED_APPS += tuple("apps.%s" % app for app in EXPLORER_APPS)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    "base.views.project_context_processor",
)

ROOT_URLCONF = 'memex.urls'

WSGI_APPLICATION = 'memex.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'base/static')

STATIC_URL = '/static/'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

MEDIA_URL = '/resources/'

CRISPY_TEMPLATE_PACK = 'bootstrap3'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'resources/logs/django-app.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Celery Config
BROKER_URL = 'redis://localhost'
CELERY_RESULT_BACKEND = 'redis://localhost'

CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT=['pickle']
CELERY_TRACK_STARTED = True

#These must be specified
MEDIA_ROOT = None
PROJECT_PATH = None
EXTERNAL_APP_LOCATIONS = {}

# Update this set if you add an external application
EXTERNAL_APPS = {'celery',
                 'ddt',
                 'elasticsearch',
                 'kibana',
                 'rabbitmq',
                 'bokeh-server',
                 'redis',
                 'tad',
                 'tika'}

sys.stderr.write("[%d]: Querying supervisor for state of external applications\n" % (os.getpid()))
READY_EXTERNAL_APPS = {app for app in EXTERNAL_APPS if check_process_state(app)}
if READY_EXTERNAL_APPS:
    sys.stderr.write("[%d]: The following applications are ready %s\n" % (os.getpid(), str(READY_EXTERNAL_APPS)))
else:
    sys.stderr.write("[%d]: Supervisord not running or no applications are running\n" % (os.getpid()))

ENABLE_STREAM_VIZ = 'bokeh-server' in READY_EXTERNAL_APPS and 'rabbitmq' in READY_EXTERNAL_APPS

sys.stderr.write("Setting enable stream viz to: {}".format(ENABLE_STREAM_VIZ))

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}
