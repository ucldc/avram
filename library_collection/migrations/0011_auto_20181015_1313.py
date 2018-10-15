# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0010_auto_20181009_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='aeon_prod',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='repository',
            name='aeon_test',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
