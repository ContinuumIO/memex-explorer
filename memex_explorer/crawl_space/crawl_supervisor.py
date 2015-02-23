"""Crawl Supervisor is a free-standing script that monitors and logs output
from crawl processes, via CrawlRunner.

At the moment, this is a thin wrapper for the purpose of development. In
production systems, Memex Explorer should leverage a job queue
that manages crawl processes on distributed systems.


Example
-------

    $ python crawl_supervisor.py --project project_slug --crawl crawl_slug

"""
from __future__ import absolute_import

import argparse
import inspect
import sys, os

from crawl_runners import AcheCrawlRunner, NutchCrawlRunner

from base.models import Project
from crawl_space.models import Crawl

def get_crawl(project_slug, crawl_slug):
    project = Project.objects.get(slug=project_slug)
    crawl = Crawl.objects.get(project=project, slug=crawl_slug)
    return crawl


def parse_args():
    """Helper function to parse command line arguments.

    Arguments
    ---------

    -p, --project : str, required
        Project slug
    -c, --crawl : str, required
        Crawl slug

    Returns
    -------

    argparse.Namespace    
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", dest="project_slug", type=str,
                        required=True, help="Project slug")
    parser.add_argument("-c", "--crawl", dest="crawl_slug", type=str,
                        required=True, help="Crawl slug")
    return parser.parse_args()




class CrawlSupervisor(object):
    """Wraps crawl process execution.

    Parameters
    ----------

    project_slug : str, required
    crawl_slug : str, required

    Attributes
    ----------

    crawl_model : crawl_space.models.CrawlModel
    crawl : crawl_space.crawls.CrawlRunner subclass
        Currently supports AcheCrawlRunner and NutchCrawlRunner.
    """

    def __init__(self, *args, **kwargs):
        import ipdb
        ipdb.set_trace()
        crawl = self.crawl_model = get_crawl(
            kwargs['project_slug'],
            kwargs['crawl_slug'])

        if crawl.crawler == 'ache':
            self.crawl_runner = AcheCrawlRunner(crawl)

        elif crawl.crawler == 'nutch':
            self.crawl_runner = NutchCrawlRunner(crawl)

    def start(self):
        """Start the crawl process.""" 
        self.crawl_runner.run()

if __name__ == "__main__":
    import django
    django.setup()
    args = parse_args()
    crawl_supervisor = CrawlSupervisor(**vars(args))
    crawl_supervisor.start()
