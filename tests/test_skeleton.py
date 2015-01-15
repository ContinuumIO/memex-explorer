"""
Base test skeleton.
"""

import os
import sys
import unittest

from flask.ext.testing import TestCase, LiveServerTestCase

from app import app, db

class TestSkeleton(TestCase):

    # Required for flask-testing
    # See https://pythonhosted.org/Flask-Testing/#testing-with-liveserver
    def create_app(self):
        return app


    @classmethod
    def setUpClass(cls):
        print "Setting up"
        app.config.from_pyfile('../tests/test_config.py')
        cls.test_app = app.test_client()
        cls.test_db = db


    @classmethod
    def tearDownClass(cls):
        pass


    def setUp(self):
        self.test_db.create_all()
        

    def tearDown(self):
        self.test_db.session.remove()
        self.test_db.drop_all()


class LiveTestSkeleton(TestSkeleton, LiveServerTestCase):
    pass

    # def create_app(self):
    #     return app


    # def setUpClass(cls):



    # def setUp(self):
    #     """Add test_project fixture to database."""
    #     super(LiveTestSkeleton, self).setUp()
