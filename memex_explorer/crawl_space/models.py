import os
import errno

from django.db import models
from base.models import Project, alphanumeric_validator
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError


def validate_model_file(value):
    if value != 'pageclassifier.model':
        raise ValidationError("Model file must be named 'pageclassifier.model'.")

from crawl_space.settings import CRAWL_PATH, SEEDS_TMP_DIR

def validate_features_file(value):
    if value != 'pageclassifier.features':
        raise ValidationError("Features file must be named 'pageclassifier.features'.")


class DataModel(models.Model):


    def get_upload_path(instance, filename):
        return os.path.join('models', instance.name, filename)
    
    name = models.CharField(max_length=64)
    model = models.FileField(upload_to=get_upload_path, validators=[validate_model_file])
    features = models.FileField(upload_to=get_upload_path, validators=[validate_features_file])
    project = models.ForeignKey(Project)

    def get_absolute_url(self):
        return reverse('base:project',
            kwargs=dict(slug=self.project.slug))

    def __str__(self):
        return self.name


from django.conf import settings as app_settings

class Crawl(models.Model):


    def ensure_crawl_path(instance):
        crawl_path = os.path.join(CRAWL_PATH, slugify(str(instance.pk)))
        try:
            os.makedirs(crawl_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        return crawl_path


    def get_seeds_upload_path(instance, filename):
        return os.path.join(SEEDS_TMP_DIR, filename)

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
    config = models.CharField(max_length=64)
    seeds_list = models.FileField(upload_to=get_seeds_upload_path)
    pages_crawled = models.BigIntegerField(default=0)
    harvest_rate = models.FloatField(default=0)
    project = models.ForeignKey(Project)
    data_model = models.ForeignKey(DataModel)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        # If this is the first time the model is saved, then the seeds
        #    file needs to be moved from SEEDS_TMP_DIR/filename to the
        #    crawl directory.
        if self.pk is None:
            ensure_crawl_path()
            self.slug = slugify(self.name)
            # Need to save first to obtain the pk attribute.
            super().save(*args, **kwargs)

        else:
            self.slug = slugify(self.name)
            super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('base:crawl_space:crawl',
            kwargs=dict(slug=self.project.slug, crawl_slug=self.slug))

