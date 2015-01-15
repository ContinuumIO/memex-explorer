# import mock
# from nose.tools import *
# import re
# import requests
# from bs4 import BeautifulSoup
# from tests.fixtures import mock_links, mock_urls, mock_forms

import shutil
import os
from StringIO import StringIO

from app.models import Project
from app.utils import make_dirs

from test_skeleton import LiveTestSkeleton
from robobrowser.browser import RoboBrowser
from robobrowser import exceptions


class InteractionsTest(LiveTestSkeleton):

    @classmethod
    def setUpClass(cls):
        """Initialize test application (see TestSkeleton.setUpClass),
        and create a temporary directory structure.
        """
        super(InteractionsTest, cls).setUpClass()

        # Create necessary directory structure to test crawl registration
        for key in ("SEED_FILES", "MODEL_FILES", "CONFIG_FILES", "CRAWLS_PATH"):
            make_dirs(cls.test_app.application.config[key])

        cls.browser = RoboBrowser(user_agent='MEMEX_TESTER')


    def test_register_project(self):


        # from ipsh import ipsh; ipsh()
        # alias self.browser
        b = self.browser

        # Open home page
        HOME_PAGE = self.get_server_url()
        b.open(HOME_PAGE)

        self.assert_200(b.response)

        # Add project
        add_project = b.find(href='/add_project')
        b.follow_link(add_project)

        self.assertEqual(b.url, 'http://localhost:8943/add_project')

# # Get the signup form
# signup_form = browser.get_form(class_='signup')
# signup_form         # <RoboForm user[name]=, user[email]=, ...

# # Inspect its values
# signup_form['authenticity_token'].value     # 6d03597 ...

# # Fill it out
# signup_form['user[name]'].value = 'python-robot'
# signup_form['user[user_password]'].value = 'secret'

# # Submit the form
# browser.submit_form(signup_form)

