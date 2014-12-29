from __future__ import absolute_import, division, print_function
import subprocess
import os

from .config import SEED_FILES, MODEL_FILES, CONFIG_FILES, CRAWLS_PATH, LANG_DETECT_PATH, IMAGE_SPACE_PATH


class AcheCrawl(object):

    def __init__(self, crawl_name, seeds_file, model_name, conf_name):
        self.crawl_name = crawl_name
        self.config = os.path.join(CONFIG_FILES, conf_name)
        self.seeds_file = os.path.join(SEED_FILES, seeds_file)
        self.model_dir = os.path.join(MODEL_FILES, model_name)
        self.crawl_dir = os.path.join(CRAWLS_PATH, crawl_name)
        self.proc = None
        # TODO record start and stop variables
        #self.start_timestamp
        #self.stop_timestamp

    def start(self):
        with open(os.path.join(self.crawl_dir, 'stdout.txt'), 'w') as stdout:
            with open(os.path.join(self.crawl_dir,'stderr.txt'), 'w') as stderr:
                self.proc = subprocess.Popen(['ache', 'startCrawl', self.crawl_dir, self.config, self.seeds_file,
                                          self.model_dir, LANG_DETECT_PATH], stdout=stdout, stderr=stderr)
        self.proc.poll()
        return self.proc.pid

    def stop(self):
        if self.proc is not None:
            print("Killing %s" % str(self.proc.pid))
            self.proc.kill()

    def status(self):
        if self.proc is None:
            return "No process exists"
        elif self.proc.returncode is None:
            return "Running"
        elif self.proc.returncode < 0:
            return "Process was terminated by signal %s" % self.proc.returncode
        else:
            return "Process ended"


class NutchCrawl(object):

    def __init__(self, seed_dir, crawl_dir):
        self.seed_dir =  os.path.join(SEED_FILES, seed_dir)
        self.crawl_dir = os.path.join(CRAWLS_PATH, crawl_dir)
        self.img_dir = os.path.join(IMAGE_SPACE_PATH, crawl_dir)
        #TODO Switch from "2" to parameter.
        # For now let's set up number_of_rounds to 1.
        self.number_of_rounds = "1"
        #self.number_of_rounds = numberOfRounds
        self.proc = None

    def start(self):
        subprocess.Popen(['mkdir', self.crawl_dir]).wait()
        self.proc = subprocess.Popen(['crawl', self.seed_dir, self.crawl_dir, self.number_of_rounds])
        self.proc.poll()
        return self.proc.pid

    def stop(self):
        if self.proc is not None:
            print("Killing %s" % str(self.proc.pid))
            self.proc.kill()

    def status(self):
        if self.proc is None:
            return "No process exists"
        elif self.proc.returncode is None:
            return "Running"
        elif self.proc.returncode < 0:
            return "Process was terminated by signal %s" % self.proc.returncode
        else:
            return "Process ended"

    def dump_images(self):
        if self.proc.returncode is None:
            return "Crawl process is still running, can't dump images yet"
        elif self.proc.returncode < 0:
            return "Process was terminated by signal %s, data could had been corrupted" % self.proc.returncode
        else:
            with open(os.path.join(self.crawl_dir, 'img_stdout.txt'), 'w') as stdout:
                with open(os.path.join(self.crawl_dir,'img_stderr.txt'), 'w') as stderr:
                    img_dump_proc = subprocess.Popen(['nutch', 'dump', '-outputDir', self.img_dir, '-segment',
                                  os.path.join(self.crawl_dir, 'segments'), '-mimetype', 'image/jpeg', 'image/png',
                                  'text/html'], stdout=stdout, stderr=stderr)
            return "Dumping images"

    def stats(self):
        with open(os.path.join(self.crawl_dir, 'stats_stdout.txt'), 'w') as stdout:
            with open(os.path.join(self.crawl_dir,'stats_stderr.txt'), 'w') as stderr:
                stats_proc = subprocess.Popen(['nutch', 'readdb', os.path.join(self.crawl_dir, 'crawldb'), '-stats'],
                                              stdout=stdout, stderr=stderr)
                # Wait until process finishes
                stats_proc.wait()
        num_lines = sum(1 for line in open('stats_stdout.txt'))
        with open(os.path.join(self.crawl_dir, 'stats_stdout.txt'), 'r') as stdout:
            stats_output = stdout.readlines()
                lines=[3,num_lines-1]
                
        return stats_output