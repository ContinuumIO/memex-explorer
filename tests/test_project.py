"""
Unit testing basic project actions.
"""

#  IMPORTS
# =========

from test_skeleton import TestSkeleton


class ProjectTest(TestSkeleton):

    #  SETUP & TEARDOWN
    # ==================
    # Not required to unit test projects (no side effects)


    #  UNIT TESTS
    # ============

    def test_page_exists(self):
        """Test if `/add_project` endpoint exists."""
        response = self.test_app.get('/add_project')
        self.assert_200(response)

    def test_no_data(self):
        """"Send a POST request with no data."""

        data = {}

        response = self.test_app.post('/add_project', data=data, follow_redirects=True)
        self.assertIn("This field is required.", response.data)

    def test_partial_data(self):
        """Send a POST request with partial data."""

        data = {"description": "test test"}

        response = self.test_app.post('/add_project', data=data, follow_redirects=True)
        self.assertIn("This field is required.", response.data)

    def test_register_project(self):
        """Register a valid project."""

        data = {"name": "cats",
                "description": "Cats are cute!",
                "icon": "fa-arrows"}

        response = self.test_app.post('/add_project', data=data, follow_redirects=True)
        self.assertIn("Project &#39;cats&#39; was successfully registered", response.data)


    def test_duplicate_project(self):
        """Register a duplicate project."""

        data = {"name": "cats",
                "description": "Cats are cute!",
                "icon": "fa-arrows"}

        response = self.test_app.post('/add_project', data=data, follow_redirects=True)
        self.assertIn("Project &#39;cats&#39; was successfully registered", response.data)

        response = self.test_app.post('/add_project', data=data, follow_redirects=True)
        self.assertIn("Project &#39;cats&#39; already exists", response.data)
