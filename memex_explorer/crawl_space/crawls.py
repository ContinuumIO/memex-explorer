#  IMPORTS
# =========

# Standard Library
# ----------------

import os
import subprocess
# import shlex
# from datetime import datetime

from abc import ABCMeta, abstractmethod
#abstractproperty

# Local Imports
# -------------

from crawl_space.settings import (LANG_DETECT_PATH, CRAWL_PATH,
                                  MODEL_PATH, CONFIG_PATH)

# from .utils import make_dir, make_dirs, run_proc

#  EXCEPTIONS
# ============

class CrawlException(Exception):
    pass

class NutchException(CrawlException):
    pass

class AcheException(CrawlException):
    pass



#  CLASSES
# ==========

class Crawl(metaclass=ABCMeta):
    """Abstract base class for crawls. `Crawl` encapsulates these attributes:

        start_time (datetime.datetime)
        stop_time (datetime.datetime): (`None` if not yet stopped.)


    @property
        duration (datetime.timedelta): The time elapsed
            between `start_time` and `stop_time` (if stopped) else
            between `start_time` and `datetime.now()`.


    Classes that inherit from `Crawl` are expected to implement the following:

        crawl
        stop
        statistics
        status
    
    """

    def __init__(self, crawl):
        """Initialize common crawl attributes."""
        c = self.crawl = crawl



    # name 
    # slug 
    # description 
    # crawler 
    # status 
    # config 
    # seeds_list 
    # pages_crawled 
    # harvest_rate 
    # project 
    # data_model



    # @property
    # def duration(self):
    #     if self.stop_time:
    #         delta = self.stop_time - self.start_time
    #     else:
    #         delta = datetime.now() - self.start_time
    #     return delta.total_seconds()


class AcheCrawl(Crawl):

    def __init__(self, crawl):
        """ACHE specific attributes."""

        super().__init__(crawl)

        c = self.crawl
        self.config = os.path.join(CONFIG_PATH, c.config)
        self.crawl_dir = os.path.join(CRAWL_PATH, str(c.id))
        self.seeds_file = crawl.seeds_list.path
        from ipsh import ipsh; ipsh()

        self.model_dir = os.path.join(MODEL_PATH, str(model.id))
        self.crawl_dir = os.path.join(CRAWLS_PATH, str(crawl.id))
        self.status = crawl.status

    def crawl(self):
        self.proc = subprocess.Popen(["ache", "startCrawl",
                self.crawl_dir,
                self.config,
                self.seeds_file,
                self.model_dir,
                LANG_DETECT_PATH],
            stdout=stdout, stderr=subprocess.PIPE)

    def stop(self):
        pass
        # TODO


    def statistics(self):
        pass
        # TODO

    def status(self):
        pass
        # TODO


class NutchCrawl(Crawl):

    def __init__(self, crawl):
        # TODO
        super().__init__(crawl)

    def crawl(self):
        pass
        # TODO

    def stop(self):
        pass
        # TODO


    def statistics(self):
        pass
        # TODO

    def status(self):
        pass
        # TODO

    def dump_images(self, image_space):
        pass
