# Generated by Django 3.2.23 on 2024-03-06 21:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library_collection', '0024_auto_20231219_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='HarvestTrigger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dag_id', models.CharField(max_length=255)),
                ('hostname', models.CharField(max_length=255)),
                ('stdout', models.TextField(blank=True)),
                ('stderr', models.TextField(blank=True)),
                ('dag_run_id', models.CharField(blank=True, max_length=255, null=True)),
                ('airflow_execution_time', models.DateTimeField(blank=True, null=True)),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library_collection.collection')),
            ],
        ),
        migrations.CreateModel(
            name='HarvestRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('deferred', 'deferred'), ('failed', 'failed'), ('queued', 'queued'), ('removed', 'removed'), ('restarting', 'restarting'), ('running', 'running'), ('scheduled', 'scheduled'), ('shutdown', 'shutdown'), ('skipped', 'skipped'), ('success', 'success'), ('up_for_reschedule', 'up for reschedule'), ('up_for_retry', 'up for retry'), ('upstream_failed', 'upstream failed'), ('no_status', 'no status')], default='X', max_length=24)),
                ('notes', models.TextField(blank=True)),
                ('harvest_trigger', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='library_collection.harvesttrigger')),
            ],
        ),
    ]
