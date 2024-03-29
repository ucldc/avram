# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-04-14 19:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0020_collection_rikolti_mapper_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='extent',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='files_in_dams',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='files_in_hand',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='formats',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='harvest_frequency',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='hosted',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='metadata_in_dams',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='qa_completed',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='staging_notes',
        ),
        migrations.DeleteModel(
            name='Format',
        ),
    ]
