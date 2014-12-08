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
from .models import Crawl, DataSource, Dashboard, Plot, Project
from .forms import CrawlForm, MonitorDataForm, PlotForm, ContactForm, \
                    DashboardForm, ProjectForm
from .mail import send_email
from .config import ADMINS, DEFAULT_MAIL_SENDER
from .crawls import CrawlAcheInstance
from .auth import requires_auth
from .plotting import plot_builder


# Dictionary of crawls by key(project_name-crawl_name)
CRAWLS_RUNNING = {}


@app.context_processor
def context():
    projects = Project.query.all()
    return dict(projects=projects)


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


@app.route('/')
def index():
    return render_template('index.html')

# Project
# -----------------------------------------------------------------------------


@app.route('/<project_name>')
def project(project_name):
    project = Project.query.filter_by(name=project_name).first()
    if not project:
        flash("Project '%s' was not found." % project_name, 'error')
        abort(404)
    crawls = Crawl.query.filter_by(project_id=project.id)
    dashboards = Dashboard.query.filter_by(project_id=project.id)
    return render_template('project.html', project=project, crawls=crawls, \
                            dashboards=dashboards)


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    form = ProjectForm(request.form)

    if form.validate_on_submit():
        name = form.name.data
        data = Project(name=form.name.data, description=form.description.data, \
                        icon=form.icon.data)
        db.session.add(data)
        db.session.commit()
        flash("Project '%s' was successfully registered" % form.name.data, 'success')
        return redirect(url_for('project', project_name=name))

    return render_template('add_project.html', form=form)


# Crawl
# -----------------------------------------------------------------------------



@app.route('/<project_name>/add_crawl', methods=['GET', 'POST'])
def add_crawl(project_name):
    project = Project.query.filter_by(name=project_name).first()
    crawls = Crawl.query.filter_by(project_id=project.id)
    dashboards = Dashboard.query.filter_by(project_id=project.id)
    form = CrawlForm(request.form)
    if form.validate_on_submit():
        crawl = Crawl(name=form.name.data,
                      description=form.description.data,
                      crawler=form.crawler.data,
                      config=form.config.data,
                      project_id=project.id,
                      data_model_id=1)
        db.session.add(crawl)
        db.session.commit()
        flash('%s has successfully been registered!' % form.name.data, 'success')
        return redirect(url_for('crawl', project_name=project.name, \
                                crawl_name=form.name.data))

    return render_template('add_crawl.html', form=form, project=project, \
                           crawls=crawls, dashboards=dashboards)


@app.route('/<project_name>/crawls')
def crawls(project_name):
    project = Project.query.filter_by(name=project_name).first()
    crawls = Crawl.query.filter_by(project_id=project.id)
    dashboards = Dashboard.query.filter_by(project_id=project.id)
    return render_template('crawls.html', project=project, crawls=crawls, \
                            dashboards=dashboards)


@app.route('/<project_name>/crawls/<crawl_name>')
def crawl(project_name, crawl_name):
    project = Project.query.filter_by(name=project_name).first()
    crawl = Crawl.query.filter_by(name=crawl_name).first()
    crawls = Crawl.query.filter_by(project_id=project.id)
    dashboards = Dashboard.query.filter_by(project_id=project.id)
    if not crawl:
        flash("Crawl '%s' was not found." % crawl_name, 'error')
        abort(404)
    elif not project:
        flash("Project '%s' was not found." % project_name, 'error')
        abort(404)
    elif crawl.project_id != project.id:
        flash("This crawl is not part of project '%s'" % project_name, 'error')
        abort(404)
    return render_template('crawl.html', project=project, crawl=crawl,\
                            crawls=crawls, dashboards=dashboards)


@app.route('/<project_name>/crawl/<crawl_name>/run', methods=['POST'])
def run_crawl(project_name, crawl_name):
    key = project_name + '-' + crawl_name
    if CRAWLS_RUNNING.has_key(key):
        abort(400)
    else:
        crawl = Crawl.query.filter_by(name=crawl_name).first()
        seeds_list = crawl.seeds_list
        model_name = crawl.data_model
        crawl_instance = CrawlAcheInstance(seeds_list, model_name)
        pid = crawl_instance.start()
        CRAWLS_RUNNING[key] = crawl_instance
        return "Crawl running"


@app.route('/<project_name>/crawl/<crawl_name>/stop', methods=['POST'])
def stop_crawl(project_name, crawl_name):
    key = project_name + '-' + crawl_name
    crawl_instance = CRAWLS_RUNNING.get(key)
    if crawl_instance is not None:
        crawl_instance.stop()
        del CRAWLS_RUNNING[key]
        return "Crawl stopped"
    else:
        abort(400)


@app.route('/<project_name>/crawl/<crawl_name>/status', methods=['GET'])
def status_crawl(project_name, crawl_name):
    key = project_name + '-' + crawl_name
    crawl_instance = CRAWLS_RUNNING.get(key)
    if crawl_instance is not None:
        return crawl_instance.status()
    else:
        return "Stopped"

# Data
# -----------------------------------------------------------------------------


@app.route('/crawl/<crawl_endpoint>/register_data', methods=['GET', 'POST'])
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


@app.route('/crawl/<crawl_endpoint>/data/<data_endpoint>')
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


@app.route('/crawl/<crawl_endpoint>/data/<data_endpoint>/explore')
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
    project = Project.query.filter_by(name=project_name).first()
    crawls = Crawl.query.filter_by(project_id=project.id)
    dashboards = Dashboard.query.filter_by(project_id=project.id)
    form = DashboardForm(request.form)

    if form.validate_on_submit():
        data = Dashboard(name=form.name.data, description=form.description.data, \
                        project_id=project.id)
        db.session.add(data)
        db.session.commit()
        flash("Dashboard '%s' was successfully registered" % form.name.data, 'success')
        return redirect(url_for('dash', project_name=project.name, \
                        dashboard_name=form.name.data))

    return render_template('add_dashboard.html', project=project, crawls=crawls,
                            form=form, dashboards=dashboards)


@app.route('/<project_name>/dashboards/<dashboard_name>')
def dash(project_name, dashboard_name):
    project = Project.query.filter_by(name=project_name).first()
    crawls = Crawl.query.filter_by(project_id=project.id)
    dashboards = Dashboard.query.filter_by(project_id=project.id)
    dashboard = Dashboard.query.filter_by(name=dashboard_name).first()
    plots = Plot.query.filter_by(project_id=project.id)
    if not dashboard:
        flash("Dashboard '%s' was not found." % dashboard_name, 'error')
        abort(404)
    elif not project:
        flash("Project '%s' was not found." % project_name, 'error')
        abort(404)
    elif dashboard.project_id != project.id:
        flash("Dashboard is not part of project '%s'." % project_name, 'error')
        abort(404)

    return render_template('dash.html', project=project, crawls=crawls, \
                           dashboards=dashboards, dashboard=dashboard, plots=plots)


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
