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
        name='project')
)


# The following lines build a url route to each application listed in
#   `settings.EXPLORER_APPS`, namespaced appropriately.
#   See <https://github.com/ContinuumIO/memex-explorer/issues/316>

from django.conf import settings

inject_urls = [
    url(project_slug, include('%s.urls' % app, namespace=app))
    for app in settings.EXPLORER_APPS
]

urlpatterns += patterns('', *inject_urls)
