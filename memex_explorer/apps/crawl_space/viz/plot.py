from abc import ABCMeta, abstractmethod
from bokeh.models import ColumnDataSource
from bokeh.plotting import Document, Session

from harvest import Harvest
from domain import Domain


class PlotsNotReadyException(Exception):
    pass 


class AcheDashboard(object):

    def __init__(self, crawl):
        if crawl.crawler != "ache":
            raise ValueError("Crawl must be using the Ache crawler.")
        self.harvest = Harvest(crawl)
        self.domain = Domain(crawl)

    def get_harvest_plot(self):
        try:
            script, div = self.harvest.create()
        except Exception:
            raise PlotsNotReadyException("Harvest plot sources are not yet intiialized.")
        return [script, div]

    def get_domain_plot(self):
        try:
            script, div = self.domain.create()
        except Exception:
            raise PlotsNotReadyException("Domain plot sources are not yet intiialized.")
        return [script, div]

    def get_plots(self):
        harvest_plot = self.get_harvest_plot()
        domain_plot = self.get_domain_plot()
        return {
            'scripts': [domain_plot[0], harvest_plot[0]],
            'divs': [domain_plot[1], harvest_plot[1]],
        }

