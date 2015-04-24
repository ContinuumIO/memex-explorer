import os
from os.path import join
import sys
import json
import csv
import subprocess
import shutil
import itertools

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
from apps.crawl_space.settings import CRAWL_PATH, IMAGES_PATH

from task_manager.tika_tasks import create_index


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

    def post(self, request, *args, **kwargs):
        crawl_model = self.get_object()

        # Start
        if request.POST['action'] == "start":
            crawl_model.status = "starting"
            crawl_model.save()

            project_slug = self.kwargs['project_slug']
            crawl_slug = self.kwargs['crawl_slug']

            call = ["python",
                    "apps/crawl_space/crawl_supervisor.py",
                    "--project", project_slug,
                    "--crawl", crawl_slug]

            subprocess.Popen(call)

            return HttpResponse(json.dumps(dict(
                    status="starting")),
                content_type="application/json")


        # Stop
        elif request.POST['action'] == "stop":
            crawl_model.status = 'stopping'
            crawl_model.save()

            crawl_path = crawl_model.get_crawl_path()
            # TODO use crawl_model.status as a stop flag
            touch(join(crawl_path, 'stop'))
            return HttpResponse(json.dumps(dict(
                    status="stopping")),
                content_type="application/json")

        # Dump Images
        elif request.POST['action'] == "dump":
            self.dump_images()
            return HttpResponse("Success")

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

    def dump_images(self):
        self.img_dir = os.path.join(IMAGES_PATH, self.get_object().slug)
        if os.path.exists(self.img_dir):
            shutil.rmtree(self.img_dir)
        else:
            os.makedirs(self.img_dir)

        img_dump_proc = subprocess.Popen(["nutch", "dump", "-outputDir", self.img_dir, "-segment",
                                         os.path.join(self.get_object().get_crawl_path(), 'segments'),"-mimetype",
                                         "image/jpeg", "image/png"]).wait()
        return "Dumping images"

    def get(self, request, *args, **kwargs):
        # Get Relevant Seeds File
        if not request.GET:
            # no url parameters, return regular response
            return super(CrawlView, self).get(request, *args, **kwargs)

        elif 'resource' in request.GET and request.GET['resource'] == "seeds":
            seeds = self.get_ache_dashboard().get_relevant_seeds()
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=relevant_seeds.txt'
            response.write('\n'.join(seeds))
            return response

        elif 'resource' in request.GET and request.GET['resource'] == "initial_seeds":
            seeds = self.get_seeds_list()
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=seeds.txt'
            response.write(''.join(seeds))
            return response

        elif 'resource' in request.GET and request.GET['resource'] == "crawl_log":
            crawl_log = self.get_crawl_log()
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=crawl_log.txt'
            response.write(crawl_log)
            return response

    def get_crawl_log(self):
        log_path = os.path.join(self.get_object().get_crawl_path(), "crawl_proc.log")
        with open(log_path) as f:
            crawl_log = f.readlines()
            return ''.join(crawl_log)

    def get_seeds_path(self):
        if self.get_object().crawler == "nutch":
            seeds_path = os.path.join(self.get_object().seeds_list.path, "seeds")
        elif self.get_object().crawler == "ache":
            seeds_path = self.get_object().seeds_list.path
        else:
            seeds_path = ""
        return seeds_path

    def get_seeds_list(self, lines=None):
        with open(self.get_seeds_path()) as f:
            if lines:
                seeds_list = list(itertools.islice(f, lines))
            else:
                seeds_list = f.readlines()
            return seeds_list

    def get_object(self):
        return Crawl.objects.get(
            project=self.get_project(),
            slug=self.kwargs['crawl_slug'])

    def get_ache_dashboard(self):
        return AcheDashboard(self.get_object())

    def get_context_data(self, **kwargs):
        context = super(CrawlView, self).get_context_data(**kwargs)
        context['project'] = self.get_project()
        context['seeds'] = self.get_seeds_list(10)
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


class DeleteCrawlView(SuccessMessageMixin, ProjectObjectMixin, DeleteView):

    model = Crawl
    success_message = "Crawl %(name)s was deleted successfully."

    def delete(self, request, *args, **kwargs):
        """ Remove crawl folder """
        shutil.rmtree(self.get_object().get_crawl_path())
        return super(DeleteCrawlView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.get_project().get_absolute_url()

    def get_object(self):
        return Crawl.objects.get(project=self.get_project(),
                                 slug=self.kwargs['crawl_slug'])


class DeleteCrawlModelView(SuccessMessageMixin, ProjectObjectMixin, DeleteView):

    model = CrawlModel
    success_message = "Crawl model %(name)s was deleted successfully."

    def get_success_url(self):
        return self.get_project().get_absolute_url()

    def get_object(self):
        return CrawlModel.objects.get(
            project=self.get_project(),
            slug=self.kwargs['model_slug'])

