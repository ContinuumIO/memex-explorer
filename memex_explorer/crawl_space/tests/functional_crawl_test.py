from __future__ import unicode_literals
from os.path import exists, join
import shutil
import pytest
import tempfile

from django.conf import settings
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import Select

from base.models import Project
from apps.crawl_space.models import CrawlModel

TEST_RESOURCES_DIR = settings.MEDIA_ROOT
TEST_MODEL_PATH = join(TEST_RESOURCES_DIR,
    "test_model/pageclassifier.model")
TEST_FEATURES_PATH = join(TEST_RESOURCES_DIR,
    "test_model/pageclassifier.features")




@pytest.mark.slow
class TestCrawls(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.browser = WebDriver()
        cls.browser.implicitly_wait(1)
        super(TestCrawls, cls).setUpClass()


    def setUp(self):
        self.project = Project.objects.create(
            name="Potatoes",
            description="Why are they?")
        self.project.save()
        super(TestCrawls, self).setUp()


    def tearDown(self):
        shutil.rmtree(join(TEST_RESOURCES_DIR, 'crawls'),
                      ignore_errors=True)
        shutil.rmtree(join(TEST_RESOURCES_DIR, 'models'),
                      ignore_errors=True)
        super(TestCrawls, self).tearDown()


    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(TestCrawls, cls).tearDownClass()


    def test_add_crawl_model(self):

        # Names are super awesome
        ff = self.browser

        # Navigate to the project page
        ff.get(self.live_server_url + self.project.get_absolute_url())
        assert "/projects/potatoes" in ff.current_url

        #TODO Use selenium to locate the icon to click via element ID.
        # Click on "Add Crawl Model"
        # add_crawl = ff.find_element_by_...
        ff.get(self.live_server_url +
               self.project.get_absolute_url() +
               'add_crawl_model')

        assert "/projects/potatoes/add_crawl_model" in ff.current_url

        # Click "Submit" on an empty form.
        submit = ff.find_element_by_id('submit-id-submit')
        submit.click()

        # Verify that errors appear as expected
        name_error = ff.find_element_by_id('error_1_id_name')
        assert name_error.text == "This field is required."
        model_error = ff.find_element_by_id('error_1_id_model')
        assert model_error.text == "This field is required."
        features_error = ff.find_element_by_id('error_1_id_features')
        assert features_error.text == "This field is required."

        # Fill out the form with valid input, and submit
        name = ff.find_element_by_id("id_name")
        name.send_keys("Test Crawl Model")

        #TODO locate test model and features file
        assert exists(TEST_MODEL_PATH) and exists(TEST_FEATURES_PATH)
        model = ff.find_element_by_id("id_model")
        model.send_keys(TEST_MODEL_PATH)

        features = ff.find_element_by_id("id_features")
        features.send_keys(TEST_FEATURES_PATH)

        submit = ff.find_element_by_id('submit-id-submit')
        submit.click()


    def test_add_ache_crawl(self):

        ff = self.browser

        model_copy = TEST_MODEL_PATH + '.copy'
        features_copy = TEST_FEATURES_PATH + '.copy'

        shutil.copyfile(TEST_MODEL_PATH, model_copy)
        shutil.copyfile(TEST_FEATURES_PATH, features_copy)

        test_crawl_model = CrawlModel(
            name = u"Test Crawl Model",
            model = model_copy,
            features = features_copy,
            project = self.project)
        test_crawl_model.save()


        # Navigate to the project page
        ff.get(self.live_server_url + self.project.get_absolute_url())
        assert "/projects/potatoes" in ff.current_url

        # Click on "+ Add Crawl"
        add_crawl = ff.find_element_by_id("link-add-crawl")
        add_crawl.click()
        assert "/projects/potatoes/add_crawl" in ff.current_url

        # Fill out the form with valid input, and submit
        name = ff.find_element_by_id("id_name")
        name.send_keys("Test ACHE Crawl")

        description = ff.find_element_by_id("id_description")
        description.send_keys("Test description")

        ache_radio = ff.find_element_by_id("id_crawler_2")
        assert ache_radio.get_attribute("value") == "ache"
        ache_radio.click()

        crawl_model = ff.find_element_by_id("id_crawl_model")
        crawl_model_select = Select(crawl_model)
        crawl_model_select.select_by_visible_text(test_crawl_model.name)

        seeds_list = ff.find_element_by_id("id_seeds_list")
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"https://binstar.org/\nhttp://www.continuum.io/")
            f.flush()
            seeds_list.send_keys(f.name)

            submit = ff.find_element_by_id('submit-id-submit')
            submit.click()

        assert "projects/potatoes/crawls/test-ache-crawl/" in ff.current_url


    def test_add_crawl_errors(self):

        # Names are awesome
        ff = self.browser

        # Navigate to the project page
        ff.get(self.live_server_url + self.project.get_absolute_url())
        assert "/projects/potatoes" in ff.current_url

        # Click on "+ Add Crawl"
        add_crawl = ff.find_element_by_id("link-add-crawl")
        add_crawl.click()
        assert "/projects/potatoes/add_crawl" in ff.current_url

        # Click "Submit" on an empty form
        submit = ff.find_element_by_id('submit-id-submit')
        submit.click()

        # Verify that errors appear as expected
        name_error = ff.find_element_by_id('error_1_id_name')
        assert name_error.text == "This field is required."
        description_error = ff.find_element_by_id('error_1_id_description')
        assert description_error.text == "This field is required."
        seeds_error = ff.find_element_by_id('error_1_id_seeds_list')
        assert seeds_error.text == "This field is required."


    def test_add_nutch_crawl(self):

        # Names are awesome
        ff = self.browser

        # Navigate to the project page
        ff.get(self.live_server_url + self.project.get_absolute_url())
        assert "/projects/potatoes" in ff.current_url

        # Click on "+ Add Crawl"
        add_crawl = ff.find_element_by_id("link-add-crawl")
        add_crawl.click()
        assert "/projects/potatoes/add_crawl" in ff.current_url

        # Fill out the form with valid input, and submit
        name = ff.find_element_by_id("id_name")
        name.send_keys("Test Nutch Crawl")

        description = ff.find_element_by_id("id_description")
        description.send_keys("Test description")

        nutch_radio = ff.find_element_by_id("id_crawler_1")
        assert nutch_radio.get_attribute("value") == "nutch"
        nutch_radio.click()

        seeds_list = ff.find_element_by_id("id_seeds_list")
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"https://binstar.org/\nhttp://www.continuum.io/")
            f.flush()
            seeds_list.send_keys(f.name)

            submit = ff.find_element_by_id('submit-id-submit')
            submit.click()

        assert "projects/potatoes/crawls/test-nutch-crawl/" in ff.current_url
