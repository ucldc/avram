# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-11-02 20:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0022_auto_20231102_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='harvest_exception_notes',
            field=models.TextField(blank=True, default='', help_text='Notes on processing quirks'),
            preserve_default=False,
        ),
    ]