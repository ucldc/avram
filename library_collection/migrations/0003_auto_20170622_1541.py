# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0002_add_note_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='merritt_id',
            field=models.CharField(help_text=b'Merritt Id (ARK)', max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='harvest_exception_notes',
            field=models.TextField(help_text=b'Notes on processing quirks', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='harvest_type',
            field=models.CharField(default=b'X', max_length=3, choices=[(b'X', b'None'), (b'OAC', b'Legacy OAC'), (b'OAI', b'OAI-PMH'), (b'SLR', b'Solr Index'), (b'MRC', b'MARC21'), (b'NUX', b'Shared DAMS'), (b'ALX', b'Aleph MARC XML'), (b'SFX', b'UCSF XML Search Results (tobacco)'), (b'UCB', b'Solr Generic - cursorMark'), (b'PRE', b'Preservica CMIS Atom Feed'), (b'FLK', b'Flickr Api All Public Photos'), (b'YTB', b'YouTube Api - Playlist Videos'), (b'TBD', b'Harvest type TBD')]),
        ),
    ]
