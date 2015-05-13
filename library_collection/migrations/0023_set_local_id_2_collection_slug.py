# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for c in orm.Collection.objects.all():
            c.local_id = c.slug
            c.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'library_collection.campus': {
            'Meta': {'object_name': 'Campus'},
            'ark': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'google_analytics_tracking_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'library_collection.collection': {
            'Meta': {'object_name': 'Collection'},
            'campus': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['library_collection.Campus']", 'symmetrical': 'False', 'blank': 'True'}),
            'dcmi_type': ('django.db.models.fields.CharField', [], {'default': "'X'", 'max_length': '1'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enrichments_item': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'extent': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'files_in_dams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'files_in_hand': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'formats': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['library_collection.Format']", 'null': 'True', 'blank': 'True'}),
            'harvest_extra_data': ('django.db.models.fields.CharField', [], {'max_length': '511', 'blank': 'True'}),
            'harvest_type': ('django.db.models.fields.CharField', [], {'default': "'X'", 'max_length': '3'}),
            'hosted': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_id': ('django.db.models.fields.CharField', [], {'max_length': '1028', 'blank': 'True'}),
            'metadata_in_dams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'qa_completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ready_for_publication': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repository': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['library_collection.Repository']", 'null': 'True', 'blank': 'True'}),
            'rights_statement': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rights_status': ('django.db.models.fields.CharField', [], {'default': "'X'", 'max_length': '3'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('name', 'description')", 'overwrite': 'False'}),
            'staging_notes': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'url_harvest': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'url_local': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'url_oac': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'library_collection.format': {
            'Meta': {'object_name': 'Format'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'library_collection.repository': {
            'Meta': {'object_name': 'Repository'},
            'ark': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'campus': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['library_collection.Campus']", 'null': 'True', 'blank': 'True'}),
            'google_analytics_tracking_code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "'name'", 'overwrite': 'False'})
        }
    }

    complete_apps = ['library_collection']
    symmetrical = True
