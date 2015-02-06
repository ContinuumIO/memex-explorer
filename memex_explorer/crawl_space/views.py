import os
import sys
import json

import subprocess

from django.views import generic
from django.apps import apps
from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from base.models import Project
from crawl_space.models import Crawl
from crawl_space.forms import AddCrawlForm, AddCrawlModelForm


from crawl_space.utils import touch, join

class AddCrawlView(generic.edit.CreateView):
    form_class = AddCrawlForm
    template_name = "crawl_space/add_crawl.html"

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        form.instance.project = Project.objects.get(slug=self.kwargs['slug'])
        return super().form_valid(form)


class ListCrawlsView(generic.ListView):
    model = Crawl
    template_name = "crawl_space/crawls.html"

    def get_project(self):
        return Project.objects.get(slug=self.kwargs['slug'])


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_project()
        return context


class CrawlView(generic.DetailView):
    model = Crawl
    template_name = "crawl_space/crawl.html"


    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


    def post(self, request, *args, **kwargs):
        crawl_model = self.get_object()

        # Start
        if request.POST['action'] == "start":
            project_slug = self.kwargs['slug']
            crawl_slug = self.kwargs['crawl_slug']

            call = ["python",
                    "crawl_space/crawl_supervisor.py",
                    "--project", project_slug,
                    "--crawl", crawl_slug]

            # TODO fire start
            # from ipsh import ipsh; ipsh()
            subprocess.Popen(call,
               # env={'PYTHONPATH': os.pathsep.join(sys.path)})
            )

            crawl_model.status = "starting"
            crawl_model.save()

                
        # Stop
        elif request.POST['action'] == "stop":
            # TODO use crawl_model.status as a stop flag
            crawl_path = crawl_model.get_crawl_path()
            touch(join(crawl_path, 'stop'))
            return HttpResponse(json.dumps(dict(
                    status="stopping")),
                content_type="application/json")


        # Update status, statistics
        elif request.POST['action'] == "status":
            return HttpResponse(json.dumps(dict(
                    status=crawl_model.status,
                    harvest_rate=crawl_model.harvest_rate,
                    pages_crawled=crawl_model.pages_crawled,
                    )),
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


class AddCrawlModelView(generic.edit.CreateView):
    form_class = AddCrawlModelForm
    template_name = "crawl_space/add_crawl_model.html"

    def form_valid(self, form):
        form.instance.project = Project.objects.get(slug=self.kwargs['slug'])
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

