import os
import shutil

from os.path import join

from django.db import models
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from base.models import Project, alphanumeric_validator
from apps.crawl_space.utils import ensure_exists


def validate_model_file(value):
    if value != 'pageclassifier.model':
        raise ValidationError("Model file must be named 'pageclassifier.model'.")

from apps.crawl_space.settings import (MODEL_PATH, CRAWL_PATH,
                                       SEEDS_TMP_DIR, MODELS_TMP_DIR)

def validate_features_file(value):
    if value != 'pageclassifier.features':
        raise ValidationError("Features file must be named 'pageclassifier.features'.")

class CrawlModel(models.Model):
    """CrawlModel model, specifically for ACHE crawls.

    Model Fields
    ------------

    name : str, 64 characters max
    model : FileField
        Upload pageclassifier.model file
    features : FileField
        Upload pageclassifier.features file
    project : fk to base.Project

    """


    def get_model_upload_path(instance, filename):
        return join(MODELS_TMP_DIR, instance.name, filename)

    def get_model_path(instance):
        return join(MODEL_PATH, str(instance.pk))

    def ensure_model_path(instance):
        model_path = instance.get_model_path()
        ensure_exists(model_path)

        return model_path
    
    name = models.CharField(max_length=64, validators=[alphanumeric_validator()])
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=64)
    model = models.FileField(upload_to=get_model_upload_path,
        validators=[validate_model_file])
    features = models.FileField(upload_to=get_model_upload_path,
        validators=[validate_features_file])
    project = models.ForeignKey(Project)

    def get_absolute_url(self):
        return reverse('base:project',
            kwargs=dict(project_slug=self.project.slug))


    def save(self, *args, **kwargs):

        if self.pk is None:
            super(CrawlModel, self).save(*args, **kwargs)

            model_path = self.ensure_model_path()
            model_dst = join(model_path, 'pageclassifier.model')
            features_dst = join(model_path, 'pageclassifier.features')

            shutil.move(self.model.path, model_dst)
            self.model.name = model_dst
            shutil.move(self.features.path, features_dst)
            self.features.name = features_dst

        self.slug = slugify(self.name)
        super(CrawlModel, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class Crawl(models.Model):
    """Crawl model.

    Model Fields
    ------------

    name : str, 64 characters max
    slug : str, 64 characters max
        The `slug` field is derived from `name` on save, and is restricted
        to URL-safe characters.
    description : str
    crawler : str
        Either 'nutch' or 'ache'
    status : str
    config : str
        [ACHE] Name of configuration directory, defaults to "config_default"
    seeds_list : FileField
        Upload text file containing seed URLs
    pages_crawled : int
    harvest_rate : float
        [ACHE] Ratio of relevant pages in the crawl
    project : fk to base.Project
    crawl_model : fk to CrawlModel
    """

    def get_seeds_upload_path(instance, filename):
        return join(SEEDS_TMP_DIR, instance.name, filename)
        
    def get_crawl_path(instance):
        return join(CRAWL_PATH, str(instance.pk))

    def ensure_crawl_path(instance):
        crawl_path = instance.get_crawl_path()
        ensure_exists(crawl_path)
        return crawl_path

    CRAWLER_CHOICES = (
        ('nutch', "Nutch"),
        ('ache', "ACHE"))

    name = models.CharField(max_length=64, unique=True,
        validators=[alphanumeric_validator()])
    slug = models.SlugField(max_length=64, unique=True)
    description = models.TextField()
    crawler = models.CharField(max_length=64,
        choices=CRAWLER_CHOICES,
        default='nutch')
    status = models.CharField(max_length=64,
        default="Not started")
    config = models.CharField(max_length=64,
        default="config_default")
    seeds_list = models.FileField(upload_to=get_seeds_upload_path)
    pages_crawled = models.BigIntegerField(default=0)
    harvest_rate = models.FloatField(default=0)
    project = models.ForeignKey(Project)
    crawl_model = models.ForeignKey(CrawlModel, null=True, blank=True, 
        default=None)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):

        # If this is the first time the model is saved, then the seeds
        #    file needs to be moved from SEEDS_TMP_DIR/filename to the
        #    crawl directory.
        if self.pk is None:
            # Need to save first to obtain the pk attribute.
            self.slug = slugify(unicode(self.name))
            super(Crawl, self).save(*args, **kwargs)

            # Ensure that the crawl path `resources/crawls/<crawl.pk>` exists
            crawl_path = self.ensure_crawl_path()

            # Move the file from temporary directory to crawl directory,
            #   and update the FileField accordingly:
            #   https://code.djangoproject.com/ticket/15590#comment:10

            # Nutch requires a seed directory, not a seed file
            if self.crawler == 'nutch':
                seed_dir = join(crawl_path, 'seeds')
                ensure_exists(seed_dir)
                dst = join(crawl_path, 'seeds/seeds')
                shutil.move(self.seeds_list.path, dst)
                self.seeds_list.name = seed_dir
            else:
                dst = join(crawl_path, 'seeds')
                shutil.move(self.seeds_list.path, dst)
                self.seeds_list.name = dst

            # Continue saving as normal

        self.slug = slugify(unicode(self.name))
        super(Crawl, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('base:crawl_space:crawl',
            kwargs=dict(project_slug=self.project.slug, crawl_slug=self.slug))

