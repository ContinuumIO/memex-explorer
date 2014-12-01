from __future__ import absolute_import

from .viz.domain import Domain
from .viz.harvest import Harvest
from .viz.termite import Termite    
from .models import DataSource

def plot_builder(crawl, plot):

    if plot.plot == 'domain_by_relevance':
        data = DataSource.query.filter_by(crawl_id=crawl.id)
        crawled_uri = data.filter_by(name='crawledpages').first().data_uri
        relevant_uri = data.filter_by(name='relevantpages').first().data_uri
        frontier_uri = data.filter_by(name='frontierpages').first().data_uri
        d = Domain(crawled=crawled_uri, relevant=relevant_uri, frontier=frontier_uri)
        script, div = d.create_plot_relevant()        

    if plot.plot == 'domain_by_crawled':
        data = DataSource.query.filter_by(crawl_id=crawl.id)
        crawled_uri = data.filter_by(name='crawledpages').first().data_uri
        relevant_uri = data.filter_by(name='relevantpages').first().data_uri
        frontier_uri = data.filter_by(name='frontierpages').first().data_uri
        d = Domain(crawled=crawled_uri, relevant=relevant_uri, frontier=frontier_uri)
        script, div = d.create_plot_crawled()

    if plot.plot == 'domain_by_frontier':
        data = DataSource.query.filter_by(crawl_id=crawl.id)
        crawled_uri = data.filter_by(name='crawledpages').first().data_uri
        relevant_uri = data.filter_by(name='relevantpages').first().data_uri
        frontier_uri = data.filter_by(name='frontierpages').first().data_uri
        d = Domain(crawled=crawled_uri, relevant=relevant_uri, frontier=frontier_uri)
        script, div = d.create_plot_frontier()

    if plot.plot == 'harvest':
        data = DataSource.query.filter_by(crawl_id=crawl.id)
        harvest = data.filter_by(name='harvest').first().data_uri
        d = Harvest(harvest)
        script, div = d.create_plot_harvest()

    if plot.plot == 'harvest_updating':
        data = MonitorData.query.filter_by(crawl_id=crawl.id)
        harvest = data.filter_by(name='harvest').first().data_uri
        d = Harvest(input_data=harvest, crawl=crawl.name)
        script, div = ('', d.create_and_push())
        print "Launched child with pid %s" % d.launch_pusher()

    if plot.plot == 'harvest_rate':
        data = DataSource.query.filter_by(crawl_id=crawl.id)
        harvest = data.filter_by(name='harvest').first().data_uri
        d = Harvest(harvest)
        script, div = d.create_plot_harvest_rate()

    if plot.name == 'termite':
        data = DataSource.query.filter_by(crawl_id=crawl.id)
        termite = data.filter_by(name='termite').first().data_uri
        t =  Termite(termite)
        script, div = t.create_plot()

    return script, div