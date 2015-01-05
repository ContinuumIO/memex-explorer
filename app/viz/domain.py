"""
Generate a bar chart of number of pages crawled in each domain.
"""
from __future__ import division

import pandas as pd
from blaze import into
from bokeh.plotting import *
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, DataRange1d, FactorRange
from tld import get_tld
from functools import partial

from app import db
from plot import PlotManager
from ..config import CRAWLS_PATH


GREEN = "#47a838"
DARK_GRAY = "#2e2e2e"
LIGHT_GRAY = "#6e6e6e"

class Domain(PlotManager):

    def __init__(self, datasources, plot, sort='relevant'):
        # TODO Retrieve plot datasources from db
        self.crawled_data = CRAWLS_PATH + datasources['crawled'].data_uri
        self.relevant_data = CRAWLS_PATH+ datasources['relevant'].data_uri
        self.frontier_data = CRAWLS_PATH + datasources['frontier'].data_uri

        self.sort = sort

        super(Domain, self).__init__(plot)


    def update_source(self):

        # Relevant
        df = pd.read_csv(self.relevant_data, delimiter='\t', header=None, names=['url', 'timestamp'])
        df['domain'] = df['url'].apply(partial(get_tld, fail_silently=True))
        df1 = df.groupby(['domain']).size()

        # Crawled
        df = pd.read_csv(self.crawled_data, delimiter='\t', header=None, names=['url', 'timestamp'])
        df['domain'] = df['url'].apply(partial(get_tld, fail_silently=True))
        df2 = df.groupby(['domain']).size()

        # Frontier
        df = pd.read_csv(self.frontier_data, delimiter='\t', header=None, names=['url'])
        df['domain'] = df['url'].apply(partial(get_tld, fail_silently=True))
        df3 = df.groupby(['domain']).size()

        df = pd.concat((df1, df2, df3), axis=1)
        df.columns = ['relevant', 'crawled', 'frontier']

        df = df.sort(self.sort, ascending=False).head(25).fillna(value=0)

        for col in df.columns:
            df['%s_half' % col] = df[col] / 2

        df.reset_index(inplace=True)

        source = into(ColumnDataSource, df)
        return source

    def create(self):

        self.source = self.update_source()

        xdr = DataRange1d(sources=[self.source.columns("crawled")])
        if self.sort == "frontier":
            xdr.sources.append(self.source.columns("frontier"))

        p = figure(plot_width=400, plot_height=400,
            title="Domains Sorted by %s" % self.sort, x_range = xdr,
            y_range = FactorRange(factors=self.source.data['index']),
            tools='reset, resize, save')

        if self.sort == 'frontier':
            p.rect(y='index', x='frontier_half', height=0.75, width='frontier',
                   color=LIGHT_GRAY, source = self.source, legend="frontier")
        p.rect(y='index', x='crawled_half', height=0.75, width='crawled',
               color=DARK_GRAY, source = self.source, legend="crawled")
        p.rect(y='index', x='relevant_half', height=0.75, width='relevant',
               color=GREEN, source = self.source, legend="relevant")

        p.ygrid.grid_line_color = None
        p.xgrid.grid_line_color = '#8592A0'
        p.axis.major_label_text_font_size = "8pt"

        # Save ColumnDataSource model id to database model 
        self.plot.source_id = self.source._id
        db.session.flush()
        db.session.commit()
        
        script, div = components(p, INLINE)

        return (script, div)
