from __future__ import division
from __future__ import print_function

from datetime import datetime
import json
from Queue import Empty

import numpy as np
from bokeh.plotting import figure, output_server
from kombu import Exchange, Connection, Queue

from bokeh.models.glyphs import Segment
from bokeh.models.markers import Circle
from bokeh.models import Range1d, ColumnDataSource
from bokeh.models.grids import Grid
from bokeh.embed import autoload_server
from bokeh.session import Session
from bokeh.document import Document

from django.conf import settings
EXTERNAL_APP_LOCATIONS = settings.EXTERNAL_APP_LOCATIONS
VIRTUAL_HOST = settings.VIRTUAL_HOST

DEFAULT_NUM_URLS = 25
URL_CHAR_WIDTH = 50
EXCHANGE_NAME = "fetcher_log"
PLOT_CIRCLES = False

def init_plot(crawl_name):
    session = Session()
    document = Document()
    session.use_doc(crawl_name)
    session.load_document(document)

    if document.context.children:
        plot = document.context.children[0]
    else:
        output_server(crawl_name)
        # TODO: Remove these when Bokeh is upgraded
        # placeholders or Bokeh can't inject properly
        current = np.datetime64(datetime.now())
        xdr = Range1d(current, current + 1)
        ydr = ["urls"]

        # styling suggested by Bryan
        plot = figure(title="Crawler Monitor", tools="hover",
                      x_axis_type="datetime", y_axis_location="right", x_range=xdr, y_range=ydr,
                      width=1200, height=600)
        plot.toolbar_location = None
        plot.xgrid.grid_line_color = None

        # temporarily turn these off
        plot.ygrid.grid_line_color = None
        plot.xaxis.minor_tick_line_color = None
        plot.xaxis.major_tick_line_color = None
        plot.xaxis.major_label_text_font_size = '0pt'
        plot.yaxis.minor_tick_line_color = None
        plot.yaxis.major_tick_line_color = None
        plot.yaxis.major_label_text_font_size = '0pt'

    document.add(plot)
    session.store_document(document)
    script = autoload_server(plot, session)

    #TODO: Looks like a Bokeh bug, probably not repeatable with current code
    script = script.replace("'modelid': u'", "'modelid': '")

    if VIRTUAL_HOST != "localhost":
        script = script.replace('http://localhost:5006', EXTERNAL_APP_LOCATIONS['bokeh-server'])
    return script


class NutchUrlTrails:
    """
    Class for managing URL Trails visualizations
    """

    @staticmethod
    def strip_url(url):
        """
        Make a URL safe for visualization in Bokeh server
        :param url: a URL to be shortened/stripped
        :return: The stripped URL
        """
        # TODO: remove protocol-stripping on next Bokeh release
        stripped_url = url.replace('https://', '').replace('http://', '').replace(':', '_').replace('-', '_')

        if len(stripped_url) <= URL_CHAR_WIDTH:
            return stripped_url
        else:
            return stripped_url[:int(URL_CHAR_WIDTH/2)] + '...' + stripped_url[-int(URL_CHAR_WIDTH/2)-3:]

    @staticmethod
    def jtime_to_datetime(t):
        """
        Convert a Java-format Epoch time stamp into np.datetime64 object
        :param t: Java-format Epoch time stamp (milliseconds)
        :return: A np.datetime64 scalar
        """
        return np.datetime64(datetime.fromtimestamp(t/1000.0))

    def __init__(self, crawl_name, num_urls=DEFAULT_NUM_URLS):
        """
        Create a NutchUrlTrails instance for visualizing a running Nutch crawl in real-time using Bokeh
        :param name: The name of the crawl (as identified by the queue)
        :param num_urls: The number of URLs to display in the visualization
        :return: A NutchUrLTrails instance
        """
        self.crawl_name = crawl_name
        self.num_urls = num_urls
        self.open_urls = {}
        self.closed_urls = {}
        self.old_segments = None
        self.old_circles = None
        
        self.session = Session()
        self.session.use_doc(self.crawl_name)
        self.document = Document()

        con = Connection()

        exchange = Exchange(EXCHANGE_NAME, 'direct', durable=False)
        queue = Queue(crawl_name, exchange=exchange, routing_key=crawl_name)
        self.queue = con.SimpleQueue(name=queue)

    def handle_messages(self):
        """
        Get and parse up to 250 messages from the queue then plot.  Break early if less.
        """

        for i in range(250):
            try:
                m = self.queue.get(block=True, timeout=1)
                self.parse_message(m)
            except Empty:
                break
        self.plot_urls()

    def parse_message(self, message):
        """
        Parse a single message arriving from the queue.  Updates list of open/closed urls.
        :param message: A message from the queue
        """
        print(message.body)
        message = json.loads(message.body)
        url = message["url"]
        if message["eventType"] == "START":
            self.open_urls[url] = NutchUrlTrails.jtime_to_datetime(message["timestamp"])
        elif message["eventType"] == "END":
            if url in self.open_urls:
                self.closed_urls[url] = (self.open_urls[url], NutchUrlTrails.jtime_to_datetime(message["timestamp"]))
                del self.open_urls[url]
            else:
                # TODO: Log mismatched messages instead of just swallowing them
                pass
        else:
            raise Exception("Unexpected message type")

    def plot_urls(self):
        """
        Visualize crawler activity by showing the most recently crawled URLs and the fetch time.
        """

        self.session.load_document(self.document)
        plot = self.document.context.children[0]

        # don't plot if no URLs available
        if not (self.open_urls or self.closed_urls):
            return

        # x0/x0, left and right boundaries of segments, correspond to fetch time
        x0 = []
        x = []
        # y-axis, name of URL being fetched
        urls = []

        # maintain x and URL of circles in a separate list
        circles = []
        circle_urls = []

        current_time = np.datetime64(datetime.now())

        # For open URLs (not completed fetching), draw a segment from start time to now
        for url, start_t in self.open_urls.items():
            url = NutchUrlTrails.strip_url(url)
            x0.append(start_t)
            x.append(current_time)
            urls.append(url)

        # For closed URLs (completed fetching), draw a segment from start to end time, and a circle as well.
        for url, (start_t, end_t) in self.closed_urls.items():
            url = NutchUrlTrails.strip_url(url)
            x0.append(start_t)
            x.append(end_t)
            circles.append(end_t)
            urls.append(url)
            circle_urls.append(url)

        x0 = np.asarray(x0)
        x = np.asarray(x)
        circles = np.asarray(circles)

        # sort segments
        sort_index = np.argsort(x0)[::-1]
        x0 = x0[sort_index]
        x = x[sort_index]
        urls = [urls[i] for i in sort_index]

        # sort circles
        if self.closed_urls:
            circle_sort_index = np.argsort(circles)[::-1]
            circles = circles[circle_sort_index]
            circle_urls = [circle_urls[i] for i in circle_sort_index]

        # Filter to latest num_url URLs (ascending order)
        # filter segments
        active_x0 = x0[:self.num_urls]
        active_x = x[:self.num_urls]
        active_urls = urls[:self.num_urls]

        min_x = min(active_x0)
        plot.x_range.start = min_x
        plot.x_range.end = np.datetime64(datetime.now())
        plot.y_range.factors = active_urls

        # make sure these are turned back on!
        # turn y axis grid lines back on
        for r in plot.renderers:
            if type(r) == Grid:
                r.grid_line_color = 'black'
                break

        # turn tickers and their labels back on
        plot.right[0].minor_tick_line_color = 'black'
        plot.right[0].major_tick_line_color = 'black'
        plot.right[0].major_label_text_font_size = '12pt'
        plot.below[0].minor_tick_line_color = 'black'
        plot.below[0].major_tick_line_color = 'black'
        plot.below[0].major_label_text_font_size = '12pt'

        # TODO: Find a more correct way to remove old segment/circle glyphs
        if self.old_circles:
            plot.renderers.pop()
            self.old_circles = None
        if self.old_segments:
            plot.renderers.pop()
            self.old_segments = None

        segment_source = ColumnDataSource(dict(x0=active_x0,
                                               x1=active_x,
                                               urls=active_urls))

        self.old_segments = Segment(x0="x0", y0="urls", x1="x1", y1="urls", line_color="orange", line_width=10)
        plot.add_glyph(segment_source, self.old_segments)

        if self.closed_urls and PLOT_CIRCLES:
            # filter circles (some of these might not be displayed)
            active_circles = circles[:self.num_urls]
            active_circle_urls = circle_urls[:self.num_urls]

            circle_source = ColumnDataSource(dict(x=active_circles, urls=active_circle_urls))

            self.old_circles = Circle(x="x", y="urls", size=12, fill_color="green", line_color="orange", line_width=2)
            plot.add_glyph(circle_source, self.old_circles)

        self.session.store_document(self.document, dirty_only=False)
