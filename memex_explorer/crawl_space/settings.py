"""Crawl settings."""

from __future__ import absolute_import

import sys, os

# from django.conf import settings
sys.path.insert(1, '/'.join(os.path.dirname(__file__).split('/')[:-1]))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "memex.settings")

import django
from django.conf import settings

resources_dir = settings.MEDIA_ROOT

# ACHE language detection files.
# TODO Investigate using conda-installed ACHE resources.
LANG_DETECT_PATH = os.path.join(resources_dir, 'profiles')

CRAWL_PATH = os.path.join(resources_dir, 'crawls')
MODEL_PATH = os.path.join(resources_dir, 'models')
CONFIG_PATH = os.path.join(resources_dir, 'configs')

# Directory to store seed files temporary. See `Crawl.save()` in
#   `crawl_space.models`
SEEDS_TMP_DIR = os.path.join(resources_dir, 'seeds_tmp')
MODELS_TMP_DIR = os.path.join(resources_dir, 'models_tmp')

