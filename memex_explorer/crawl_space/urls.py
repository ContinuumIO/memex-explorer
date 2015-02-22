"""Crawl space url routes.

Each of these url patterns is built off a project URL-

    /project/<project_slug>

-and belongs to the "crawl_space" namespace. See `base.urls` for an
explanation of the dynamic route generation.

URLs
----

project/<project_slug>/
    add_crawl/
    add_crawl_model/
    crawls/
    crawls/<crawl_slug/

"""

from django.conf.urls import patterns, url

from apps.crawl_space import views

urlpatterns = patterns('',
    url(r'^add_crawl/$', views.AddCrawlView.as_view(),
        name='add_crawl'),

    url(r'^add_crawl_model/$', views.AddCrawlModelView.as_view(),
        name='add_crawl_model'),

    url(r'^(?P<model_slug>[\w-]+)/delete/$', views.DeleteCrawlModelView.as_view(),
        name='delete_crawl_model'),

    url(r'^crawls/$', views.ListCrawlsView.as_view(),
        name='crawls'),

    url(r'^crawls/(?P<crawl_slug>[\w-]+)/$', views.CrawlView.as_view(),
        name='crawl')
)

