import os
import errno
import shutil

from django.db import models
from base.models import Project, alphanumeric_validator
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError


from django.db.models.constants import LOOKUP_SEP
from django.db.models.query_utils import DeferredAttribute

class RefreshableModel(models.Model):

    class Meta:
        abstract = True

    def get_deferred_fields(self):
        """
        Returns a set containing names of deferred fields for this instance.
        """
        return {
            f.attname for f in self._meta.concrete_fields
            if isinstance(self.__class__.__dict__.get(f.attname), DeferredAttribute)
        }

    def refresh_from_db(self, using=None, fields=None, **kwargs):
        """
        Reloads field values from the database.
        By default, the reloading happens from the database this instance was
        loaded from, or by the read router if this instance wasn't loaded from
        any database. The using parameter will override the default.
        Fields can be used to specify which fields to reload. The fields
        should be an iterable of field attnames. If fields is None, then
        all non-deferred fields are reloaded.
        When accessing deferred fields of an instance, the deferred loading
        of the field will call this method.
        """
        if fields is not None:
            if len(fields) == 0:
                return
            if any(LOOKUP_SEP in f for f in fields):
                raise ValueError(
                    'Found "%s" in fields argument. Relations and transforms '
                    'are not allowed in fields.' % LOOKUP_SEP)

        db = using if using is not None else self._state.db
        if self._deferred:
            non_deferred_model = self._meta.proxy_for_model
        else:
            non_deferred_model = self.__class__
        db_instance_qs = non_deferred_model._default_manager.using(db).filter(pk=self.pk)

        # Use provided fields, if not set then reload all non-deferred fields.
        if fields is not None:
            fields = list(fields)
            db_instance_qs = db_instance_qs.only(*fields)
        elif self._deferred:
            deferred_fields = self.get_deferred_fields()
            fields = [f.attname for f in self._meta.concrete_fields
                      if f.attname not in deferred_fields]
            db_instance_qs = db_instance_qs.only(*fields)

        db_instance = db_instance_qs.get()
        non_loaded_fields = db_instance.get_deferred_fields()
        for field in self._meta.concrete_fields:
            if field.attname in non_loaded_fields:
                # This field wasn't refreshed - skip ahead.
                continue
            setattr(self, field.attname, getattr(db_instance, field.attname))
            # Throw away stale foreign key references.
            if field.rel and field.get_cache_name() in self.__dict__:
                rel_instance = getattr(self, field.get_cache_name())
                local_val = getattr(db_instance, field.attname)
                related_val = getattr(rel_instance, field.related_field.attname)
                if local_val != related_val:
                    del self.__dict__[field.get_cache_name()]
        self._state.db = db_instance._state.db



def validate_model_file(value):
    if value != 'pageclassifier.model':
        raise ValidationError("Model file must be named 'pageclassifier.model'.")

from crawl_space.settings import MODEL_PATH, CRAWL_PATH, SEEDS_TMP_DIR

def validate_features_file(value):
    if value != 'pageclassifier.features':
        raise ValidationError("Features file must be named 'pageclassifier.features'.")



class CrawlModel(models.Model):

    def get_upload_path(instance, filename):
        return os.path.join('models', instance.name, filename)


    def get_model_path(instance):
        return os.path.join(MODEL_PATH, str(instance.pk))

    
    name = models.CharField(max_length=64)
    model = models.FileField(upload_to=get_upload_path, validators=[validate_model_file])
    features = models.FileField(upload_to=get_upload_path, validators=[validate_features_file])
    project = models.ForeignKey(Project)

    def get_absolute_url(self):
        return reverse('base:project',
            kwargs=dict(slug=self.project.slug))


    def save(self, *args, **kwargs):

        if self.pk is None:
            super().save(*args, **kwargs)

            model_path = self.ensure_model_path()
            model_dst = os.path.join(model_path, 'pageclassifier.model')
            features_dst = os.path.join(crawl_path, 'pageclassifier.features')

            shutil.move(self.model.path, model_dst)
            self.model.name = model_dst
            shutil.move(self.features.path, features_dst)
            self.features.name = features_dst

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Crawl(RefreshableModel):


    def ensure_crawl_path(instance):
        crawl_path = os.path.join(CRAWL_PATH, str(instance.pk))
        try:
            os.makedirs(crawl_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        return crawl_path

    def get_crawl_path(instance):
        return os.path.join(CRAWL_PATH, str(instance.pk))


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
    config = models.CharField(max_length=64,
        default="config_default")
    seeds_list = models.FileField(upload_to=get_seeds_upload_path)
    pages_crawled = models.BigIntegerField(default=0)
    harvest_rate = models.FloatField(default=0)
    project = models.ForeignKey(Project)
    crawl_model = models.ForeignKey(CrawlModel, null=True, blank=True, 
        default=None)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        # If this is the first time the model is saved, then the seeds
        #    file needs to be moved from SEEDS_TMP_DIR/filename to the
        #    crawl directory.
        if self.pk is None:
            # Need to save first to obtain the pk attribute.
            self.slug = slugify(self.name)
            super().save(*args, **kwargs)

            # Ensure that the crawl path `resources/<crawl.pk>` exists
            crawl_path = self.ensure_crawl_path()

            # Move the file from temporary directory to crawl directory,
            #   and update the FileField accordingly:
            #   https://code.djangoproject.com/ticket/15590#comment:10

            # Nutch requires a seed directory, not a seed file
            if self.crawler == 'nutch':
                seed_dir = os.mkdir(os.path.join(crawl_path, 'seeds'))
                dst = os.path.join(crawl_path, 'seeds/seeds')
                shutil.move(self.seeds_list.path, dst)
                self.seeds_list.name = seed_dir

            else:
                dst = os.path.join(crawl_path, 'seeds')
                shutil.move(self.seeds_list.path, dst)
                self.seeds_list.name = dst

            # Continue saving as normal

        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('base:crawl_space:crawl',
            kwargs=dict(slug=self.project.slug, crawl_slug=self.slug))

