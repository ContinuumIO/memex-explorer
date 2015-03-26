"""Provides CrawlRunner subclasses to wrap crawl process execution and
monitoring."""

import os
import sys
import signal
from os.path import join
import subprocess
import time
import shlex

from abc import ABCMeta, abstractmethod

from settings import (LANG_DETECT_PATH, CRAWL_PATH,
                      MODEL_PATH, CONFIG_PATH, IMAGES_PATH)
from utils import touch, rm_if_exists


# Exceptions
class CrawlException(Exception):
    pass

class NutchException(CrawlException):
    pass

class AcheException(CrawlException):
    pass



#  CLASSES
# ==========

class CrawlRunner(object):
    """Abstract base class for crawl runners.

    CrawlRunner subclasses are expected to implement these methods:
        call(self)
        log_statistics(self)

    Parameters
    ----------

    crawl : crawl_space.models.Crawl subclass

    Attributes
    ----------

    crawl : crawl_space.models.Crawl subclass
    crawl_dir : str
        Path to crawl directory,
          ex. `resources/crawls/4`.
    seeds_path : str
        Path to seeds file (or directory, in the case of Nutch),
          ex. `resources/crawls/4/seeds`.
    stop_file : str
        Path to a sentinel file that indicates a stop has been requested.

    """

    __metaclass__ = ABCMeta

    def __init__(self, crawl):
        """Initialize common CrawlRunner attributes based on `crawl`."""

        self.crawl = crawl
        self.crawl_dir = crawl.get_crawl_path()
        self.seeds_path = crawl.seeds_list.path
        self.stop_file = join(self.crawl_dir, 'stop')
        self.force_stop_file = join(self.crawl_dir, 'stop')
        self.solr_url = "http://localhost:8983/solr/"  #TODO - Move to Crawl

    @property
    @abstractmethod
    def call(self):
        """The tokenized call to the appropriate crawl process.
        Ex:
            return ['ache', 'startCrawl', *args]

        """
        pass

    def run(self):
        """Run the crawl.

        Note
        ----
        This method should be called via super() from a subclass.

        Operation
        ---------
        First, remove the stop file if it exists. This is a convenient action
        while developing, however, #TODO should raise an error if the stop
        file exists for a crawl that has not yet run.

        Second, open a subprocess based on `self.call` (defined by a subclass)
        and direct its output to an appropriate log file. Update the status.

        Then, as long as the process is running, every five seconds:
          1. Log statistics
          2. Check if a stop file has appeared, exit the process accordingly

        When a process has ended--either naturally or after a stop was
        requested--the crawl status is updated.

        """

        rm_if_exists(self.stop_file)

        with open(join(self.crawl_dir, 'crawl_proc.log'), 'a') as stdout:
            self.proc = subprocess.Popen(self.call,
                stdout=stdout, stderr=subprocess.STDOUT,
                preexec_fn=os.setsid)

        self.crawl.status = "running"
        self.crawl.save()

        stopped_by_user = False
        while self.proc.poll() is None:
            self.log_statistics()
            if rm_if_exists(self.stop_file):
                stopped_by_user = True
                break

            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(5)

        if stopped_by_user:
            os.killpg(self.proc.pid, signal.SIGTERM)

        self.crawl.status = "stopped"
        self.crawl.save()
        return True

    @abstractmethod
    def log_statistics(self):
        pass


class AcheCrawlRunner(CrawlRunner):
    """Subclass of CrawlRunner that adds a few ACHE specific attributes.

    Attributes
    ----------

    config_dir : str
        Path to the ACHE configuration directory applied to this crawl.
        Hardcoded to "resources/configs/config_default" at the moment.
    model_dir : str
        Path to the ACHE crawl model directory, containing "pageclassifier"
        model and features file.

    """

    def __init__(self, crawl):
        """ACHE specific attributes."""

        super(AcheCrawlRunner, self).__init__(crawl)

        self.config_dir = join(CONFIG_PATH, self.crawl.config)
        self.model_dir = self.crawl.crawl_model.get_model_path()


    @property
    def call(self):
        return ["ache", "startCrawl",
                self.crawl_dir,
                self.config_dir,
                self.seeds_path,
                self.model_dir,
                LANG_DETECT_PATH]


    def log_statistics(self):
        harvest_path = join(self.crawl_dir, 'data_monitor/harvestinfo.csv')
        proc = subprocess.Popen(["tail", "-n", "1", harvest_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if stderr and b"No such file or directory" not in stderr:
                raise AcheException(stderr)

        harvest_stats = stdout.decode()

        if not harvest_stats:
            return

        relevant, crawled = tuple(harvest_stats.split('\t')[:2])
        self.crawl.harvest_rate = "%.2f" % (float(relevant) /
                                                  float(crawled))
        self.crawl.pages_crawled = crawled
        self.crawl.save()


class NutchCrawlRunner(CrawlRunner):

    def __init__(self, crawl):
        """Nutch specific attributes."""
        super(NutchCrawlRunner, self).__init__(crawl)


    @property
    def call(self):
        return ["crawl",
                self.seeds_path,
                self.crawl_dir,
                self.solr_url,
                "1"]

    def run(self):
        while True:
            rm_if_exists(self.stop_file)
            rm_if_exists(self.force_stop_file)

            with open(join(self.crawl_dir, 'crawl_proc.log'), 'a') as stdout:
                self.proc = subprocess.Popen(self.call,
                    stdout=stdout, stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid)

            self.crawl.status = "running"
            self.crawl.save()

            stopped_by_user = False
            while self.proc.poll() is None:
                if rm_if_exists(self.stop_file):
                    stopped_by_user = True
                    self.crawl.status = "stopping"
                    self.crawl.save()
                elif rm_if_exists(self.force_stop_file):
                    stopped_by_user = True
                    os.killpg(self.proc.pid, signal.SIGTERM)
                    break
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(5)
                self.log_statistics()

            if stopped_by_user:
                self.crawl.status = "stopped"
                self.crawl.save()
                break

    def log_statistics(self):
        crawl_db_dir = join(self.crawl_dir, 'crawldb')
        if not os.path.exists(crawl_db_dir):
            self.crawl.pages_crawled = 0
            self.crawl.save()
            return
        stats_call = "nutch readdb {} -stats".format(crawl_db_dir)
        self.stats_proc = subprocess.Popen(shlex.split(stats_call), stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

        stdout, stderr = self.stats_proc.communicate()

        if stderr:
            raise NutchException(stderr)

        nutch_stats = stdout.decode()

        for line in stdout.split('\n'):
            if 'db_fetched' in line:
                self.crawl.pages_crawled = int(line.split('\t')[-1])
                self.crawl.save()

