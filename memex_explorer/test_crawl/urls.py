"""Test site urls.

URLs
----

project/<project_slug>/
    content/<content_id>/

"""

from django.conf.urls import patterns, url
from test_crawl import views

urlpatterns = patterns('',
    url(r'^content/(?P<content_id>[\w-]+)/$', views.ContentView.as_view(),
        name='content')
)
