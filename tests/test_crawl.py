"""
Unit testing basic crawl actions.
"""

#  IMPORTS
# =========

import shutil
import os
from StringIO import StringIO

from app.models import Project
from app.utils import make_dirs

from test_skeleton import TestSkeleton


class CrawlTest(TestSkeleton):

    #  SETUP & TEARDOWN
    # ==================

    @classmethod
    def setUpClass(cls):
        """Initialize test application (see TestSkeleton.setUpClass),
        and create a temporary directory structure.
        """
        super(CrawlTest, cls).setUpClass()

        # Create necessary directory structure to test crawl registration
        for key in ("SEED_FILES", "MODEL_FILES", "CONFIG_FILES", "CRAWLS_PATH"):
            make_dirs(cls.test_app.application.config[key])


    @classmethod
    def tearDownClass(cls):
        super(CrawlTest, cls).tearDownClass()

        # Remove resources directory
        BASEDIR = cls.test_app.application.config['BASEDIR']
        shutil.rmtree(os.path.join(BASEDIR, 'resources'))


    def setUp(self):
        """Add test_project fixture to database."""
        super(CrawlTest, self).setUp()

        # Add test project
        test_project = Project(slug="cats",
                               name="cats",
                               description="Cats are cute!",
                               icon="fa-arrows")

        self.test_db.session.add(test_project)
        self.test_db.session.commit()


    #  UNIT TESTS
    # ============


    def test_page_exists(self):
        """Test if `cats/add_crawl` endpoint exists."""
        response = self.test_app.get('cats/add_crawl')
        self.assert_200(response)


    def test_post_no_data(self):
        """"Send a POST request with no data."""

        data = {}

        response = self.test_app.post('cats/add_crawl', data=data,
            follow_redirects=True)
        self.assertIn("This field is required.", response.data)


    def test_post_partial_data(self):
        """Send a POST request with partial data."""

        response = self.test_app.get('/')
        data = {"description": "dogs are better"}

        response = self.test_app.post('cats/add_crawl', data=data,
            follow_redirects=True)
        self.assertIn("This field is required.", response.data)


    def test_register_nutch_crawl(self):
        """Register a valid Nutch crawl."""

        data = {"name": "Cat Crawl",
                "description": "Find all the best cat pictures on the internet!",
                "crawler": "nutch",
                # Emulate file upload with StringIO
                "seeds_list": (StringIO(
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"), 'seeds.txt')}

        response = self.test_app.post('cats/add_crawl', buffered=True,
            content_type='multipart/form-data', data=data,
            follow_redirects=True)
        self.assertIn("Cat Crawl has successfully been registered!", response.data)


    def test_register_ache_crawl(self):
        """Register a valid ACHE crawl."""

        data = {"name": "Cat Crawl",
            "description": "Find all the best cat pictures on the internet!",
            "crawler": "ache",
            # New model and features file
            "model_radio": "new",
            "new_model_file": (StringIO("model_content"), 'new.model'),
            "new_model_features": (StringIO("model_features"), 'new.features'),
            "new_model_name": "New Model",
            "seeds_list": (StringIO(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"), 'seeds.txt')}

        response = self.test_app.post('cats/add_crawl', buffered=True,
            content_type='multipart/form-data', data=data,
            follow_redirects=True)

        self.assertIn("Cat Crawl has successfully been registered!", response.data)


    def test_duplicate_crawl(self):
        """Register a duplicate crawl."""

        data = {"name": "Cat Crawl",
                "description": "Find all the best cat pictures on the internet!",
                "crawler": "nutch",
                # Emulate file upload with StringIO
                "seeds_list": (StringIO(
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"), 'seeds.txt')}

        response = self.test_app.post('cats/add_crawl', buffered=True,
            content_type='multipart/form-data', data=data,
            follow_redirects=True)
        self.assertIn("Cat Crawl has successfully been registered!", response.data)


        # Refresh with new StringIO instance
        data["seeds_list"] = (StringIO(
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"), 'seeds.txt')

        response = self.test_app.post('cats/add_crawl', buffered=True,
            content_type='multipart/form-data', data=data,
            follow_redirects=True)
        self.assertIn("Crawl name already exists, please choose another name", response.data)


    def test_delete_crawl(self):
        """Register and delete a crawl."""

        self.test_register_nutch_crawl()

        response = self.test_app.post('cats/crawls/cat-crawl/delete',
            follow_redirects=True)
        self.assertIn("Cat Crawl has successfully been deleted", response.data)
