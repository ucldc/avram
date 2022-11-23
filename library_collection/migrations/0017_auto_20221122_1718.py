# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-11-22 23:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0016_auto_20201201_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='solr_count',
            field=models.IntegerField(default=0, help_text='Number of items in Solr index'),
        ),
        migrations.AddField(
            model_name='collection',
            name='solr_last_updated',
            field=models.DateTimeField(blank=True, help_text='Last time Solr count was updated', null=True),
        ),
    ]
