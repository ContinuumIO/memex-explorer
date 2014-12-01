from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, ValidationError, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email


class CrawlForm(Form):
    name = StringField('Name', validators = [DataRequired()])
    description = TextAreaField('Description')


class MonitorDataForm(Form):
    name = StringField('Name', validators = [DataRequired()])
    data_uri = StringField('Data URI', validators = [DataRequired()])
    description = TextAreaField('Description')


class DashboardForm(Form):
    name = StringField('Name', validators = [DataRequired()])
    description = TextAreaField('Description')


class PlotForm(Form):
    name = StringField('Name', validators = [DataRequired()])
    description = TextAreaField('Description')
    plot = SelectField('Plot', choices=[('domain_by_relevance', 'Domain Relevance'), ('domain_by_crawled', 'Domain Crawled'), \
        ('domain_by_frontier', 'Domain Frontier'), ('harvest', 'Harvest'), \
        ('harvest_updating', 'Updating Harvest'), \
        ('harvest_rate', 'Harvest rate'), ('termite', 'Termite')], validators = [DataRequired()])


class ContactForm(Form):
    name = StringField('Name', validators = [DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])
    description = TextAreaField('Name', validators = [DataRequired()])
