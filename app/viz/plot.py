from abc import ABCMeta, abstractmethod
from bokeh.models import ColumnDataSource
from bokeh.plotting import Document, Session


class PlotManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, plot):
        self.doc_name = '%d_%s' % (plot.id, plot.name)
        self.plot = plot

    @abstractmethod
    def create(self):
        pass
