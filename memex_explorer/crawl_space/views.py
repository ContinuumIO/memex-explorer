import json
import django_rq

from redis.exceptions import ConnectionError

from django.views import generic
from django.apps import apps
from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from base.models import Project
from crawl_space.models import Crawl
from crawl_space.forms import AddCrawlForm, AddDataModelForm

from crawl_space.crawls import AcheCrawl


class AddCrawlView(generic.edit.CreateView):
    form_class = AddCrawlForm
    template_name = "crawl_space/add_crawl.html"

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        form.instance.project = Project.objects.get(slug=self.kwargs['slug'])
        return super().form_valid(form)


class CrawlView(generic.DetailView):
    model = Crawl
    template_name = "crawl_space/crawl.html"


    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


    def post(self, request, *args, **kwargs):
        if request.POST['action'] == "start":
            # from ipsh import ipsh; ipsh()
            crawl_model = self.get_object()
            queue = django_rq.get_queue('default')


            ache_crawl = AcheCrawl(crawl_model)
            try:
                queue.enqueue(ache_crawl.crawl)
            except ConnectionError as e:
                return HttpResponse(json.dumps(dict(
                        status="error",
                        error="start the redis server")),
                    content_type="application/json")



        # TESTING reflect POST request
        return HttpResponse(json.dumps(dict(
                args=args,
                kwargs=kwargs,
                post=request.POST)),
            content_type="application/json")



    def get_object(self):
        return Crawl.objects.get(
            project=Project.objects.get(slug=self.kwargs['slug']),
            slug=self.kwargs['crawl_slug'])


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        return context


class AddDataModelView(generic.edit.CreateView):
    form_class = AddDataModelForm
    template_name = "crawl_space/add_data_model.html"

    def form_valid(self, form):
        form.instance.project = Project.objects.get(slug=self.kwargs['slug'])
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

