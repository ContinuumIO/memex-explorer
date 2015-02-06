from django.forms import ModelForm, RadioSelect, Select

from crawl_space.models import Crawl, CrawlModel


class AddCrawlForm(ModelForm):
    class Meta:
        model = Crawl
        fields = ['name', 'description', 'crawler', 'seeds_list', 'crawl_model']
        widgets = {'crawler': RadioSelect, 'crawl_model': Select}


class AddCrawlModelForm(ModelForm):
    class Meta:
        model = CrawlModel
        fields = ['name', 'model', 'features']

