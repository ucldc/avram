# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='date_last_harvested',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='harvest_exception_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='harvest_frequency',
            field=models.DurationField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='files_in_dams',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='collection',
            name='files_in_hand',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='collection',
            name='formats',
            field=models.ManyToManyField(help_text=b'File formats for DAMS ingest', to='library_collection.Format', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='metadata_in_dams',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='collection',
            name='qa_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='collection',
            name='repository',
            field=models.ManyToManyField(to='library_collection.Repository', verbose_name=b'Unit', blank=True),
        ),
        migrations.AlterField(
            model_name='repository',
            name='campus',
            field=models.ManyToManyField(to='library_collection.Campus', blank=True),
        ),
    ]
