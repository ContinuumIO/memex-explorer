import argparse

from base.models import Project
from crawl_space.models import Crawl
from crawl_space.crawls import AcheCrawl, NutchCrawl


def parse_args():
    parser = argparse.ArgumentParser(
         description='Construct and display a new dashboard.')

    parser.add_argument("-p", "--project", dest="project_slug", type=str,
                        required=True, help="Project slug")
    parser.add_argument("-c", "--crawl", dest="crawl_slug", type=str,
                        required=True, help="Crawl slug")

    return parser.parse_args()


def get_crawl(project_slug, crawl_slug):
    # from ipsh import ipsh; ipsh()
    return Crawl.objects.get(project=Project.objects.get(slug=project_slug),
                             slug=crawl_slug)


class CrawlSupervisor(object):

    def __init__(self, *args, **kwargs):

        c = self.crawl_model = get_crawl(kwargs['project_slug'], kwargs['crawl_slug'])
        if c.crawler == 'ache':
            self.crawl = AcheCrawl(c)

        elif c.crawler == 'nutch':
            self.crawl = NutchCrawl(c)

    def start(self):
        self.crawl.run()


if __name__ == "__main__":

    import django
    django.setup()

    args = parse_args()
    crawl_supervisor = CrawlSupervisor(**vars(args))
    crawl_supervisor.start()
