# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-12-19 20:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0023_auto_20231102_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='harvest_type',
            field=models.CharField(choices=[('X', 'None'), ('ETL', 'Rikolti ETL'), ('OAC', 'Legacy OAC'), ('OAI', 'OAI-PMH'), ('SLR', 'Solr Index'), ('MRC', 'MARC21'), ('NUX', 'Shared DAMS'), ('ALX', 'Aleph MARC XML'), ('SFX', 'UCSF XML Search Results (tobacco)'), ('UCB', 'Solr Generic - cursorMark'), ('PRE', 'Preservica CMIS Atom Feed'), ('FLK', 'Flickr Api All Public Photos'), ('YTB', 'YouTube Api - Playlist Videos'), ('XML', 'XML File'), ('EMS', 'eMuseum API'), ('UCD', 'UC Davis JSON'), ('IAR', 'Internet Archive API'), ('PRA', 'Preservica API')], default='X', max_length=3),
        ),
    ]
