import os

# Test
from memex.test_utils.unit_test_utils import UnitTestSkeleton, form_errors, get_object
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

# App
from crawl_space.forms import AddCrawlForm
from crawl_space.models import Crawl
from base.models import Project


def assert_form_errors(response, *errors):
    """Given a response, assert that only the given `errors`
    are present in the form response.
    """
    efe = expected_form_errors = set(errors)
    assert set(form_errors(response).keys()) - efe == set()


class TestViews(UnitTestSkeleton):

    @classmethod
    def setUpClass(cls):
        super(TestViews, cls).setUpClass()
        cls.test_project = Project(
            name = "Test",
            description = "Test Project Description",
            icon = "fa-arrows")
        cls.test_project.save()

        cls.test_crawl = Crawl(
            name = "Test Crawl",
            description = "Test Crawl Description",
            crawler = "ache",
            config = "config_default",
            seeds_list = "ERROR",
            project = cls.test_project)
        cls.test_crawl.save()
        cls.seeds = SimpleUploadedFile('ht.seeds', bytes('This is some content.\n', 'utf-8'))


    @property
    def form_data(self):
        return {'name': 'Cat Crawl',
             'description': 'Find all the cats.',
             'crawler': 'ache'}

    @property
    def slugs(self):
        return dict(slugs=dict(
            slug="test"))

    @property
    def crawl_slugs(self):
        return dict(slugs=dict(
            slug="test",
            crawl_slug="test-crawl"))


    def test_add_crawl_page(self):
        response = self.get('base:crawl_space:add_crawl', **self.slugs)
        assert 'crawl_space/add_crawl.html' in response.template_name


    def test_add_crawl_no_data(self):
        response = self.post('base:crawl_space:add_crawl', **self.slugs)
        assert_form_errors(response, 'name', 'description', 'crawler', 'seeds_list')


    def test_add_crawl_no_name(self):
        response = self.post('base:crawl_space:add_crawl',
            {'description': 'Find all the cats.',
             'crawler': 'ache',
             'seeds_list': self.seeds},
            **self.slugs)
        assert not response.context['form'].errors

    def test_add_crawl_bad_crawler(self):
        response = self.post('base:crawl_space:add_crawl',
            {'name': 'Cat Crawl',
             'description': 'Find all the cats.',
             'crawler': 'fake!'},
            **self.slugs)
        assert_form_errors(response, 'crawler')


    def test_add_crawl_success(self):
        response = self.post('base:crawl_space:add_crawl',
            {'name': 'Cat Crawl',
             'description': 'Find all the cats.',
             'crawler': 'ache'},
            **self.slugs)
        assert 'crawl_space/crawl.html' in response.template_name

        # Crawl name, slug is as expected
        crawl = get_object(response)
        assert (crawl.name, crawl.slug) == ("Cat Crawl", "cat-crawl")

        # Crawl is linked to the right project
        assert crawl.project == self.test_project

    def test_crawl_page(self):
        response = self.get('base:crawl_space:crawl', **self.crawl_slugs)
        assert 'crawl_space/crawl.html' in response.template_name

        crawl = get_object(response)
        assert (crawl.name, crawl.slug) == ("Test Crawl", "test-crawl")

        # Crawl is linked to the right project
        assert crawl.project == self.test_project


# class TestForms(TestCase):
#     pass

    # def test_project_form(self):
    #     form_data = {
    #         'name': 'CATS!',
    #         'description': 'cats cats cats',
    #         'icon': 'fa-arrows'}
    #     form = AddProjectForm(data=form_data)
    #     assert form.is_valid()

