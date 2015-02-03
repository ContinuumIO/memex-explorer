# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import crawl_space.models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl_space', '0007_auto_20150202_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datamodel',
            name='features',
            field=models.FileField(upload_to=crawl_space.models.DataModel.get_upload_path, validators=[crawl_space.models.validate_features_file]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='datamodel',
            name='model',
            field=models.FileField(upload_to=crawl_space.models.DataModel.get_upload_path, validators=[crawl_space.models.validate_model_file]),
            preserve_default=True,
        ),
    ]
