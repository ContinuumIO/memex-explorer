from __future__ import division
import csv
import sys
from blaze import *
import pandas as pd
from bokeh.plotting import *
from bokeh.objects import HoverTool
from collections import OrderedDict
import numpy as np
import os
import datetime as dt
from bokeh.embed import components
from bokeh.resources import CDN
from time import sleep

class Harvest(object):

    def __init__(self, input_data='harvestinfo.csv'):
        self.harvest_data = input_data
        self.source = self.update_source()
        self.current = os.path.getmtime(input_data)
        #self.plot, self.rate_plot = self.create_plot()

    def update_source(self):
        t = Data(CSV(self.harvest_data, columns=['relevant_pages', 'downloaded_pages', 'timestamp']))
        t = transform(t, timestamp=t.timestamp.map(dt.datetime.fromtimestamp, schema='datetime'))
        t = transform(t, date=t.timestamp.map(lambda x: x.date(), schema='date'))
        t = transform(t, harvest_rate=t.relevant_pages/t.downloaded_pages)

        source = into(ColumnDataSource, t)

        return source

    def create_plot_harvest(self):

        figure(plot_width=500, plot_height=250, title="Harvest Plot", tools='pan, wheel_zoom, box_zoom, reset, resize, save, hover', x_axis_type='datetime')
        hold()

        scatter(x="timestamp", y="relevant_pages", fill_alpha=0.6, color="red", source=self.source)
        line(x="timestamp", y="relevant_pages", color="red", width=0.2, legend="relevant", source=self.source)
        scatter(x="timestamp", y="downloaded_pages", fill_alpha=0.6, color="blue", source=self.source)
        line(x="timestamp", y="downloaded_pages", color="blue", width=0.2, legend="downloaded", source=self.source)

        hover = curplot().select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ("harvest_rate", "@harvest_rate"),
        ])

        legend().orientation = "top_left"

        harvest_plot = curplot()

        harvest = components(harvest_plot, CDN)
        
        return harvest

    def create_plot_harvest_rate(self):

        figure(plot_width=500, plot_height=250, title="Harvest Rate", x_axis_type='datetime', tools='pan, wheel_zoom, box_zoom, reset, resize, save, hover')
        line(x="timestamp", y="harvest_rate", fill_alpha=0.6, color="blue", width=0.2, legend="harvest_rate", source=self.source)
        scatter(x="timestamp", y="harvest_rate", alpha=0, color="blue", legend="harvest_rate", source=self.source)

        hover = curplot().select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ("harvest_rate", "@harvest_rate"),
        ])

        harvest_rate_plot = curplot()

        harvest_rate = components(harvest_rate_plot, CDN)

        return harvest_rate

    def create_and_push(self, doc_name='harvest'):

        output_server(doc_name)
        figure(plot_width=500, plot_height=250, title="Harvest Plot", tools='pan, wheel_zoom, box_zoom, reset, resize, save, hover', x_axis_type='datetime')
        hold()

        scatter(x="timestamp", y="relevant_pages", fill_alpha=0.6, color="red", source=self.source)
        line(x="timestamp", y="relevant_pages", color="red", width=0.2, legend="relevant", source=self.source)
        scatter(x="timestamp", y="downloaded_pages", fill_alpha=0.6, color="blue", source=self.source)
        line(x="timestamp", y="downloaded_pages", color="blue", width=0.2, legend="downloaded", source=self.source)

        hover = curplot().select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ("harvest_rate", "@harvest_rate"),
        ])

        legend().orientation = "top_left"
        push()

    def keep_pushing(self):

        while True:
            sleep(1)
            if self.current != os.path.getmtime(self.harvest_data):
                print('changed!!')
                t = Data(CSV(self.harvest_data, columns=['relevant_pages', 'downloaded_pages', 'timestamp']))
                t = transform(t, timestamp=t.timestamp.map(dt.datetime.fromtimestamp, schema='datetime'))
                t = transform(t, date=t.timestamp.map(lambda x: x.date(), schema='date'))
                t = transform(t, harvest_rate=t.relevant_pages/t.downloaded_pages)

                source = into(ColumnDataSource, t)
                push()



