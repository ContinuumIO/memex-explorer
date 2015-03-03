import os
from os.path import join
import sys
import json

import subprocess

from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.apps import apps
from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from base.models import Project
from apps.crawl_space.models import Crawl, CrawlModel
from apps.crawl_space.forms import AddCrawlForm, AddCrawlModelForm, CrawlSettingsForm

from apps.crawl_space.utils import touch

from apps.crawl_space.viz.plot import AcheDashboard


class ProjectObjectMixin(ContextMixin):

    def get_project(self):
        return Project.objects.get(slug=self.kwargs['project_slug'])

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProjectObjectMixin, self).get_context_data(**kwargs)
        context['project'] = self.get_project()
        return context


class AddCrawlView(SuccessMessageMixin, ProjectObjectMixin, CreateView):

    form_class = AddCrawlForm
    template_name = "crawl_space/add_crawl.html"
    success_message = "Crawl %(name)s was saved successfully."

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        form.instance.project = self.get_project()
        return super(AddCrawlView, self).form_valid(form)


class ListCrawlsView(ProjectObjectMixin, ListView):
    model = Crawl
    template_name = "crawl_space/crawls.html"


class CrawlView(ProjectObjectMixin, DetailView):
    model = Crawl
    template_name = "crawl_space/crawl.html"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CrawlView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        crawl_model = self.get_object()

        # Start
        if request.POST['action'] == "start":
            project_slug = self.kwargs['project_slug']
            crawl_slug = self.kwargs['crawl_slug']

            call = ["python",
                    "apps/crawl_space/crawl_supervisor.py",
                    "--project", project_slug,
                    "--crawl", crawl_slug]

            subprocess.Popen(call)

            crawl_model.status = "starting"
            crawl_model.save()
            return HttpResponse(json.dumps(dict(
                    status="starting")),
                content_type="application/json")

                
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
            project=self.get_project(),
            slug=self.kwargs['crawl_slug'])

    def get_context_data(self, **kwargs):
        context = super(CrawlView, self).get_context_data(**kwargs)
        context['project'] = self.get_project()
        if self.get_object().crawler == "ache":
            plots = AcheDashboard(self.get_object()).get_plots()
            context['scripts'] = plots['scripts']
            context['divs'] = plots['divs']
        return context


class CrawlSettingsView(SuccessMessageMixin, ProjectObjectMixin, UpdateView):

    model = Crawl
    form_class = CrawlSettingsForm
    success_message = "Crawl %(name)s was edited successfully."
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_object(self):
        return Crawl.objects.get(
            project=self.get_project(),
            slug=self.kwargs['crawl_slug'])


class AddCrawlModelView(SuccessMessageMixin, ProjectObjectMixin, CreateView):
    form_class = AddCrawlModelForm
    template_name = "crawl_space/add_crawl_model.html"
    success_message = "Crawl model %(name)s was added successfully."

    def form_valid(self, form):
        form.instance.project = self.get_project()
        return super(AddCrawlModelView, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class DeleteCrawlModelView(SuccessMessageMixin, ProjectObjectMixin, DeleteView):
    model = CrawlModel
    success_message = "Crawl model %(name)s was deleted successfully."

    def get_success_url(self):
        return self.get_project().get_absolute_url()

    def get_object(self):
        return CrawlModel.objects.get(
            project=self.get_project(),
            slug=self.kwargs['model_slug'])

