from rest_framework import routers, serializers, viewsets, parsers, filters

from base.models import Project
from apps.crawl_space.models import Crawl, CrawlModel


class SlugModelSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False, read_only=True)


class ProjectSerializer(SlugModelSerializer):
    url = serializers.CharField(read_only=True)

    class Meta:
        model = Project


class CrawlSerializer(SlugModelSerializer):
    # Expose these fields, but only as read only.
    id = serializers.ReadOnlyField()
    seeds_list = serializers.FileField(use_url=False)
    status = serializers.CharField(read_only=True)
    config = serializers.CharField(read_only=True)
    index_name = serializers.CharField(read_only=True)
    url = serializers.CharField(read_only=True)
    pages_crawled = serializers.IntegerField(read_only=True)
    harvest_rate = serializers.FloatField(read_only=True)
    location = serializers.CharField(read_only=True)

    class Meta:
        model = Crawl


class CrawlModelSerializer(SlugModelSerializer):
    model = serializers.FileField(use_url=False)
    features = serializers.FileField(use_url=False)

    class Meta:
        model = CrawlModel


"""
Viewset Classes.

Filtering is provided by django-filter.

Backend settings are in common_settings.py under REST_FRAMEWORK. Setting is:
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)

This backend is supplied to every viewset by default. Alter query fields by adding
or removing items from filter_fields
"""
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_fields = ('id', 'slug', 'name',)


class CrawlViewSet(viewsets.ModelViewSet):
    queryset = Crawl.objects.all()
    serializer_class = CrawlSerializer
    filter_fields = ('id', 'slug', 'name', 'description', 'status', 'project',
        'crawl_model', 'crawler')


class CrawlModelViewSet(viewsets.ModelViewSet):
    queryset = CrawlModel.objects.all()
    serializer_class = CrawlModelSerializer
    filter_fields = ('id', 'slug', 'name', 'project')


router = routers.DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"crawls", CrawlViewSet)
router.register(r"crawl_models", CrawlModelViewSet)
