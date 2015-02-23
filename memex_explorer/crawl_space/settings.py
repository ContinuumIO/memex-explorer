"""Crawl settings."""

from __future__ import absolute_import

import os
# from django.conf import settings

resources_dir = '/Users/brittainchristopherhard/Documents/memex-explorer/memex_explorer/resources'

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
