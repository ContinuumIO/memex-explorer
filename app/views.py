"""Main views for memex-explorer application"""
from __future__ import absolute_import, division, print_function

#  IMPORTS
# =========

# Standard Library
# ----------------

import os
import logging
import json
import datetime as dt
import subprocess
import traceback
import shutil

# Third-party Libraries
# ---------------------

from flask import (redirect, flash, render_template, request, url_for,
                   send_from_directory, jsonify, session, abort)
from werkzeug import secure_filename
from webhelpers import text

from blaze import resource, discover, Data, into, compute
from pandas import DataFrame
from bokeh.plotting import ColumnDataSource

import exifread

# Local Imports
# -------------

from . import app, db

from .config import (ADMINS, DEFAULT_MAIL_SENDER, BASEDIR, SEED_FILES, 
                     CONFIG_FILES, MODEL_FILES, CRAWLS_PATH, IMAGE_SPACE_PATH,
                     UPLOAD_DIR)

from .mail import send_email
from .auth import requires_auth
from .models import (Crawl, DataSource, Plot, Project, Image,
                     ImageSpace, DataModel)
from .utils import make_dir
from .db_api import (get_project, get_crawl, get_crawls, get_data_source,
                     get_images, get_image, get_matches, db_add_crawl, get_plot,
                     db_init_ache, get_crawl_model, get_model, get_models, get_crawl_image_space,
                     db_process_exif, get_image_space, db_add_model, get_uploaded_image_names, get_image_in_image_space,
                     get_image_space_from_name)

from .forms import (CrawlForm, MonitorDataForm, PlotForm, ContactForm,
                    DashboardForm, ProjectForm, DataModelForm, EditProjectForm,
                    EditCrawlForm)

from .crawls import AcheCrawl, NutchCrawl

from .plotting import default_ache_dash, PlotsNotReadyException
from .viz.domain import Domain
from .viz.harvest import Harvest

from .images import allowed_file, lost_camera_retreive, image_retrieve, serve_upload_page, process_exif

# Dictionary of crawls by key(project_slug-crawl_name)
CRAWLS = {}


@app.context_processor
def context():
    """Inject some context variables useful across templates.
    See http://flask.pocoo.org/docs/0.10/templating/#context-processors
    """

    context_vars = {}

    if request.view_args and 'project_slug' in request.view_args:
        project_slug = request.view_args['project_slug']
        project = get_project(project_slug)
        if not project:
            return {}
            # flash("Project '%s' was not found." % project_slug, 'error')
            # abort(404)

        crawls = get_crawls(project.id)
        models = get_models()
        image_spaces = get_image_space(project.id)


        context_vars.update(dict(
            project=project, crawls=crawls, \
            models=models, image_spaces=image_spaces))

    # All pages should (potentially) be able to present all projects
    context_vars.update(projects=Project.query.all())

    return context_vars


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def application_error(e):
    # TODO
    # http://flask.pocoo.org/docs/0.10/errorhandling/#application-errors

    # sender = DEFAULT_MAIL_SENDER
    # send_email(subject=subject, sender=sender, recipients=ADMINS, text_body=text_body, html_body=text_body)
    return render_template('500.html'), 500


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(BASEDIR, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about/')
def about_page():
    return render_template('about.html')


# Project
# -----------------------------------------------------------------------------

@app.route('/<project_slug>')
def project(project_slug):

    # return render_template('project.html', project=project, crawls=crawls,
    #                                        dashboards=dashboards)

    # `project`, `crawls`, and `dashboards` handled by the context processor.
    #   See `context() defined above.`
    return render_template('project.html')


@app.route('/<project_slug>/delete', methods=['POST'])
def delete_project(project_slug):
    project = get_project(project_slug)
    db.session.delete(project)
    db.session.commit()
    flash('%s has successfully been deleted.' % project.name, 'success')
    return redirect(url_for('index'))


@app.route('/<project_slug>/edit', methods=['POST', 'GET'])
def edit_project(project_slug):
    form = EditProjectForm()
    project = get_project(project_slug)
    original_name = project.slug
    if form.validate_on_submit():
        if form.name.data:
            project.name = form.name.data
            project.slug = text.urlify(form.name.data)
        if form.description.data:
            project.description = form.description.data
        if form.icon.data:
            project.icon = form.icon.data
        db.session.commit()
        flash('%s has successfully been edited.' % original_name, 'success')
        return redirect(url_for('index'))
    return render_template("edit_project.html", form=form)


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    form = ProjectForm(request.form)

    if form.validate_on_submit():
        existing_project = get_project(text.urlify(form.name.data))
        if existing_project:
            flash("Project '%s' already exists" % existing_project.name, 'error')
            return redirect(url_for('add_project'))
        project = Project(slug=text.urlify(form.name.data),
                          name=form.name.data,
                          description=form.description.data,
                          icon=form.icon.data)
        db.session.add(project)
        db.session.commit()
        flash("Project '%s' was successfully registered" % project.name, 'success')
        return redirect(url_for('project', project_slug=project.slug))

    return render_template('add_project.html', form=form)


# Crawl
# -----------------------------------------------------------------------------

@app.route('/<project_slug>/add_crawl', methods=['GET', 'POST'])
def add_crawl(project_slug):
    form = CrawlForm()
    project = get_project(project_slug)
    if form.validate_on_submit():
        existing_crawl = Crawl.query.filter_by(slug=text.urlify(form.name.data)).first()
        if existing_crawl:
            flash('Crawl name already exists, please choose another name', 'error')
            return render_template('add_crawl.html', form=form)
        if form.new_model_name.data:
            registered_model = DataModel.query.filter_by(name=form.new_model_name.data).first()
            if registered_model:
                flash('Data model name already exists, please choose another name', 'error')
                return render_template('add_crawl.html', form=form)
            db_add_model(project, form.new_model_name.data)
            model = get_model(name=form.new_model_name.data)
            model_directory = MODEL_FILES + str(model.id)
            make_dir(model_directory)
            model_file = secure_filename(form.new_model_file.data.filename)
            model_features = secure_filename(form.new_model_features.data.filename)
            form.new_model_file.data.save(model_directory + '/' + model_file)
            form.new_model_features.data.save(model_directory + '/' + model_features)
        elif form.data_model.data:
            model = get_model(id=form.data_model.data.id)
        else:
            model = None
        seed_filename = secure_filename(form.seeds_list.data.filename)
        if form.crawler.data == "ache":
            form.seeds_list.data.save(SEED_FILES + seed_filename)
        elif form.crawler.data == "nutch":
            seed_folder = text.urlify(form.name.data)
            subprocess.Popen(['mkdir', os.path.join(SEED_FILES, seed_folder)]).wait()
            form.seeds_list.data.save(os.path.join(SEED_FILES, seed_folder, seed_filename))
        # TODO allow upload configuration
        #config_filename = secure_filename(form.config.data.filename)
        #form.config.data.save(CONFIG_FILES + config_filename)
        crawl = db_add_crawl(project, form, seed_filename, model)
        subprocess.Popen(['mkdir', os.path.join(CRAWLS_PATH, str(crawl.id))]).wait()

        if crawl.crawler == 'ache':
            db_init_ache(project, crawl)

        else:
            #TODO add db_init_nutch
            pass

        flash('%s has successfully been registered!' % form.name.data, 'success')
        return redirect(url_for('crawl', project_slug=project.slug,
                                         crawl_slug=crawl.slug))
    else:
        print(form.errors)

    return render_template('add_crawl.html', form=form)


@app.route('/<project_slug>/crawls')
def crawls(project_slug):
    return render_template('crawls.html')


@app.route('/<project_slug>/crawls/<crawl_slug>')
def crawl(project_slug, crawl_slug):
    project = get_project(project_slug)
    crawl = get_crawl(project, crawl_slug)
    model = get_model(id=crawl.data_model_id)

    if not project:
        flash("Project '%s' was not found." % project_slug, 'error')
        abort(404)
    elif not crawl:
        flash("Crawl '%s' was not found." % crawl.name, 'error')
        abort(404)

    if crawl.crawler == 'ache':
        try:
            scripts, divs = default_ache_dash(crawl)
        except PlotsNotReadyException as e:
            traceback.print_exc()
            return render_template('crawl.html', crawl=crawl,
                status=status_crawl(project_slug, crawl_slug), model=model)


        relevant_path = url_for('relevant_pages', project_slug=project.slug,
                crawl_slug=crawl.slug)

        return render_template('crawl.html', scripts=scripts,
                status=status_crawl(project_slug, crawl_slug), divs=divs,
                crawl=crawl, model=model)

    else:
        return render_template('crawl.html', crawl=crawl,
                status=status_crawl(project_slug, crawl_slug),  model=model)


@app.route('/<project_slug>/crawls/<crawl_slug>/delete', methods=['POST'])
def delete_crawl(project_slug, crawl_slug):
    project = get_project(project_slug)
    crawl = get_crawl(project, crawl_slug)
    shutil.rmtree(os.path.join(CRAWLS_PATH + str(crawl.id)))
    db.session.delete(crawl)
    db.session.commit()
    flash('%s has successfully been deleted.' % crawl.name, 'success')
    return redirect(url_for('project', project_slug=project_slug))


@app.route('/<project_slug>/crawls/<crawl_slug>/edit', methods=['POST', 'GET'])
def edit_crawl(project_slug, crawl_slug):
    project = get_project(project_slug)
    crawl = Crawl.query.filter_by(project_id=project.id, slug=crawl_slug).first()
    form = EditCrawlForm()
    if form.validate_on_submit():
        if form.name.data:
            crawl.name = form.name.data
            crawl.slug = text.urlify(form.name.data)
        if form.description.data:
            crawl.description = form.description.data
        if form.crawler.data == 'nutch':
            crawl.crawler = form.crawler.data
            crawl.data_model_id = ''
        elif form.crawler.data == 'ache':
            crawl.crawler = form.crawler.data
        if form.seeds_list.data:
            seed_filename = secure_filename(form.seeds_list.data.filename)
            form.seeds_list.data.save(SEED_FILES + seed_filename)
            crawl.seeds_list = SEED_FILES + seed_filename
        if form.data_model.data:
            crawl.data_model_id = form.data_model.data.id
        db.session.commit()
        flash('%s has successfully been changed.' % crawl.name, 'success')
        return redirect(url_for('project', project_slug=project_slug))

    return render_template('edit_crawl.html', form=form)


@app.route('/<project_slug>/crawls/<crawl_slug>/run', methods=['POST'])
def run_crawl(project_slug, crawl_slug):
    project = get_project(project_slug)
    key = project_slug + '-' + crawl_slug
    try:
        crawl = get_crawl(project, crawl_slug)
        seeds_list = crawl.seeds_list
        if crawl.crawler == "ache":
            model = get_crawl_model(crawl)
            crawl_instance = AcheCrawl(crawl)
            pid = crawl_instance.start()
            CRAWLS[key] = crawl_instance
            return "Crawl %s running" % crawl.name
        elif crawl.crawler == "nutch":
            crawl_instance = NutchCrawl(crawl)
            pid = crawl_instance.start()
            CRAWLS[key] = crawl_instance
            return "Crawl %s running" % crawl.name
    except Exception as e:
        traceback.print_exc()
        return "Error"


@app.route('/<project_slug>/crawls/<crawl_slug>/stop', methods=['POST'])
def stop_crawl(project_slug, crawl_slug):
    key = project_slug + '-' + crawl_slug
    crawl_instance = CRAWLS.get(key)
    if crawl_instance is not None:
        crawl_instance.stop()
        return "Crawl stopped"
    else:
        return "No such crawl"


@app.route('/<project_slug>/crawls/<crawl_slug>/refresh', methods=['POST'])
def refresh(project_slug, crawl_slug):

    project = get_project(project_slug)
    crawl = get_crawl(project, crawl_slug)
    ### Domain
    crawled = get_data_source(crawl, "crawledpages")
    relevant = get_data_source(crawl, "relevantpages")
    frontier = get_data_source(crawl, "frontierpages")
    domain_plot = get_plot(crawl, "domain")
    #domain_sources = dict(crawled=crawled, relevant=relevant)
    domain_sources = dict(crawled=crawled, relevant=relevant, frontier=frontier)

    domain = Domain(domain_sources, domain_plot)
    domain.push_to_server()
    ###

    ### Harvest
    harvest_source = get_data_source(crawl, "harvest")
    harvest_plot = get_plot(crawl, "harvest")

    harvest = Harvest(harvest_source, harvest_plot)
    harvest.push_to_server()
    ###

    return "pushed"


@app.route('/<project_slug>/crawls/<crawl_slug>/status', methods=['GET'])
def status_crawl(project_slug, crawl_slug):
    key = project_slug + '-' + crawl_slug
    project = get_project(project_slug)
    crawl = get_crawl(project=project, crawl_slug=crawl_slug)
    crawl_instance = CRAWLS.get(key)
    if crawl_instance is not None:
        status = crawl_instance.get_status()
    elif crawl.crawler == "nutch":
        crawl_instance = NutchCrawl(crawl)
        status = crawl_instance.get_status()
    elif crawl.crawler == "ache":
        crawl_instance = AcheCrawl(crawl)
        status = crawl_instance.get_status()
    else:
        status = "Error, no status found"

    return status


@app.route('/<project_slug>/crawls/<crawl_slug>/stats', methods=['GET'])
def stats_crawl(project_slug, crawl_slug):
    project = get_project(project_slug)
    key = project_slug + '-' + crawl_slug
    crawl_instance = CRAWLS.get(key)
    if crawl_instance is not None:
        return jsonify(crawl_instance.statistics())
    else:
        crawl = get_crawl(project, crawl_slug)
        seeds_list = crawl.seeds_list
        if crawl.crawler == "ache":
            model = get_crawl_model(crawl)
            crawl_instance = AcheCrawl(crawl)
        elif crawl.crawler == "nutch":
            crawl_instance = NutchCrawl(crawl)

        stats_output = crawl_instance.statistics()
        return jsonify(stats_output)


@app.route('/<project_slug>/crawls/<crawl_slug>/update_stats', methods=['POST'])
def update_stats(project_slug, crawl_slug):
    project = get_project(project_slug)
    crawl = get_crawl(project, crawl_slug)
    if request.json['crawler'] == 'ache':
        crawl.pages_crawled = request.json['crawled']
        crawl.harvest_rate = request.json['harvest']
    if request.json['crawler'] == 'nutch':
        crawl.pages_crawled = request.json['crawled']
    db.session.commit()
    return 'success' 


@app.route('/<project_slug>/crawls/<crawl_slug>/dump', methods=['POST'])
def dump_images(project_slug, crawl_slug):
    project = get_project(project_slug)
    key = project_slug + '-' + crawl_slug
    crawl = get_crawl(project, crawl_slug)
    crawl_instance = CRAWLS.get(key)
    if crawl.crawler=="ache":
        return "No image dump for ACHE crawls"
    elif crawl.crawler=="nutch":
        if crawl_instance is None:
            crawl_instance = NutchCrawl(crawl)
        image_space = get_crawl_image_space(crawl=crawl, project=project)
        crawl_instance.dump_images(image_space)
        images = os.listdir(os.path.join(IMAGE_SPACE_PATH, str(image_space.id), 'images'))
        for image in images:
            image_path = os.path.join(IMAGE_SPACE_PATH, str(image_space.id), 'images', image)
            print(image_path)
            with open(image_path, 'rb') as f:
                exif_data = exifread.process_file(f)
                db_process_exif(exif_data, crawl_slug, image, image_space)
        print("Images dumped for NUTCH crawl %s" % crawl.name)
        return redirect(url_for('image_table', project_slug=project.slug, image_space_slug=crawl.slug))
    else:
        return "Could not dump images"


# Contact page
# -----------------------------------------------------------------------------

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    crawls = Crawl.query.all()

    if form.validate_on_submit():
        subject = ' -- '.join([form.issue.data, form.name.data])
        sender = DEFAULT_MAIL_SENDER
        text_body = form.description.data
        send_email(subject=subject, sender=sender, recipients=ADMINS,
                   text_body=text_body, html_body=text_body)
        flash('Thank you for contacting us! We will be in touch shortly.', 'success')
        return redirect(url_for('index'))

    return render_template('contact.html', form=form)


# Compare (Image Space)
# ------------------------------------------------------------------------

@app.route('/<project_slug>/image_space/<image_name>/compare')
def compare(project_slug, image_name):
    project = get_project(project_slug)
    img = get_image(image_name)

    exif_info = dict(zip(('EXIF_BodySerialNumber', 'EXIF_LensSerialNumber',
              'Image_BodySerialNumber', 'MakerNote_InternalSerialNumber',
              'MakerNote_SerialNumber', 'MakerNote_SerialNumberFormat'),

             (img.EXIF_BodySerialNumber, img.EXIF_LensSerialNumber,
              img.Image_BodySerialNumber, img.MakerNote_InternalSerialNumber,
              img.MakerNote_SerialNumber, img.MakerNote_SerialNumberFormat)))

    internal_matches = get_matches(project.id, img.filename)
    for x in internal_matches:
        if (img.id, x.id) in app.MATCHES:
            x.match = "true"
        else:
            x.match = "false"

    return render_template('compare.html', image=img, exif_info=exif_info, internal_matches=internal_matches)


@app.route('/<image_directory>/images/<image_name>')
def image_source(image_directory, image_name):
    img_dir = os.path.join(IMAGE_SPACE_PATH, image_directory, 'images')
    img_filename = image_name
    return send_from_directory(img_dir, img_filename)


@app.route('/<project_slug>/image_space/<image_space_slug>/<image_name>/delete', methods=['POST'])
def delete_image(project_slug, image_space_slug, image_name):
    image = get_image(image_name) 
    os.remove(IMAGE_SPACE_PATH + image_space_slug + '/images/' + image.filename)
    db.session.delete(image) 
    db.session.commit()
    flash('%s has successfully been deleted.' % image.filename, 'success')
    return redirect(url_for('image_table', project_slug=project_slug, image_space_slug=image_space_slug))


@app.route('/uploaded_images/<image_name>')
def uploaded_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


@app.route('/<project_slug>/crawls/<crawl_slug>/seeds')
def relevant_pages(project_slug, crawl_slug):

    project = get_project(project_slug)
    crawl = get_crawl(project, crawl_slug)

    relevant = get_data_source(crawl, "relevantpages")
    # relevant_path = CRAWLS_PATH + relevant.data_uri

    return send_from_directory(os.path.join(CRAWLS_PATH, crawl.id), relevant.data_uri)


@app.route('/<project_slug>/image_space')
def image_space(project_slug):
    project = get_project(project_slug)
    image_spaces = ImageSpace.query.filter_by(project_id=project.id)
    return render_template('image_space.html', project=project, image_spaces=image_spaces)


@app.route('/<project_slug>/image_space/<image_space_slug>/')
def image_table(project_slug, image_space_slug):
    project = get_project(project_slug)
    image_space = ImageSpace.query.filter_by(name=image_space_slug).first()
    images = image_space.images.all()
    print(images)
    return render_template('image_table.html', images=images, project=project, image_space=image_space)


@app.route('/<project_slug>/upload_image', methods=['GET', 'POST'])
def upload(project_slug):
    image_names = os.listdir(UPLOAD_DIR)
    image_pages = [ {"name":filename, "url":url_for('compare', project_slug=project_slug,  image_name=filename) } \
                    for filename in image_names]
    if request.method == 'POST':
        uploaded_file = request.files['file']
        existing_file = get_uploaded_image_names()
        if uploaded_file.filename in existing_file:
            response = jsonify(dict(
                error="Image already exists by that name."))
            response.status_code = 500
            return response
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            full_path = os.path.join(app.config['UPLOAD_DIR'], filename)
            uploaded_file.save(full_path)
            with open(full_path, 'rb') as f:
                exif_data = exifread.process_file(f)
                process_exif(exif_data, 'uploaded_images', filename)
                return jsonify(url=url_for('compare', project_slug=project_slug, image_name=filename))
        else:
            allowed = ', '.join(app.config['ALLOWED_EXTENSIONS'])
            response = jsonify(dict(
                error="File does not match allowed extensions: %s" % allowed))
            response.status_code = 500
            return response

    return render_template('upload.html', image_pages=image_pages)
