"""
Unit testing the front page. (Sanity check.)
"""

from test_skeleton import TestSkeleton

class ServerUpTest(TestSkeleton):

    def test_page_exists(self):
        """Test if root page exists."""
        response = self.test_app.get('/')
        self.assert_200(response)

    def test_title(self):
        """Test title of root page."""
        response = self.test_app.get('/')
        self.assertIn('MEMEX EXPLORER', response.data)
