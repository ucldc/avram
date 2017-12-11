# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0005_auto_20171211_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='disqus_shortname',
            field=models.CharField(help_text=b'find in disqus admin', max_length=64, blank=True),
        ),
    ]
