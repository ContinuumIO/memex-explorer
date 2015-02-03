from django.forms import ModelForm, RadioSelect, Select

from crawl_space.models import Crawl, DataModel


class AddCrawlForm(ModelForm):
    class Meta:
        model = Crawl
        fields = ['name', 'description', 'crawler', 'seeds_list', 'data_model']
        widgets = {'crawler': RadioSelect, 'data_model': Select}


class AddDataModelForm(ModelForm):
    class Meta:
        model = DataModel
        fields = ['name', 'model', 'features']

