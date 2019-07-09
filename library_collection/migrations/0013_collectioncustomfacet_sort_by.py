# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-08 23:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0012_auto_20190708_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectioncustomfacet',
            name='sort_by',
            field=models.CharField(choices=[('count', 'number of results'), ('value', 'alphanumeric order')], default='count', max_length=20),
        ),
    ]