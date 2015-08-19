"""Base models."""

import os
import subprocess
import shutil

from django.db import models
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save

from jinja2 import Template
from jinja2.runtime import Context

from django.conf import settings


def alphanumeric_validator():
    return RegexValidator(r'^[a-zA-Z0-9-_ ]+$',
        'Only numbers, letters, underscores, dashes and spaces are allowed.')


def zipped_file_validator():
    return RegexValidator(r'.*\.(ZIP|zip)$',
        'Only compressed archive (.zip) files are allowed.')


class Project(models.Model):
    """Project model.

    Every application that plugs into Memex Explorer should have a
    foreign key relationship to a Project.

    Model Fields
    ------------

    name : str, 64 characters max
    slug : str, 64 characters max
        The `slug` field is derived from `name` on save, and is restricted
        to URL-safe characters.
    description : textfield

    """

    name = models.CharField(max_length=64, unique=True,
        validators=[alphanumeric_validator()])
    slug = models.SlugField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(unicode(self.name))
        super(Project, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('base:project',
            kwargs=dict(project_slug=self.slug))

    @property
    def url(self):
        return self.get_absolute_url()

    def kibana_url(self):
        return '/{}/kibana/'.format(self.name)

    def __unicode__(self):
        return self.name


def get_zipped_data_path(instance, filename):
    """
    This method must stay outside of the class definition because django
    cannot serialize unbound methods in Python 2:

    https://docs.djangoproject.com/en/dev/topics/migrations/#migration-serializing
    """
    return os.path.join(settings.MEDIA_ROOT, "indices", instance.slug, "zipped_data", filename)


class Index(models.Model):
    """Index model.

    The index model keeps track of indices that are made and what files are
    contained within them.

    Model Fields
    ------------

    name : str, 64 characters max
    description : textfield
    uploaded_data : Django FileField
    data_dolder : textfield
    project : fk to base.Project

    """
    def get_dumped_data_path(instance):
        return os.path.join(
            settings.MEDIA_ROOT,
            "indices",
            instance.slug,
            "data"
        )

    name = models.CharField(max_length=64, unique=True,
        validators=[alphanumeric_validator()])
    slug = models.SlugField(max_length=64, unique=True)
    uploaded_data = models.FileField(upload_to=get_zipped_data_path,
        validators=[zipped_file_validator()])
    data_folder = models.TextField(blank=True)
    project = models.ForeignKey(Project)
    status = models.CharField(max_length=64, default="")
    num_files = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.slug = slugify(unicode(self.name))
        self.data_folder = self.get_dumped_data_path()
        super(Index, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('base:project',
            kwargs=dict(project_slug=self.project.slug))

    @property
    def index_name(self):
        return "%s_%s_%s" % (self.slug, self.project.slug, "dataset")

    def __unicode__(self):
        return self.name
