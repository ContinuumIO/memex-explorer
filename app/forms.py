from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, ValidationError, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plotting import PLOT_TYPES
from models import DataModel

from . import app, db


def data_models():
    return DataModel.query.all()


class CrawlForm(Form):
    name = StringField('Name', validators = [DataRequired()])
    description = TextAreaField('Description')
    crawler = SelectField('Crawler', choices=[('nutch','Nutch'), \
                         ('ache','Ache')],
                          validators=[DataRequired()])
    # config = FileField('Configuration', DataRequired()])
    seeds_list = FileField('Seeds List', validators=[DataRequired()])
    data_model = QuerySelectField('Data Model', query_factory=data_models, \
                                  allow_blank=True, get_label='name')
    new_model_file = FileField()
    new_model_features = FileField()
    new_model_name = StringField()


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
    plot = SelectField('Plot', choices=PLOT_TYPES, validators = [DataRequired()])


class ContactForm(Form):
    name = StringField('Name', validators = [DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])
    description = TextAreaField('Name', validators = [DataRequired()])


class ProjectForm(Form):
    name = StringField('Name', validators = [DataRequired()])
    description = TextAreaField('Description')
    icon = StringField('Icon')

class DataModelForm(Form):
    name = StringField('Name', validators = [DataRequired()])
    filename = FileField()


# Forms for edit views.


class EditProjectForm(Form):
    name = StringField('Name')
    description = TextAreaField('Description')
    icon = StringField('Icon')


class EditCrawlForm(Form):
    name = StringField('Name')
    description = TextAreaField('Description')
    crawler = SelectField('Crawler', choices=[('',''),('nutch','Nutch'), \
                         ('ache','Ache')])
    seeds_list = FileField('Seeds List')
    data_model = QuerySelectField('Data Model', query_factory=data_models, \
                                  allow_blank=True, get_label='name')
