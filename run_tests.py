import unittest

from tests.test_front_page import ServerUpTest
from tests.test_project import ProjectTest
from tests.test_crawl import CrawlTest
# from tests.test_interactions import InteractionsTest


def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(ServerUpTest))
    suite.addTest(unittest.makeSuite(ProjectTest))
    suite.addTest(unittest.makeSuite(CrawlTest))
    # suite.addTest(unittest.makeSuite(InteractionsTest))

    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
