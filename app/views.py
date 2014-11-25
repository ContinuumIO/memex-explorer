"""Main views for memex-viewer application"""
from __future__ import absolute_import, division, print_function

#  IMPORTS
# =========

# Standard Library
# ----------------

# Third-party Libraries
# ---------------------

from flask import (redirect, flash, render_template, request, url_for,
                   abort)
from blaze import resource, Data, into
from pandas import DataFrame

# Local Imports
# -------------

from . import app, db, text
from .models import Crawl, MonitorData, Dashboard, Plot
from .forms import CrawlForm, DashboardForm, MonitorDataForm, DashboardForm, PlotForm, ContactForm
from .mail import send_email
from .config import ADMINS, DEFAULT_MAIL_SENDER
from .auth import requires_auth
from .plotting import plot_builder


@app.context_processor
def inject_crawls():
    crawls = Crawl.query.all()
    plots = Plot.query.all()
    dashboards = Dashboard.query.all()
    return dict(crawls=crawls, plots=plots, dashboards=dashboards)


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

# Crawl
# -----------------------------------------------------------------------------

@app.route('/register_crawl', methods=['GET', 'POST'])
def register():
    form = CrawlForm(request.form)
    if form.validate_on_submit():
        endpoint = text.urlify(form.name.data)
        crawl = Crawl(name=form.name.data,
                      endpoint=endpoint,
                      description=form.description.data)

        crawl_exists = crawl.query.filter_by(name=form.name.data).first()
        if crawl_exists:
            flash("A crawl named '%s' has already been registered-"
                  "please provide another name." % form.name.data, 'error')
            return render_template('register_crawl.html', form=form)
        else:
            db.session.add(crawl)
            db.session.commit()
            flash('%s has successfully been registered!' % form.name.data, 'success')
            return redirect(url_for('crawl', crawl_endpoint=endpoint))

    return render_template('register_crawl.html', form=form)


@app.route('/crawl/<crawl_endpoint>')
def crawl(crawl_endpoint):
    crawl = Crawl.query.filter_by(endpoint=crawl_endpoint).first()
    if crawl is None:
        flash("Crawl '%s' was not found." % crawl_endpoint, 'error')
        abort(404)

    data = crawl.monitor_data.all()
    plots = crawl.plots
    dashbs = crawl.dashboards

    data_list = [dict(name=x.name, endpoint=x.endpoint) for x in data]
    plot_list = [dict(name=x.name, endpoint=x.endpoint) for x in plots]
    dash_list = [dict(name=x.name, endpoint=x.endpoint) for x in dashbs]

    return render_template('crawl.html',
                            crawl=crawl, data_list=data_list,
                            plot_list=plot_list, dash_list=dash_list)

# Data
# -----------------------------------------------------------------------------

@app.route('/crawl/<crawl_endpoint>/register_data', methods=['GET', 'POST'])
def register_data(crawl_endpoint):
    crawl = Crawl.query.filter_by(endpoint=crawl_endpoint).first()
    form = MonitorDataForm(request.form)

    if form.validate_on_submit():
        endpoint = text.urlify(form.name.data)
        data = MonitorData(name=form.name.data, endpoint=endpoint,
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
    monitor_data = MonitorData.query.filter_by(crawl_id=crawl.id, endpoint=data_endpoint).first()

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
    monitor_data = MonitorData.query.filter_by(crawl_id=crawl.id,endpoint=data_endpoint).first()

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

# Plot
# -----------------------------------------------------------------------------

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


@app.route('/dashboard/<dashboard_endpoint>')
def dash(dashboard_endpoint):
    dash = Dashboard.query.filter_by(endpoint=dashboard_endpoint).first()
    plots = dash.plots
    crawls = dash.crawls.query.all()

    return render_template('dash.html', dash=dash, plot=plot, crawls=crawls) 


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
