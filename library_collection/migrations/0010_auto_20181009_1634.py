# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0009_collection_merritt_extra_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='harvest_type',
            field=models.CharField(default=b'X', max_length=3, choices=[(b'X', b'None'), (b'OAC', b'Legacy OAC'), (b'OAI', b'OAI-PMH'), (b'SLR', b'Solr Index'), (b'MRC', b'MARC21'), (b'NUX', b'Shared DAMS'), (b'ALX', b'Aleph MARC XML'), (b'SFX', b'UCSF XML Search Results (tobacco)'), (b'UCB', b'Solr Generic - cursorMark'), (b'PRE', b'Preservica CMIS Atom Feed'), (b'FLK', b'Flickr Api All Public Photos'), (b'YTB', b'YouTube Api - Playlist Videos'), (b'XML', b'XML File'), (b'EMS', b'eMuseum API'), (b'UCD', b'UC Davis JSON')]),
        ),
    ]
