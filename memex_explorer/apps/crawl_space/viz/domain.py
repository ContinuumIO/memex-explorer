"""
Generate a bar chart of number of pages crawled in each domain.
"""
from __future__ import division

import pandas as pd
from blaze import *
from bokeh.plotting import *
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, DataRange1d, FactorRange
from tld import get_tld
import traceback
import subprocess
import shlex

from apps.crawl_space.settings import CRAWL_PATH


GREEN = "#47a838"
DARK_GRAY = "#2e2e2e"
LIGHT_GRAY = "#6e6e6e"
TAIL_LENGTH = 10000


def extract_tld(url):
    try:
        return get_tld(url, fail_silently=True)
    except:
        traceback.print_exc()
        print "\n\nInvalid url: %s" % url
        return url

class Domain(object):

    def __init__(self, crawl, sort='crawled'):
        # TODO Retrieve plot datasources from db
        self.crawled_data = os.path.join(CRAWL_PATH, str(crawl.id), 'data_monitor/crawledpages.csv')
        self.relevant_data = os.path.join(CRAWL_PATH, str(crawl.id), 'data_monitor/relevantpages.csv')

        self.sort = sort

    def update_source(self):

        # Relevant
        df = pd.read_csv(self.relevant_data, delimiter='\t', header=None,
                         names=['url', 'timestamp']).tail(n=TAIL_LENGTH)
        df['domain'] = df['url'].apply(extract_tld)
        df1 = df.groupby(['domain']).size()

        # Crawled
        df = pd.read_csv(self.crawled_data, delimiter='\t', header=None,
                         names=['url', 'timestamp']).tail(n=TAIL_LENGTH)
        df['domain'] = df['url'].apply(extract_tld)
        df2 = df.groupby(['domain']).size()

        df = pd.concat((df1, df2), axis=1)
        df.columns = ['relevant', 'crawled']

        df = df.sort(self.sort, ascending=False).head(25).fillna(value=0)

        for col in df.columns:
            df['%s_half' % col] = df[col] / 2

        df.reset_index(inplace=True)

        source = into(ColumnDataSource, df)
        return source

    def create(self):

        self.source = self.update_source()

        xdr = DataRange1d(sources=[self.source.columns("crawled")])

        p = figure(plot_width=400, plot_height=400,
            title="Domains Sorted by %s" % self.sort, x_range = xdr,
            y_range = FactorRange(factors=self.source.data['index']),
            tools='reset, resize, save')

        p.rect(y='index', x='crawled_half', height=0.75, width='crawled',
               color=DARK_GRAY, source = self.source, legend="crawled")
        p.rect(y='index', x='relevant_half', height=0.75, width='relevant',
               color=GREEN, source = self.source, legend="relevant")

        p.ygrid.grid_line_color = None
        p.xgrid.grid_line_color = '#8592A0'
        p.axis.major_label_text_font_size = "8pt"

        script, div = components(p, INLINE)

        return (script, div)

