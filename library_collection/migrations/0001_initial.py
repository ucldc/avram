# -*- coding: utf-8 -*-
from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=4)),
                ('position', models.IntegerField(default=0)),
                ('ark', models.CharField(max_length=255, blank=True)),
                ('google_analytics_tracking_code', models.CharField(help_text=b'Enable tracking of your digital assets hosted in the UCLDC by entering your Google Analytics tracking code.', max_length=64, blank=True)),
            ],
            options={
                'verbose_name_plural': 'campuses',
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'Collection Title')),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from=('name', 'description'), editable=False, blank=True)),
                ('description', models.TextField(blank=True)),
                ('local_id', models.CharField(help_text=b'used for google analytics subsetting', max_length=1028, blank=True)),
                ('url_local', models.URLField(help_text=b'Collection homepage URL', max_length=255, blank=True)),
                ('url_oac', models.URLField(help_text=b'OAC finding aid URL', max_length=255, blank=True)),
                ('url_harvest', models.URLField(max_length=255, verbose_name=b'Harvest Endpoint', blank=True)),
                ('hosted', models.CharField(help_text=b'Indicate format and output', max_length=255, verbose_name=b'Existing metadata (Format/Output)', blank=True)),
                ('extent', models.BigIntegerField(help_text=b'must be entered in bytes, will take abbreviations later', null=True, blank=True)),
                ('harvest_type', models.CharField(default=b'X', max_length=3, choices=[(b'X', b'None'), (b'OAC', b'Legacy OAC'), (b'OAI', b'OAI-PMH'), (b'SLR', b'Solr Index'), (b'MRC', b'MARC21'), (b'NUX', b'Shared DAMS'), (b'ALX', b'Aleph MARC XML'), (b'SFX', b'UCSF XML Search Results (tobacco)'), (b'UCB', b'UCB Blacklight Solr'), (b'PRE', b'Preservica CMIS Atom Feed'), (b'TBD', b'Harvest type TBD')])),
                ('harvest_extra_data', models.CharField(help_text=b'extra text data needed for the particular type of harvest.', max_length=511, blank=True)),
                ('enrichments_item', models.TextField(help_text=b'Enhancement chain to run on individual harvested items.', blank=True)),
                ('staging_notes', models.TextField(default=b'', help_text=b'Possible support needed by contributor', blank=True)),
                ('files_in_hand', models.BooleanField()),
                ('files_in_dams', models.BooleanField()),
                ('metadata_in_dams', models.BooleanField()),
                ('qa_completed', models.BooleanField()),
                ('ready_for_publication', models.BooleanField(default=False)),
                ('featured', models.BooleanField(default=False, help_text=b'Collection featured on repository home page')),
                ('rights_status', models.CharField(default=b'X', max_length=3, choices=[(b'CR', b'copyrighted'), (b'PD', b'public domain'), (b'UN', b'copyright unknown'), (b'X', b'-----')])),
                ('rights_statement', models.TextField(blank=True)),
                ('dcmi_type', models.CharField(default=b'X', help_text=b'DCMI Type for objects in this collection', max_length=1, choices=[(b'C', b'Collection'), (b'D', b'Dataset'), (b'E', b'Event'), (b'I', b'Image'), (b'R', b'Interactive Resource'), (b'F', b'Moving Image'), (b'V', b'Service'), (b'S', b'Software'), (b'A', b'Sound'), (b'T', b'Text'), (b'P', b'Physical Object'), (b'X', b'-----')])),
                ('campus', models.ManyToManyField(to='library_collection.Campus', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CollectionCustomFacet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('facet_field', models.CharField(max_length=20, choices=[(b'contributor_ss', b'contributor'), (b'coverage_ss', b'coverage'), (b'creator_ss', b'creator'), (b'date_ss', b'date'), (b'extent_ss', b'extent'), (b'format_ss', b'format'), (b'genre_ss', b'genre'), (b'language_ss', b'language'), (b'location_ss', b'location'), (b'publisher_ss', b'publisher'), (b'relation_ss', b'relation'), (b'rights_ss', b'rights'), (b'rights_holder_ss', b'rights_holder'), (b'rights_note_ss', b'rights_note'), (b'rights_date_ss', b'rights_date'), (b'source_ss', b'source'), (b'subject_ss', b'subject'), (b'temporal_ss', b'temporal')])),
                ('label', models.CharField(max_length=255)),
                ('collection', models.ForeignKey(to='library_collection.Collection', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', django_extensions.db.fields.AutoSlugField(populate_from='name', editable=False, blank=True)),
                ('ark', models.CharField(max_length=255, blank=True)),
                ('google_analytics_tracking_code', models.CharField(help_text=b'Enable tracking of your digital assets hosted in the UCLDC by entering your Google Analytics tracking code.', max_length=64, blank=True)),
                ('campus', models.ManyToManyField(to='library_collection.Campus', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'repositories',
            },
        ),
        migrations.AddField(
            model_name='collection',
            name='formats',
            field=models.ManyToManyField(help_text=b'File formats for DAMS ingest', to='library_collection.Format', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='repository',
            field=models.ManyToManyField(to='library_collection.Repository', null=True, verbose_name=b'Unit', blank=True),
        ),
    ]
