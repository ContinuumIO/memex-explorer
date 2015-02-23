from __future__ import unicode_literals

import os
import shutil
from django.core.urlresolvers import reverse
from django.conf import settings

# # Test
from memex.test_utils.unit_test_utils import UnitTestSkeleton, get_object
from django.core.files.uploadedfile import SimpleUploadedFile

# # App
from crawl_space.models import Crawl
from base.models import Project


class TestViews(UnitTestSkeleton):

    @classmethod
    def setUpClass(cls):
        """Initialize a test project and crawl,
        and save them to the test database."""

        super(TestViews, cls).setUpClass()
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'crawls'))

        cls.test_project = Project(
            name = "Crawl Operation",
            description = "Test Project Description")
        cls.test_project.save()

        cls.test_crawl = Crawl(
            name = "Test Crawl Operation",
            description = "Test Crawl Description",
            crawler = "nutch",
            config = "config_default",
            seeds_list = cls.get_seeds(),
            project = cls.test_project)
        cls.test_crawl.save()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_crawl.get_crawl_path())

    @classmethod
    def get_seeds(self):
        """Return a new instance of SimpleUploadedFile. This file can only
        be used once."""

        # /content/1
        crawl_seed = reverse('base:test_crawl:content',
            kwargs=dict(project_slug=self.test_project.slug, content_id=1))

        return SimpleUploadedFile('ht.seeds', bytes(crawl_seed), 'utf-8')


    @property
    def crawl_slugs(self):
        """Return a dictionary with a "test" project slug and
        a "test-crawl" crawl slug."""

        return dict(slugs=dict(
            project_slug="crawl-operation",
            crawl_slug="test-crawl-operation"))


    def test_nutch_crawl(self):
        """Get the test crawl page, and assert that the
        crawl slug is generated properly and the project
        is linked correctly."""

        response = self.get('base:crawl_space:crawl', **self.crawl_slugs)
        
        assert 'crawl_space/crawl.html' in response.template_name
        crawl = get_object(response)
        assert crawl.project == self.test_project

        response = self.post('base:crawl_space:crawl', data={'action': 'start'},
            **self.crawl_slugs)

        assert "starting" in response.content

        # assert crawl_is_running
        # assert False
