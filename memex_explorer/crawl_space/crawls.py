#  IMPORTS
# =========

# Standard Library
# ----------------

import os
import subprocess
import time
# import shlex
# from datetime import datetime

from abc import ABCMeta, abstractmethod
#abstractproperty

# Local Imports
# -------------

from crawl_space.settings import (LANG_DETECT_PATH, CRAWL_PATH,
                                  MODEL_PATH, CONFIG_PATH)

# from .utils import make_dir, make_dirs, run_proc
from rq import get_current_job

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
        self.crawl = crawl



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
        self.crawl_dir = c.get_crawl_path()
        self.seeds_file = crawl.seeds_list.path
        self.model_dir = crawl.data_model.get_model_path()
        self._status = crawl.status

    def start(self):
        call = ["ache", "startCrawl",
                self.crawl_dir,
                self.config,
                self.seeds_file,
                self.model_dir,
                LANG_DETECT_PATH]
        job = get_current_job()
        job.set_id(str(self.crawl.pk))

        with open(os.path.join(self.crawl_dir, 'ache.stdout'), 'w') as stdout:
            self.proc = subprocess.Popen(call,
                stdout=stdout, stderr=subprocess.STDOUT)

        stop_path = os.path.join(self.crawl.get_crawl_path(), 'stop')
        self.crawl.status = "running"
        self.crawl.save()


        while self.proc.poll() is None:
            self.log_statistics()
            if os.path.isfile(stop_path):
                os.remove(stop_path)
                break

            print('.',end="",flush=True)
            time.sleep(5)

        self.proc.terminate()
        self.crawl.status = "stopped"
        self.crawl.save()
        return True


    def log_statistics(self):
        harvest_path = os.path.join(self.crawl_dir, 'data_monitor/harvestinfo.csv')
        proc = subprocess.Popen(["tail", "-n", "1", harvest_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if stderr and b"No such file or directory" not in stderr:
                raise AcheException(stderr)

        harvest_stats = stdout.decode() 

        if not harvest_stats:
            return

        relevant, crawled = tuple(harvest_stats.split('\t')[:2])
        self.crawl.harvest_rate = "%.2f" % (float(relevant) / float(crawled))
        self.crawl.pages_crawled = crawled
        self.crawl.save()


    def status(self):
        return self._status
        # TODO


class NutchCrawl(Crawl):

    def __init__(self, crawl):
        # TODO
        super().__init__(crawl)

    def start(self):
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
