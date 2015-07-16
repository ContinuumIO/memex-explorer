"""Base url routes.

This module also dynamically adds url routes to applications present in
INSTALLED_APPS; see the comments below.

URLs
----

/
about/
add_project/
project/

"""

from django.conf.urls import patterns, include, url
from base import views


project_slug = r'^projects/(?P<project_slug>[\w-]+)/'

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^add_project/$', views.AddProjectView.as_view(),
        name='add_project'),
    url(project_slug + r'$', views.ProjectView.as_view(),
        name='project'),
    url(project_slug + r'settings/$', views.ProjectSettingsView.as_view(),
        name='project_settings'),
    url(project_slug + r'tad/$', views.TadView.as_view(),
        name='tad'),
    url(project_slug + r'settings/delete/$', views.DeleteProjectView.as_view(),
        name='delete_project'),
    url(project_slug + r'add_dataset/$', views.AddIndexView.as_view(),
        name='add_index'),
    url(project_slug + r'datasets/$', views.ListIndicesView.as_view(),
        name='indices'),
    url(project_slug + r'datasets/(?P<index_slug>[\w-]+)/settings/$',
        views.IndexSettingsView.as_view(), name='index_settings'),
    url(project_slug + r'datasets/(?P<index_slug>[\w-]+)/settings/delete/$',
        views.DeleteIndexView.as_view(), name='delete_index'),
)


# The following lines build a url route to each application listed in
#   `settings.EXPLORER_APPS`, namespaced appropriately.
#   See <https://github.com/ContinuumIO/memex-explorer/issues/316>

from django.conf import settings

inject_urls = [
    url(project_slug, include('apps.%s.urls' % app, namespace=app))
    for app in settings.EXPLORER_APPS
]

urlpatterns += patterns('', *inject_urls)
