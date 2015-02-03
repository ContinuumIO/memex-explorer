from django.conf.urls import patterns, url

from crawl_space import views

urlpatterns = patterns('',
    url(r'^add_crawl/$', views.AddCrawlView.as_view(), name='add_crawl'),
    url(r'^add_data_model/$', views.AddDataModelView.as_view(), name='add_data_model'),
    url(r'^(?P<crawl_slug>[\w-]+)/$', views.CrawlView.as_view(), name='crawl'),
)
