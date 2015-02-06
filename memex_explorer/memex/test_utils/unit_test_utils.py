# Test
from django.test import TestCase, Client

# Utility
from django.core.urlresolvers import reverse

def form_errors(response):
    return response.context['form'].errors

def get_object(response):
    return response.context['object']

class UnitTestSkeleton(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()


    @classmethod
    def get(cls, view_name, *args, **kwargs):
        if 'slugs' in kwargs:
            slugs = kwargs.pop('slugs')
            return cls.client.get(
                reverse(view_name, kwargs=slugs),
                *args, follow=True, **kwargs)
        else:
            return cls.client.get(reverse(view_name),
                *args, follow=True, **kwargs)

    @classmethod
    def post(cls, view_name, *args, **kwargs):
        if 'slugs' in kwargs:
            slugs = kwargs.pop('slugs')
            return cls.client.post(
                reverse(view_name, kwargs=slugs),
                *args, follow=True, **kwargs)
        else:
            return cls.client.post(reverse(view_name),
                *args, follow=True, **kwargs)
