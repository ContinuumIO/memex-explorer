import subprocess
from .config import CRAWLER_PATH


class CrawlAcheInstance(object):

    def __init__(self, seeds_list, model_name):
        self.seeds_list = seeds_list
        self.model_name = model_name
        self.proc = None

    def start(self):
        self.proc = subprocess.Popen('./run_crawler.sh {0} conf/ conf/seeds/{1} conf/models/{2}/'
                                     .format(CRAWLER_PATH, self.seeds_list, self.model_name), shell=True)
        #self.proc = subprocess.Popen('./count_things.sh', shell=True)
        return self.proc.pid

    def stop(self):
        if self.proc is not None:
            print("Killing %s" % str(self.proc.pid))
            self.proc.kill()
            proc2 = subprocess.Popen('./stop_crawler.sh {0}'.format((CRAWLER_PATH)), shell=True)

    def status(self):
        if self.proc is None:
            return "No process exists"
        elif self.proc.returncode is None:
            return "Running"
        elif self.proc.returncode < 0:
            return "Stopped (Unused)"
        else:
            return "An error occurred"
