from . import app, db 
import os
from .config import SEED_FILES, CONFIG_FILES, MODEL_FILES, CRAWLS_PATH
from .models import (Project, Crawl, Dashboard, Image,
                     DataSource, Plot, DataModel, ImageSpace)

MATCHES = app.MATCHES

def get_project(project_slug):
    """Return the project identified by `project_slug`.
    """
    return Project.query.filter_by(slug=project_slug).first()


def get_crawl(crawl_slug):
    """Return the first crawl that matches `crawl_name`.
    """
    return Crawl.query.filter_by(slug=crawl_slug).first()


def get_crawls(project_id):
    """Return all crawls that match `project_id`.
    """
    return Crawl.query.filter_by(project_id=project_id)


def get_dashboards(project_id):
    """Return all dashboards that match `project_id`.
    """
    return Dashboard.query.filter_by(project_id=project_id)


def get_models():
    """
    Return all models that match 'project_id'
    """
    return DataModel.query.all()


def get_images():
    """Return all images under `project_id` that match `crawl_name`.
    """
    # TODO change to query by image_space. Requires db changes.
    return Image.query.all()


def get_data_source(project_id, data_source_name):
    """Return the data source under `project_id` that matches `data_source_name`.
    """
    return DataSource.query.filter_by(project_id=project_id, name=data_source_name).first()


def get_plot(plot_name):
    """Return the plot that matches `plot_name`.
    """
    return Plot.query.filter_by(name=plot_name).first()

def get_image(image_name):
    """Return the image that matches `image_id`.
    """
    # TODO query just in that image_space
    return Image.query.filter_by(img_file=image_name).first()


def get_crawl_model(crawl):
    """Return the page classifier model used by that crawl.
    """
    return DataModel.query.filter_by(id=crawl.data_model_id).first()


def get_image_space(project_id):
    return ImageSpace.query.filter_by(project_id=project_id)


def get_matches(project_id, image_name):
    """Return all images under `project_id` that match metadata on `image_id`.
    """

    img = get_image(image_name)
    return Image.query.filter_by(EXIF_BodySerialNumber=img.EXIF_BodySerialNumber).all()


#def get_images_in_space(project_slug, image_space_slug):
#     """Return all images under `project_id` that match metadata on `image_id`.
#    """
#    # TODO modify db model so we have a link between image and image_space
#     return


def db_add_crawl(project, form, seed_filename):
    crawl = Crawl(name=form.name.data,
                  description=form.description.data,
                  crawler=form.crawler.data,
                  project_id=project.id,
                  data_model_id=form.data_model.data.id,
                  config = os.path.join(CONFIG_FILES,'config_default'),
                  seeds_list = SEED_FILES + seed_filename)

    db.session.add(crawl)
    db.session.commit()
    return crawl


def db_init_ache(project, crawl):
    key = project.slug + '-' + crawl.name
    crawled_data_uri = os.path.join(CRAWLS_PATH, crawl.name, 'data/data_monitor/crawledpages.csv')
    crawled_data = DataSource(name=key + '-crawledpages',
                              data_uri=crawled_data_uri,
                              project_id=project.id)

    relevant_data_uri = os.path.join(CRAWLS_PATH, crawl.name, 'data/data_monitor/relevantpages.csv')
    relevant_data = DataSource(name=key + '-relevantpages',
                               data_uri=relevant_data_uri,
                               project_id=project.id,
                               crawl=crawl)

    frontier_data_uri = os.path.join(CRAWLS_PATH, crawl.name, 'data/data_monitor/frontierpages.csv')
    frontier_data = DataSource(name=key + '-frontierpages',
                               data_uri=frontier_data_uri,
                               project_id=project.id,
                               crawl=crawl)

    harvest_data_uri = os.path.join(CRAWLS_PATH, crawl.name, 'data/data_monitor/harvestinfo.csv')
    harvest_data = DataSource(name=key + '-harvestinfo',
                               data_uri=harvest_data_uri,
                               project_id=project.id,
                               crawl=crawl)

    crawl.data_source.append(crawled_data)
    crawl.data_source.append(relevant_data)
    crawl.data_source.append(frontier_data)
    crawl.data_source.append(harvest_data)

    db.session.add(crawled_data)
    db.session.add(relevant_data)
    db.session.add(frontier_data)
    db.session.add(harvest_data)

    # Add domain plot to db
    domain_plot = Plot(name=key + '-' + 'domain',
                       project_id=project.id,
                       )

    # Add harvest plot to db
    harvest_plot = Plot(name=key + '-' + 'harvest',
                        project_id=project.id,
                        )

    crawled_data.plots.append(domain_plot)
    relevant_data.plots.append(domain_plot)
    frontier_data.plots.append(domain_plot)

    harvest_data.plots.append(harvest_plot)

    db.session.add(domain_plot)
    db.session.add(harvest_plot)
    db.session.commit()


def set_match(source_id, match_id, match):
    if match:
        MATCHES.add((source_id, match_id))

    elif not match:
        MATCHES.remove((source_id, match_id))
