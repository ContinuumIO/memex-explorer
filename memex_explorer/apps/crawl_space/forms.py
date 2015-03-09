from base.forms import CrispyModelForm

from django.forms import ModelForm, RadioSelect, Select, FileInput
from crispy_forms.layout import Layout, Fieldset, Submit, HTML
from crispy_forms.bootstrap import InlineRadios, FormActions

from django.utils.translation import ugettext_lazy as _

from apps.crawl_space.models import Crawl, CrawlModel

from django.core.exceptions import ValidationError
from django.utils.text import slugify


class AddCrawlForm(CrispyModelForm):
    """Add crawl form, with a user-specified crispy layout."""

    def __init__(self, *args, **kwargs):
        super(AddCrawlForm, self).__init__(*args, **kwargs)
        self.set_layout()

    def set_layout(self):
        """Called in __init__ to register a custom layout."""

        self.helper.layout = Layout(
            Fieldset(None,
                'name',
                'description',
                InlineRadios('crawler'),
                'crawl_model',
                'seeds_list',
                FormActions(Submit('submit', "Submit"))
            )
        )

    def clean_crawl_model(self):
        crawl_model = self.cleaned_data['crawl_model']
        try:
            crawler = self.cleaned_data['crawler']
        except KeyError:
            raise ValidationError("Incorrect crawler type.")
        if not crawl_model and crawler == 'ache':
            raise ValidationError("Ache Crawls require a crawl model.")
        return crawl_model

    def clean_name(self):
        name = self.cleaned_data['name']
        if slugify(unicode(name)) in [x.slug for x in Crawl.objects.all()]:
            raise ValidationError("Crawl with this Name already exists.")
        return name

    class Meta:
        model = Crawl
        fields = ['name', 'description', 'crawler',
                  'crawl_model', 'seeds_list']
        widgets = {'crawl_model': Select}


class CrawlSettingsForm(CrispyModelForm):

    def __init__(self, *args, **kwargs):
        self.crawl_instance = kwargs["instance"]
        super(CrawlSettingsForm, self).__init__(*args, **kwargs)
        self.set_layout()

    def set_layout(self):
        """Called in __init__ to register a custom layout."""

        self.helper.layout = Layout(
            Fieldset(None,
                'name',
                'description',
                FormActions(Submit('submit', "Submit"))
            )
        )

    def clean_name(self):
        new_slug = slugify(unicode(self.cleaned_data["name"]))
        instance_slug = self.crawl_instance.slug
        slugs = [x.slug for x in Crawl.objects.exclude(slug=instance_slug)]
        if new_slug in slugs:
            raise ValidationError("Crawl with this Name already exists.")
        return self.cleaned_data["name"]

    class Meta:
        model = Crawl
        fields = ['name', 'description']


class AddCrawlModelForm(CrispyModelForm):
    """Add crawl model form, with an automatic crispy layout."""

    class Meta:
        model = CrawlModel
        fields = ['name', 'model', 'features']

