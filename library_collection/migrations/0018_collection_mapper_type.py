# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-11-23 00:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0017_auto_20221122_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='mapper_type',
            field=models.CharField(blank=True, help_text='Auto-Generated from Enrichments', max_length=511, null=True),
        ),
    ]