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

# Third-party Libraries 
# ---------------------

from flask import (redirect, flash, render_template, request, url_for,
                   send_from_directory, jsonify, session, abort)
from werkzeug import secure_filename
from webhelpers import text

from blaze import resource, discover, Data, into, compute
from pandas import DataFrame
from bokeh.plotting import ColumnDataSource

# Local Imports
# -------------

from . import app, db
from app import models
from app import db_api
from app import forms
from app import crawls

from .rest_api import api
from .mail import send_email

from .config import ADMINS, DEFAULT_MAIL_SENDER, BASEDIR, SEED_FILES, \
                    CONFIG_FILES, MODEL_FILES, CRAWLS_PATH

from .auth import requires_auth
from .plotting import plot_builder


from .viz.domain import Domain
from .viz.harvest import Harvest
from .viz.harvest_rate import HarvestRate
# from .viz.termite import Termite


# Dictionary of crawls by key(project_name-crawl_name)
CRAWLS_RUNNING = {}


@app.context_processor
def context():
    """Inject some context variables useful across templates.
    See http://flask.pocoo.org/docs/0.10/templating/#context-processors
    """

    context_vars = {}

    if request.view_args and 'project_name' in request.view_args:
        project_name = request.view_args['project_name']
        project = db_api.get_project(project_name)
        if not project:
            return {}
            # flash("Project '%s' was not found." % project_name, 'error')
            # abort(404)

        crawls = db_api.get_crawls(project.id)
        dashboards = db_api.get_dashboards(project.id)
        model = db_api.get_models()
        images = db_api.get_image_space(project.id)



        context_vars.update(dict(
            project=project, crawls=crawls, dashboards=dashboards, \
            models=model, images=images))
    # All pages should (potentially) be able to present all projects
    import pdb; pdb.set_trace;
    projects = models.Project.query.all()
    context_vars.update(projects=projects)

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


# Project
# -----------------------------------------------------------------------------

@app.route('/<project_name>')
def project(project_name):

    # return render_template('project.html', project=project, crawls=crawls,
    #                                        dashboards=dashboards)

    # `project`, `crawls`, and `dashboards` handled by the context processor.
    #   See `context() defined above.`
    return render_template('project.html')


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    form = forms.ProjectForm(request.form)

    if form.validate_on_submit():
        project = models.Project(name=form.name.data, description=form.description.data, \
                        icon=form.icon.data)
        db.session.add(project)
        db.session.commit()
        flash("Project '%s' was successfully registered" % project.name, 'success')
        return redirect(url_for('project', project_name=project.name))

    return render_template('add_project.html', form=form)


# Crawl
# -----------------------------------------------------------------------------

@app.route('/<project_name>/add_crawl', methods=['GET', 'POST'])
def add_crawl(project_name):
    form = forms.CrawlForm()
    if form.validate_on_submit():
        seed_filename = secure_filename(form.seeds_list.data.filename)
        form.seeds_list.data.save(SEED_FILES + seed_filename)
        # TODO allow upload configuration
        #config_filename = secure_filename(form.config.data.filename)
        #form.config.data.save(CONFIG_FILES + config_filename)
        project = db_api.get_project(project_name)
        crawl = db_api.db_add_crawl(project, form, seed_filename)
        subprocess.Popen(['mkdir', os.path.join(CRAWLS_PATH, crawl.name)])

        if crawl.crawler == 'ache':
            db_api.db_init_ache(project, crawl)

        else: 
            #TODO add db_init_nutch
            pass

        flash('%s has successfully been registered!' % form.name.data, 'success')
        return redirect(url_for('crawl', project_name=db_api.get_project(project_name),
                                         crawl_name=form.name.data))

    return render_template('add_crawl.html', form=form)


@app.route('/<project_name>/add_model', methods=['GET', 'POST'])
def add_model(project_name):
    form = forms.DataModelForm()
    if form.validate_on_submit():
        registered_model = forms.DataModel.query.filter_by(name=form.name.data).first()
        if registered_model:
            flash('Data model name already exists, please choose another name', 'error')
            return render_template('add_data_model.html', form=form)
        files = request.files.getlist("files")
        if not os.path.exists(MODEL_FILES + form.name.data):
            os.makedirs(MODEL_FILES + form.name.data)
        for x in files:
            x.save(MODEL_FILES + form.name.data + '/' + x.filename)
        model = models.DataModel(name=form.name.data,
                          filename=MODEL_FILES + form.name.data)
        db.session.add(model)
        db.session.commit()
        flash('Model has successfully been registered!', 'success')
        return redirect(url_for('project', 
                                project_name=db_api.get_project(project_name).name))

    return render_template('add_data_model.html', form=form)


@app.route('/<project_name>/crawls')
def crawls(project_name):
    return render_template('crawls.html')


@app.route('/<project_name>/crawls/<crawl_name>')
def crawl(project_name, crawl_name):
    project = db_api.get_project(project_name)
    crawl = db_api.get_crawl(crawl_name)

    if not project:
        flash("Project '%s' was not found." % project_name, 'error')
        abort(404)
    elif not crawl:
        flash("Crawl '%s' was not found." % crawl_name, 'error')
        abort(404)

    return render_template('crawl.html', crawl=crawl)


@app.route('/<project_name>/crawls/<crawl_name>/run', methods=['POST'])
def run_crawl(project_name, crawl_name):
    key = project_name + '-' + crawl_name
    if CRAWLS_RUNNING.has_key(key):
        return "Crawl is already running."
    else:
        crawl = db_api.get_crawl(crawl_name)
        seeds_list = crawl.seeds_list
        if crawl.crawler=="ache":
            model = db_api.get_crawl_model(crawl)
            crawl_instance = crawls.AcheCrawl(crawl_name=crawl.name, seeds_file=seeds_list, model_name=model.name,
                                       conf_name=crawl.config)
            pid = crawl_instance.start()
            CRAWLS_RUNNING[key] = crawl_instance
            return "Crawl %s running" % crawl.name
        elif crawl.crawler=="nutch":
            crawl_instance = crawls.NutchCrawl(seed_dir=seeds_list, crawl_dir=crawl.name)
            pid = crawl_instance.start()
            CRAWLS_RUNNING[key] = crawl_instance
            return "Crawl %s running" % crawl.name
        else:
            abort(400)


@app.route('/<project_name>/crawls/<crawl_name>/stop', methods=['POST'])
def stop_crawl(project_name, crawl_name):
    key = project_name + '-' + crawl_name
    crawl_instance = CRAWLS_RUNNING.get(key)
    if crawl_instance is not None:
        crawl_instance.stop()
        del CRAWLS_RUNNING[key]
        return "Crawl stopped"
    else:
        abort(400)


@app.route('/<project_name>/crawls/<crawl_name>/refresh', methods=['POST'])
def refresh(project_name, crawl_name):

    domain_plot = models.Plot.query.filter_by(name='domain').first()

    # TODO retrieve data from db. These are only valid if crawler==ache.
    crawled_data_uri = os.path.join(CRAWLS_PATH, crawl_name, 'data/data_monitor/crawledpages.csv')
    relevant_data_uri = os.path.join(CRAWLS_PATH, crawl_name, 'data/data_monitor/relevantpages.csv')
    frontier_data_uri = os.path.join(CRAWLS_PATH, crawl_name, 'data/data_monitor/frontierpages.csv')
    domain_sources = dict(crawled=crawled_data_uri, relevant=relevant_data_uri, frontier=frontier_data_uri)

    domain = Domain(domain_sources, domain_plot)
    domain.push_to_server()

    harvest_plot = models.Plot.query.filter_by(name='harvest').first()

    harvest_data_uri = os.path.join(CRAWLS_PATH, crawl_name, 'data/data_monitor/harvestinfo.csv')
    harvest_sources = dict(harvest=harvest_data_uri)
    harvest = Harvest(harvest_sources, harvest_plot)

    harvest.push_to_server()

    return "pushed"


@app.route('/<project_name>/crawls/<crawl_name>/dashboard')
def view_plots(project_name, crawl_name):

    crawl = models.Crawl.query.filter_by(name=crawl_name).first()

    key = project_name + '-' + crawl_name

    # Domain
    plot = models.Plot.query.filter_by(name=key + '-' + 'domain').first()

    #TODO use db_api
    crawled_data_uri = os.path.join(CRAWLS_PATH, crawl_name, 'data/data_monitor/crawledpages.csv')
    relevant_data_uri = os.path.join(CRAWLS_PATH, crawl_name, 'data/data_monitor/relevantpages.csv')
    frontier_data_uri = os.path.join(CRAWLS_PATH, crawl_name, 'data/data_monitor/frontierpages.csv')
    domain_sources = dict(crawled=crawled_data_uri, relevant=relevant_data_uri, frontier=frontier_data_uri)

    domain = Domain(domain_sources, plot)
    domain_tag, source_id = domain.create_and_store()

    plot.source_id = source_id
    ###


    # Harvest

    plot = models.Plot.query.filter_by(name='harvest').first()

    harvest_data_uri = os.path.join(CRAWLS_PATH, crawl_name, 'data/data_monitor/harvestinfo.csv')

    harvest_sources = dict(harvest=harvest_data_uri)

    harvest = Harvest(harvest_sources, plot)
    harvest_tag, source_id = harvest.create_and_store()

    plot.source_id = source_id
    ###

    db.session.flush()
    db.session.commit()

    return render_template('dash.html', plots=[domain_tag, harvest_tag], crawl=crawl)


@app.route('/<project_name>/crawls/<crawl_name>/status', methods=['GET'])
def status_crawl(project_name, crawl_name):
    key = project_name + '-' + crawl_name
    crawl_instance = CRAWLS_RUNNING.get(key)
    if crawl_instance is not None:
        return crawl_instance.status()
    else:
        return "Stopped"


# Image Space
# -----------------------------------------------------------------------------

@app.route('/<project_name>/crawls/<crawl_name>/image_space')
def image_space(project_name, crawl_name):
    if not crawl:
        flash("Crawl '%s' was not found." % crawl_name, 'error')
        abort(404)
    elif not project:
        flash("Project '%s' was not found." % project_name, 'error')
        abort(404)
    elif crawl.project_id != project.id:
        flash("This crawl is not part of project '%s'" % project_name, 'error')
        abort(404)
    return render_template('crawl.html')


# Data
# -----------------------------------------------------------------------------


@app.route('/crawsl/<crawl_endpoint>/register_data', methods=['GET', 'POST'])
def register_data(crawl_endpoint):
    crawl = Crawl.query.filter_by(endpoint=crawl_endpoint).first()
    form = MonitorDataForm(request.form)

    if form.validate_on_submit():
        endpoint = text.urlify(form.name.data)
        data = DataSource(name=form.name.data, endpoint=endpoint,
           data_uri=form.data_uri.data, description=form.description.data, crawl=crawl)
        registered_data = crawl.query.filter_by(name=form.name.data).first()

        if registered_data:
            flash('Monitor data name already registered, please choose another name', 'error')
            return render_template('register_data.html', form=form)

        db.session.add(data)
        db.session.commit()
        flash("Monitor data source '%s' was successfully registered" % form.name.data, 'success')
        return redirect(url_for('data', crawl_endpoint=crawl_endpoint, data_endpoint=endpoint))

    return render_template('register_data.html', crawl=crawl, form=form)


@app.route('/crawls/<crawl_endpoint>/data/<data_endpoint>')
def data(crawl_endpoint, data_endpoint):
    crawl = Crawl.query.filter_by(endpoint=crawl_endpoint).first()
    monitor_data = DataSource.query.filter_by(crawl_id=crawl.id, endpoint=data_endpoint).first()

    plots = monitor_data.plots
    plot_list = [dict(name=x.name, endpoint=x.endpoint) for x in plots]

    try:
        uri = monitor_data.data_uri
        r = resource(uri)
    except Exception as e:
        flash("Could not parse the data source with Blaze. Sorry, it's not possible to explore the dataset at this time.", 'error')
        return redirect(url_for('crawl', crawl_endpoint=crawl.endpoint))

    t = Data(uri)
    dshape = t.dshape
    columns = t.fields
    fields = ', '.join(columns)
    expr = t.head(10)
    df = into(DataFrame, expr)
    sample = df.to_html()

    return render_template('data.html',
                           crawl=crawl, data=monitor_data, plots=plots,
                           fields=fields, sample=sample, dshape=dshape) 


@app.route('/crawls/<crawl_endpoint>/data/<data_endpoint>/explore')
def data_explore(crawl_endpoint, data_endpoint):
    crawl = Crawl.query.filter_by(endpoint=crawl_endpoint).first()
    monitor_data = DataSource.query.filter_by(crawl_id=crawl.id,endpoint=data_endpoint).first()

    plots = monitor_data.plots
    plot_list = [dict(name=x.name, endpoint=x.endpoint) for x in plots]

    # TODO wrap Blaze err handling
    uri = monitor_data.data_uri
    t = Data(uri)
    dshape = t.dshape
    columns = t.fields
    fields = ', '.join(columns)
    expr = t.head(10)
    df = into(DataFrame, expr)
    sample = df.to_html()

    return render_template('data_explore.html',
                           crawl=crawl, data=monitor_data, plots=plots,
                           fields=fields, sample=sample, dshape=dshape) 


# Plot & Dashboard
# -----------------------------------------------------------------------------

@app.route('/<project_name>/add_dashboard', methods=['GET', 'POST'])
def add_dashboard(project_name):
    form = DashboardForm(request.form)

    if form.validate_on_submit():
        data = Dashboard(name=form.name.data, description=form.description.data, \
                        project_id=project.id)
        db.session.add(data)
        db.session.commit()
        flash("Dashboard '%s' was successfully registered" % form.name.data, 'success')
        return redirect(url_for('dash', project_name=project.name, \
                        dashboard_name=form.name.data))

    return render_template('add_dashboard.html')


@app.route('/<project_name>/dashboards/<dashboard_name>')
def dash(project_name, dashboard_name):
    dashboard = models.Dashboard.query.filter_by(name=dashboard_name).first()
    plots = models.Plot.query.filter_by(project_id=project.id)
    if not dashboard:
        flash("Dashboard '%s' was not found." % dashboard_name, 'error')
        abort(404)
    elif not project:
        flash("Project '%s' was not found." % project_name, 'error')
        abort(404)
    elif dashboard.project_id != project.id:
        flash("Dashboard is not part of project '%s'." % project_name, 'error')
        abort(404)

    return render_template('dash.html', dashboard=dashboard, plots=plots)


@app.route('/<crawl_endpoint>/plot/<plot_endpoint>')
def plot(crawl_endpoint, plot_endpoint):
    crawl = Crawl.query.filter_by(endpoint=crawl_endpoint).first()
    plot = Plot.query.filter_by(endpoint=plot_endpoint).first()
    script, div = plot_builder(crawl, plot)

    return render_template('plot.html',
                           plot=plot, crawl=crawl, div=div, script=script) 


@app.route('/crawl/<crawl_endpoint>/create_plot', methods=['GET', 'POST'])
def create_plot(crawl_endpoint):
    form = PlotForm(request.form)
    crawl = Crawl.query.filter_by(endpoint=crawl_endpoint).first()
    if form.validate_on_submit():
        endpoint = text.urlify(form.name.data)
        plot = Plot(name=form.name.data, endpoint=endpoint,
                    plot=form.plot.data, description=form.description.data)
        crawl.plots.append(plot)
        db.session.add(plot)
        db.session.commit()
        flash('Your plot was successfully registered!', 'success')
        return redirect(url_for('plot',
            crawl_endpoint=crawl.endpoint, plot_endpoint=endpoint))

    return render_template('create_plot.html', crawl=crawl, form=form)


@app.route('/data/<data_endpoint>/edit', methods=['GET', 'POST'])
@requires_auth
def data_edit(data_endpoint):
    form = SourceForm(request.form)
    crawls = Crawl.query.all()
    datasource = Crawl.query.filter_by(endpoint=data_endpoint).first()

    description = Crawl.description
    if form.validate_on_submit():
        db.session.add(crawl)
        crawl.name = form.name.data
        crawl.endpoint = text.urlify(form.name.data)
        crawl.uri = form.uri.data
        crawl.description = form.description.data
        crawl.datashape = form.datashape.data
        db.session.flush()
        db.session.commit()
        crawls = Crawl.query.all()
        flash('Your data source was successfully updated!', 'success')
        return redirect(url_for('data', crawl_endpoint=crawl.endpoint,
                                        data_endpoint=data_endpoint))
    return render_template('edit.html', form=form, crawl=crawl)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = form.ContactForm(request.form)
    crawls = models.Crawl.query.all()

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

@app.route('/<project_name>/image_space/<image_id>/compare/')
def compare(project_name, image_id):

    project = db_api.get_project(project_name)
    images = db_api.get_images(project.id)

    img = db_api.get_image(image_id)

    exif_info = dict(zip(('EXIF_BodySerialNumber', 'EXIF_LensSerialNumber',
              'Image_BodySerialNumber', 'MakerNote_InternalSerialNumber',
              'MakerNote_SerialNumber', 'MakerNote_SerialNumberFormat'),

             (img.EXIF_BodySerialNumber, img.EXIF_LensSerialNumber,
              img.Image_BodySerialNumber, img.MakerNote_InternalSerialNumber,
              img.MakerNote_SerialNumber, img.MakerNote_SerialNumberFormat)))

    # serial_matches = get_info_serial(img.EXIF_BodySerialNumber)
    # full_match_paths = [app.config['STATIC_IMAGE_DIR'] + x.img_file for x in serial_matches
    #                                                                  if x.Uploaded != 1]
    # internal_matches = [(x.split('/static/')[-1], x.split('/')[-1])
    #                         for x in full_match_paths]

    internal_matches = db_api.get_matches(project.id, img.id)
    for x in internal_matches:
        if (img.id, x.id) in app.MATCHES:
            x.match = "true"
        else:
            x.match = "false"

    # if img.EXIF_BodySerialNumber:
    #     external_matches = lost_camera_retreive(img.EXIF_BodySerialNumber)
    # else:
    #     external_matches = []

    return render_template('compare.html', image=img, exif_info=exif_info, 
                            internal_matches=internal_matches,
                            # external_matches=external_matches
                             )

@app.route('/static/image/<image_id>')
def image_source(image_id):
    img_dir = os.path.join(BASEDIR,
                                   'image')

    img_filename = "%s.jpg" % image_id
    print(img_dir, img_filename)

    return send_from_directory(img_dir, img_filename)


@app.route('/<project_name>/image_space/<image_id>')
def inspect(project_name, image_id):
    img = db_api.get_image(image_id)

    exif_info = dict(zip(('EXIF_BodySerialNumber', 'EXIF_LensSerialNumber',
              'Image_BodySerialNumber', 'MakerNote_InternalSerialNumber',
              'MakerNote_SerialNumber', 'MakerNote_SerialNumberFormat'),

             (img.EXIF_BodySerialNumber, img.EXIF_LensSerialNumber,
              img.Image_BodySerialNumber, img.MakerNote_InternalSerialNumber,
              img.MakerNote_SerialNumber, img.MakerNote_SerialNumberFormat)))

    return render_template('inspect.html', image=img, exif_info=exif_info)

