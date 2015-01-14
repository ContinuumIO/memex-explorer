from . import app, db
import os
from .models import Project, Crawl, Image, DataSource, Plot, DataModel, ImageSpace
from webhelpers import text

MATCHES = app.MATCHES

def get_project(project_slug):
    """Return the project identified by `project_slug`.
    """
    return Project.query.filter_by(slug=project_slug).first()


def get_crawl(project, crawl_slug):
    """Return the crawl from the project that matches the `crawl_slug`.
    """
    return Crawl.query.filter_by(project_id=project.id, slug=crawl_slug).first()

def get_crawl_by_id(crawl_id):
    """Return the crawl that matches `crawl_id`.
    """
    return Crawl.query.filter_by(id=crawl_id).first()



def get_crawls(project_id):
    """Return all crawls that match `project_id`.
    """
    return Crawl.query.filter_by(project_id=project_id)


def get_models():
    """
    Return all models that match 'project_id'
    """
    return DataModel.query.all()


def get_model(**kwargs):
    if 'name' in kwargs:
        return DataModel.query.filter_by(name=kwargs['name']).first()
    elif 'id' in kwargs:
        return DataModel.query.filter_by(id=kwargs['id']).first()
    else:
        raise Exception("Must supply either a record name or ID.")


def get_images(image_space_slug):
    """Return all images from an image space.
    """
    image_space = ImageSpace.query.filter_by(slug=image_space_slug).first()
    return image_space.images


def get_data_source(crawl, data_source_name):
    """Return the data source from a crawl by `data_source_name`.
    """
    data_source = DataSource.query.filter_by(name=data_source_name, crawl_id=crawl.id).first()

    return data_source


def get_plot(crawl, plot_name):
    """Return the plot from a crawl by name.
    """
    return Plot.query.filter_by(crawl_id=crawl.id, name=plot_name).first()


def get_image_in_image_space(image_space, image_name):
    """Return an image from an image_space that matches `image_name`.
    """
    image= Image.query.filter_by(filename=image_name).first()
    return image


def get_image(image_name):
    """Return the image that matches `image_name`.
    """
    return Image.query.filter_by(filename=image_name).first()


def get_crawl_model(crawl):
    """Return the page classifier model used by that crawl.
    """
    return DataModel.query.filter_by(id=crawl.data_model_id).first()

def set_crawl_status(crawl, status):
    crawl.status = status
    db.session.flush()
    db.session.commit()

def get_image_space(project_id):
    return ImageSpace.query.filter_by(project_id=project_id)


def get_image_space_from_name(image_space_name):
    """Return the image space that matches `image_space_name`
    """
    return ImageSpace.query.filter_by(name=image_space_name).first()


def get_crawl_image_space(project, crawl):
    """Return the image_space of a crawl. If it doesn't exist, add it to the db.
    """
    image_space = ImageSpace.query.filter_by(slug=crawl.slug, project_id=project.id).first()

    if image_space is None:
        image_space = ImageSpace(project_id=project.id,
                                 name=crawl.name,
                                 slug=crawl.slug,
                                 crawl_id=crawl.id
                                )

        db.session.add(image_space)
        db.session.commit()

    return image_space


def get_matches(project_id, image_name):
    """Return all images under `project_id` that match metadata on `image_id`.
    """
    img = get_image(image_name)
    if img.EXIF_BodySerialNumber is not None:
        return Image.query.filter_by(EXIF_BodySerialNumber=img.EXIF_BodySerialNumber).all()
    else:
        return ()


def db_add_model(project, name):
    model = DataModel(name=name, project_id=project.id)
    db.session.add(model)
    db.session.commit()


def db_add_crawl(project, form, seed_filename, model=None):
    try:
        data_model = model.id
    except:
        data_model = None

    if form.crawler.data == "nutch":
        # TODO check if "/" is necessary
        seed_list = text.urlify(form.name.data) + "/"
    elif form.crawler.data == "ache":
        seed_list = seed_filename
    else:
        seed_list = "None"

    crawl = Crawl(name=form.name.data,
                  description=form.description.data,
                  crawler=form.crawler.data,
                  project_id=project.id,
                  data_model_id=data_model,
                  config = 'config_default',
                  seeds_list = seed_list,
                  slug=text.urlify(form.name.data),
                  status="Crawl has not been started")

    db.session.add(crawl)
    db.session.commit()
    return crawl


def db_init_ache(project, crawl):
    """ When an ache crawl is registered, we need to add in the database: the data sources associated with that
    crawl (crawledpages, relevantpages and frontierpages), and the plots that are going to be available for that crawl
    (domain and harvest).
    """
    crawled_data_uri = 'data_monitor/crawledpages.csv'
    crawled_data = DataSource(name='crawledpages',
                              data_uri=crawled_data_uri,
                              project_id=project.id)

    relevant_data_uri = 'data_monitor/relevantpages.csv'
    relevant_data = DataSource(name='relevantpages',
                               data_uri=relevant_data_uri,
                               project_id=project.id)

    frontier_data_uri = 'data_monitor/frontierpages.csv'
    frontier_data = DataSource(name='frontierpages',
                               data_uri=frontier_data_uri,
                               project_id=project.id)

    harvest_data_uri = 'data_monitor/harvestinfo.csv'
    harvest_data = DataSource(name='harvest',
                              data_uri=harvest_data_uri,
                              project_id=project.id)

    crawl.data_sources.append(crawled_data)
    crawl.data_sources.append(relevant_data)
    crawl.data_sources.append(frontier_data)
    crawl.data_sources.append(harvest_data)

    db.session.add(crawled_data)
    db.session.add(relevant_data)
    db.session.add(frontier_data)
    db.session.add(harvest_data)

    # Add domain plot to db
    domain_plot = Plot(name='domain',
                       project_id=project.id,
                       crawl_id=crawl.id,
                       )

    # Add harvest plot to db
    harvest_plot = Plot(name='harvest',
                        project_id=project.id,
                        crawl_id=crawl.id,
                        )

    crawled_data.plots.append(domain_plot)
    relevant_data.plots.append(domain_plot)
    frontier_data.plots.append(domain_plot)

    harvest_data.plots.append(harvest_plot)

    db.session.add(domain_plot)
    db.session.add(harvest_plot)
    db.session.commit()


def db_process_exif(exif_data, img_path, filename, image_space):
    """ Store the EXIF data from the image in the db"""
    if not Image.query.filter_by(filename=filename).first():
        LSVN = getattr(exif_data.get('EXIF LensSerialNumber'), 'values', None)
        MSNF = getattr(exif_data.get('MakerNote SerialNumberFormat'), 'values', None)
        BSN = getattr(exif_data.get('EXIF BodySerialNumber'), 'values', None)
        MISN = getattr(exif_data.get('MakerNote InternalSerialNumber'), 'values', None)
        MSN = getattr(exif_data.get('MakerNote SerialNumber'), 'values', None)
        IBSN = getattr(exif_data.get('Image BodySerialNumber'), 'values', None)

        image = Image(filename=filename,
                      EXIF_LensSerialNumber=LSVN,
                      MakerNote_SerialNumberFormat=MSNF,
                      EXIF_BodySerialNumber=BSN,
                      MakerNote_InternalSerialNumber=MISN,
                      MakerNote_SerialNumber=MSN,
                      Image_BodySerialNumber=IBSN,
                      uploaded=0)

        image_space.images.append(image)
        # Add uploaded image to the database
        db.session.add(image)
        db.session.commit()


def set_match(source_id, match_id, match):
    if match:
        MATCHES.add((source_id, match_id))

    elif not match:
        MATCHES.remove((source_id, match_id))


def get_uploaded_image_names():
    upload_dir = app.config['UPLOAD_DIR']
    ret_list = os.listdir(upload_dir)
    return ret_list
