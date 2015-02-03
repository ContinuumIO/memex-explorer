# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import crawl_space.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('base', '__first__'),
        ('crawl_space', '0006_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataModel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('model', models.FileField(upload_to=crawl_space.models.DataModel.get_upload_path)),
                ('features', models.FileField(upload_to=crawl_space.models.DataModel.get_upload_path)),
                ('project', models.ForeignKey(to='base.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='crawl',
            name='data_model',
            field=models.ForeignKey(default=1, to='crawl_space.DataModel'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='crawl',
            name='name',
            field=models.CharField(max_length=64, unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9 ]+$', 'Only numbers, letters, and spaces are allowed.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='crawl',
            name='slug',
            field=models.SlugField(max_length=64, unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='crawl',
            name='status',
            field=models.CharField(max_length=64, default='Not started'),
            preserve_default=True,
        ),
    ]
