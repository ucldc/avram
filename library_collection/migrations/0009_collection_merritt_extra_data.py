# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0008_auto_20180122_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='merritt_extra_data',
            field=models.CharField(help_text=b'nuxeo path for Merritt harvest (usually the same as Harvest extra data)', max_length=511, blank=True),
        ),
    ]
