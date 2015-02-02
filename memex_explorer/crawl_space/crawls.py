#  IMPORTS
# =========

# Standard Library
# ----------------

# import os
# from subprocess import Popen, PIPE
# import shlex
# from datetime import datetime

from abc import ABCMeta, abstractmethod
#abstractproperty

# Local Imports
# -------------

# from . import db
# from .config import SEED_FILES, MODEL_FILES, CONFIG_FILES, CRAWLS_PATH, LANG_DETECT_PATH, IMAGE_SPACE_PATH
# from .db_api import get_data_source, get_model, set_crawl_status
# from .utils import make_dir, make_dirs, run_proc


#  EXCEPTIONS
# ============

class CrawlException(Exception):
    pass

class NutchException(CrawlException):
    pass

class AcheException(CrawlException):
    pass


# Constants
from django.conf import settings
LANG_DETECT_PATH = settings.LANG_DETECT_PATH


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
        self.id = crawl.id

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
        # TODO
        super().__init__(crawl)

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
