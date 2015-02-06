# Test
from memex.test_utils.unit_test_utils import UnitTestSkeleton, form_errors
from django.test import TestCase
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile

# App
from base.forms import AddProjectForm
from base.models import Project
from test_crawl import assert_form_errors


class TestAddDataModelView(UnitTestSkeleton):

    @classmethod
    def setUpClass(cls):
        super(TestAddDataModelView, cls).setUpClass()
        cls.test_project = Project(
            name = "Model Test",
            description = "Test Project Description",
            icon = "fa-arrows")
        cls.test_project.save()

    @property
    def slugs(self):
        return dict(slugs=dict(
            slug="model-test"))

    def get_model_file(self):
        return SimpleUploadedFile('pageclassifier.model', bytes('This is a model file.\n', 'utf-8'))

    def get_features_file(self):
        return SimpleUploadedFile('pageclassifier.features', bytes('This is a features file.\n', 'utf-8'))

    def test_add_model_page(self):
        response = self.get('base:crawl_space:add_crawl_model', **self.slugs)
        assert 'crawl_space/add_crawl_model.html' in response.template_name

    def test_add_model_no_data(self):
        response = self.post('base:crawl_space:add_crawl_model', **self.slugs)
        assert_form_errors(response, 'name', 'model', 'features')

    def test_add_model_no_name(self):
         response = self.post('base:crawl_space:add_crawl_model',
            {
                'model': self.get_model_file(),
                'features': self.get_features_file(),
            },
            **self.slugs)
         assert_form_errors(response, 'name')

    def test_add_model_no_model(self):
        response = self.post('base:crawl_space:add_crawl_model',
           {
               'name': 'Test Model',
               'features': self.get_features_file(),
           },
           **self.slugs)
        assert_form_errors(response, 'model')

    def test_add_model_no_features(self):
        response = self.post('base:crawl_space:add_crawl_model',
            {
                'name': 'Test Model',
                'model': self.get_model_file(),
            },
            **self.slugs)
        assert_form_errors(response, 'features')

    def test_add_model_success(self):
        response = self.post('base:crawl_space:add_crawl_model',
            {
                'name': 'Test Model',
                'model': self.get_model_file(),
                'features': self.get_features_file(),
            },
            **self.slugs)

