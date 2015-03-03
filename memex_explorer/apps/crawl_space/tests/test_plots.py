from __future__ import unicode_literals

import os
import shutil

# Test
from memex.test_utils.unit_test_utils import UnitTestSkeleton, form_errors, get_object
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

# App
from apps.crawl_space.models import Crawl, CrawlModel
from base.models import Project, alphanumeric_validator

from apps.crawl_space.models import Crawl
from apps.crawl_space.viz.domain import Domain


class TestPlots(UnitTestSkeleton):

    @classmethod
    def setUpClass(cls):
        """Initialize a test project and crawl model,
        and save them to the test database."""

        super(TestViews, cls).setUpClass()

        cls.test_project = Project(
            name = "Test",
            description = "Test Project Description")
        cls.test_project.save()

        cls.test_crawl = Crawl(
            name = "Test Crawl",
            description = "Test Crawl Description",
            crawler = "nutch",
            config = "config_default",
            seeds_list = cls.get_seeds(),
            project = cls.test_project)
        cls.test_crawl.save()

        cls.test_crawlmodel = CrawlModel(
            name = "Test Crawl Model",
            model = cls.get_model_file(),
            features = cls.get_features_file(),
            project = cls.test_project,
        )
        cls.test_crawlmodel.save()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_crawl.get_crawl_path())

    @classmethod
    def get_model_file(self):
        return SimpleUploadedFile('pageclassifier.model', bytes('This is a model file.\n'), 'utf-8')

    @classmethod
    def get_features_file(self):
        return SimpleUploadedFile('pageclassifier.features', bytes('This is a features file.\n'), 'utf-8')

    @classmethod
    def get_seeds(self):
        """Return a new instance of SimpleUploadedFile. This file can only
        be used once."""

        return SimpleUploadedFile('ht.seeds', bytes('This is some content.\n'), 'utf-8')

