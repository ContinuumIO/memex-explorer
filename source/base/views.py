"""Base views."""
from __future__ import absolute_import

import json
import shutil
import os

from django.shortcuts import render
from django.views import generic
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from base.models import Project, Index
from base.forms import (AddProjectForm, ProjectSettingsForm, AddIndexForm,
    IndexSettingsForm)

from apps.crawl_space.models import Crawl
from apps.crawl_space.settings import CRAWL_PATH
from apps.crawl_space.views import ProjectObjectMixin

from task_manager.file_tasks import upload_zip

import requests


def project_context_processor(request):
    additional_context = {
        'projects': Project.objects.all(),
        'deployment': settings.DEPLOYMENT,
    }
    for app, location in settings.EXTERNAL_APP_LOCATIONS.items():
        additional_context["{}_link".format(app)] = location
    return additional_context


class IndexView(ListView):
    model = Project
    template_name = "base/index.html"


class AboutView(TemplateView):
    template_name = "base/about.html"


class AddProjectView(SuccessMessageMixin, CreateView):
    model = Project
    form_class = AddProjectForm
    template_name = "base/add_project.html"
    success_message = "Project %(name)s was added successfully."

    def get_success_url(self):
        return self.object.get_absolute_url()


class ProjectView(DetailView):
    model = Project
    slug_url_kwarg = 'project_slug'
    template_name = "base/project.html"

    def post(self, request, *args, **kwargs):
        if request.POST['action'] == "index_status":
            statuses = {}
            for x in self.get_object().index_set.all():
                x.status = x.celerytask.task.status
                statuses[x.slug] = x.status
                x.save()
            return HttpResponse(
                json.dumps({"statuses": statuses}),
                content_type="application/json",
            )

        return HttpResponse(
            json.dumps({
                "args": args,
                "kwargs": kwargs,
                "post": request.POST,
            }),
            content_type="application/json",
        )

    def get_object(self):
        return Project.objects.get(slug=self.kwargs['project_slug'])

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        return context


class ProjectSettingsView(SuccessMessageMixin, UpdateView):
    model = Project
    slug_url_kwarg = 'project_slug'
    form_class = ProjectSettingsForm
    success_message = "Project %(name)s was edited successfully."
    template_name_suffix = '_update_form'


class DeleteProjectView(SuccessMessageMixin, DeleteView):
    model = Project
    success_message = "Project %(name)s was deleted successfully."
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        # Remove crawls and folders for crawls.
        # for crawl in self.get_crawls():
        #     shutil.rmtree(os.path.join(CRAWL_PATH, str(crawl.pk)))
        #     crawl.delete()
        return super(DeleteProjectView, self).delete(request, *args, **kwargs)

    def get_object(self):
        return Project.objects.get(slug=self.kwargs['project_slug'])

    def get_crawls(self):
        return Crawl.objects.filter(project=self.get_object())


class ListIndicesView(ProjectObjectMixin, ListView):
    model = Index
    template_name = "base/indices.html"

    def post(self, request, *args, **kwargs):
        if request.POST["get"] == "objects":
            indices = Index.objects.all()
            crawls = Crawl.objects.all()
            return HttpResponse(
                json.dumps({
                    "index_slugs": [x.slug for x in indices],
                    "index_names": [x.name for x in indices],
                    "crawl_slugs": [x.slug for x in crawls],
                    "crawl_names": [x.name for x in crawls],
                }),
                content_type="application/json",
            )

        return HttpResponse(
            json.dumps("Hello!"),
            content_type="application/json",
        )


class AddIndexView(SuccessMessageMixin, ProjectObjectMixin, CreateView):
    model = Index
    form_class = AddIndexForm
    template_name = "base/add_index.html"
    success_message = "Index %(name)s was added successfully."

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        """
        Add a project key:value for the form, then get the object created by
        `form.save`.
        """
        form.instance.project = self.get_project()
        self.object = form.save()
        if hasattr(settings, "TESTING"):
            upload_zip(self.object)
        else:
            upload_zip.delay(self.object)
        return super(AddIndexView, self).form_valid(form)


class IndexSettingsView(SuccessMessageMixin, ProjectObjectMixin, UpdateView):
    model = Index
    slug_url_kwarg = 'index_slug'
    form_class = IndexSettingsForm
    success_message = "Index was edited successfully."
    template_name_suffix = '_update_form'

    def get_index_path(self, index):
        return os.path.join(settings.MEDIA_ROOT, "indices", index.slug)

    def delete_folder_contents(self, folder):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception, e:
                print(e)

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_object(self):
        return Index.objects.get(
            project=self.get_project(),
            slug=self.kwargs['index_slug'])

    def get_context_data(self, **kwargs):
        context = super(IndexSettingsView, self).get_context_data(**kwargs)
        context["name"] = self.get_object().name
        return context

    def form_valid(self, form):
        """
        Add a project key:value for the form, then get the object created by
        `form.save`.
        """
        form.instance.project = self.get_project()
        if hasattr(self.object, "celerytask"):
            self.object.celerytask.delete()
        if os.path.exists(self.get_index_path(self.object)):
            self.delete_folder_contents(self.get_index_path(self.object))
        self.object = form.save()
        # If we are in deployment mode, use the asynced version. If not, use the
        # synced version.
        if hasattr(settings, "TESTING"):
            upload_zip(self.object)
        else:
            upload_zip.delay(self.object)
        return super(IndexSettingsView, self).form_valid(form)


class DeleteIndexView(SuccessMessageMixin, ProjectObjectMixin, DeleteView):
    model = Index
    success_message = "Index was deleted successfully."
    success_url = ""

    def delete(self, request, *args, **kwargs):
        self.success_url = self.get_object().get_absolute_url()
        shutil.rmtree(os.path.dirname(self.get_object().data_folder))
        return super(DeleteIndexView, self).delete(request, *args, **kwargs)

    def get_object(self):
        return Index.objects.get(
            project=self.get_project(),
            slug=self.kwargs['index_slug'])

    def get_context_data(self, **kwargs):
        context = super(IndexSettingsView, self).get_context_data(**kwargs)
        context["name"] = self.get_object().name
        return context


class TadView(ProjectObjectMixin, TemplateView):
    template_name = "base/tad.html"

    def post(self, request, *args, **kwargs):
        if request.POST["get"] == "data":
            payload = {
                "target-location": "Colorado Springs;Colorado;United States",
                "baseline-location": ";Colorado;United States",
                "analysis-start-date": "2014/01/05",
                "analysis-end-date": "2014/02/05",
                "stratify": "false",
            }
            r = requests.post("http://127.0.0.1:5000/event-report", data=json.dumps(payload))
            return HttpResponse(
                json.dumps(r.text),
                content_type="application/json",
            )

        return HttpResponse(
            json.dumps("Nope!"),
            content_type="application/json",
        )
