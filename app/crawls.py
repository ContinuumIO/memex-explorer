#  IMPORTS
# =========

# Standard Library
# ----------------

import os
from subprocess import Popen, PIPE
from datetime import datetime

from abc import ABCMeta

# Local Imports
# -------------


from .config import SEED_FILES, MODEL_FILES, CONFIG_FILES, CRAWLS_PATH, LANG_DETECT_PATH, IMAGE_SPACE_PATH
from .db_api import get_data_source, get_model, set_crawl_status
from .utils import make_dirs, run_proc


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

class Crawl(object):
    """Abstract base class for crawls. This class encapsulates a few basic attributes:

        start_time (datetime.datetime)
        stop_time (datetime.datetime): (`None` if not yet stopped.)

        proc (int): Process ID of the crawl instance.

    @property
        duration (datetime.timedelta): The time elapsed
            between `start_time` and `stop_time` (if stopped) else
            between `start_time` and `datetime.now()`.


    Classes that inherit from `Crawl` are expected to implement the following:

    
    """

    __metaclass__ = ABCMeta

    def __init__(self, crawl):
        """Initialize common crawl attributes."""

        self.crawl_name = crawl.name
        self.project_id = crawl.project_id

        # Handle to crawl process
        self.proc = None


    @property
    def duration(self):
        if self.stop_time:
            delta = self.stop_time - self.start_time
        else:
            delta = datetime.now() - self.start_time
        return delta.total_seconds()


class AcheCrawl(Crawl):

    def __init__(self, crawl):
        self.crawl = crawl
        self.config = os.path.join(CONFIG_FILES, crawl.config)
        self.seeds_file = os.path.join(SEED_FILES, crawl.seeds_list)
        model = get_model(id=crawl.data_model_id)
        self.model_dir = os.path.join(MODEL_FILES, str(model.id))
        self.crawl_dir = os.path.join(CRAWLS_PATH, str(crawl.id))
        self.status = crawl.status
        super(AcheCrawl, self).__init__(crawl)

    def start(self):
        with open(os.path.join(self.crawl_dir, 'stdout.txt'), 'w') as stdout:
            with open(os.path.join(self.crawl_dir,'stderr.txt'), 'w') as stderr:
                self.proc = run_proc("ache startCrawl {} {} {} {} {}".format(
                                 self.crawl_dir, self.config, self.seeds_file,
                                 self.model_dir, LANG_DETECT_PATH),
                            stdout=stdout, stderr=stderr)
        return self.proc.pid

    def stop(self):
        if self.proc is not None:
            print("Killing %s" % str(self.proc.pid))
            self.proc.kill()
            self.stop_time = datetime.now()


    def statistics(self):
        harvest_source = get_data_source(self.crawl, "harvest")
        harvest_path = os.path.join(self.crawl_dir, harvest_source.data_uri)
        proc = run_proc("tail -n 1 %s" % harvest_path)
        stdout, stderr = proc.communicate()
        if stderr:
            raise AcheException(stderr)

        ret = {}
        ret['nutch'] = False
        relevant, crawled = tuple(stdout.split('\t')[:2])
        ret['harvest_rate'] = "%.2f" % (float(relevant) / float(crawled))
        ret['num_crawled'] = crawled

        return ret

    def get_status(self):
        if self.proc is None:
            pass
        else:
            self.proc.poll()
            if self.proc is None:
                self.status = "No process exists"
            elif self.proc.returncode is None:
                self.status = "Crawl running"
            elif self.proc.returncode < 0:
                self.status = "Crawl was stopped"
            else:
                self.status = "Crawl not running"
        return self.status


class NutchCrawl(Crawl):

    def __init__(self, crawl, num_rounds=1):
        self.crawl = crawl
        self.seed_dir =  os.path.join(SEED_FILES, crawl.seeds_list)
        self.crawl_dir = os.path.join(CRAWLS_PATH, str(crawl.id))
        self.number_of_rounds = num_rounds
        self.status = crawl.status
        super(NutchCrawl, self).__init__(crawl)

    def start(self):
        if os.path.exists(os.path.join(self.crawl_dir, 'stop_flag')):
            stop_file = os.path.join(self.crawl_dir, "stop_flag")
            remove_stop_flag = Popen(['rm', stop_file]).wait()
        self.proc = Popen(['crawl', self.seed_dir, self.crawl_dir, str(self.number_of_rounds)])
        self.status = set_crawl_status(self.crawl, "Crawl has run previously")
        return self.proc.pid

    def stop(self):
        file = os.path.join(self.crawl_dir, "stop_flag")
        write_stop_flag = run_proc("touch %s" % file)
        return write_stop_flag

    def dump_images(self, image_space):
        self.img_dir = os.path.join(IMAGE_SPACE_PATH, str(image_space.id), 'images')
        make_dirs(self.img_dir)
        img_dump_proc = run_proc(
            "nutch dump -outputDir {} -segment {} -mimetype image/jpeg image/png".format(
                            self.img_dir, os.path.join(self.crawl_dir, 'segments')),
                        stdout=PIPE, stderr=PIPE)

        stdout, stderr = img_dump_proc.communicate()
        if stderr:
            raise NutchException(stderr)

        return "Dumping images"

    def get_status(self):
        if self.proc is None:
            pass
        else:
            self.proc.poll()
            if self.proc is None:
                self.status = "No process exists"
            elif self.proc.returncode is None:
                self.status = "Crawl running"
            elif self.proc.returncode < 0:
                self.status = "Crawl was stopped"
            elif self.status == "Crawl not running" and self.keep_going():
                self.start()
                self.status = "Crawl running"
            else:
                self.status = "Crawl not running"
        return self.status

    def statistics(self):
        crawl_db_dir = os.path.join(self.crawl_dir, 'crawldb')
        if not os.path.exists(crawl_db_dir):
            ret = {}
            ret['num_crawled'] = 0
            ret['nutch'] = True
            return ret

        proc_str = "nutch readdb {} -stats".format(crawl_db_dir)
        stats_proc = run_proc(proc_str)
                                              
        stdout, stderr = stats_proc.communicate()
        if stderr:
            raise NutchException(stderr)

        ret = {'num_crawled': 0}

        for line in stdout.split('\n'):
            if 'db_fetched' in line:
                ret['num_crawled'] = int(line.split('\t')[-1])

        # ret['duration'] = self.duration
        ret['nutch'] = True

        return ret

    def keep_going(self):
        if os.path.exists(os.path.join(self.crawl_dir, 'stop_flag')):
            return False
        else:
            return True
