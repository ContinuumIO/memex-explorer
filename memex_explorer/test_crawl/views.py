import random

from django.views.generic.base import TemplateView
from test_crawl.words import CATS, DOGS

class ContentView(TemplateView):

    template_name = "test_crawl/content.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(ContentView, self).get_context_data(*args, **kwargs)

        content_id = int(self.kwargs['content_id'])
        
        if (content_id % 2):
            context['words'] = ' '.join(random.sample(CATS, 1000))
        else:
            context['words'] = ' '.join(random.sample(DOGS, 1000))

        context['project_slug'] = self.kwargs['project_slug']
        context['link_ids'] = random.sample(xrange(content_id, 50), min(10, 49-content_id))

        return context
