from __future__ import absolute_import

import os
import traceback

from .viz.domain import Domain
from .viz.harvest import Harvest

from .config import CRAWLS_PATH

from .db_api import (get_plot, get_data_source)

PLOT_NAMES = ('Domain Relevance',
              'Domain Crawled',
              'Domain Frontier',
              'Harvest',
              'Harvest Rate',
              'Termite')

PLOT_TYPES = ('domain_by_relevance',
              'domain_by_crawled',
              'domain_by_frontier',
              'harvest',
              'harvest_rate',
              'termite')

class PlotsNotReadyException(Exception):
    pass 


def default_ache_dash(crawl):
    ### Domain
    domain_plot = get_plot(crawl, "domain")

    crawled = get_data_source(crawl, "crawledpages")
    relevant = get_data_source(crawl, "relevantpages")
    domain_sources = dict(crawled=crawled, relevant=relevant)

    if not all(os.path.exists(CRAWLS_PATH + x.data_uri) for x in domain_sources.values()):
        raise PlotsNotReadyException("Domain sources are not initialized.")

    try:
        domain = Domain(domain_sources, domain_plot)
        domain_script, domain_div = domain.create()
    except Exception as e:
        traceback.print_exc()
        raise PlotsNotReadyException("Unknown error (domain).")
    ###


    ### Harvest
    harvest_plot = get_plot(crawl, "harvest")

    harvest_source = get_data_source(crawl, "harvest")
    if not os.path.exists(os.path.join(CRAWLS_PATH, crawl.id, harvest_source.data_uri)):
        raise PlotsNotReadyException("Harvest source is not initialized.")

    try:
        harvest = Harvest(harvest_source, harvest_plot)
        harvest_script, harvest_div  = harvest.create()
    except Exception as e:
        traceback.print_exc()
        raise PlotsNotReadyException("Unknown error (harvest).")
    ###

    scripts = (domain_script, harvest_script)
    divs = (domain_div, harvest_div)

    return scripts, divs
