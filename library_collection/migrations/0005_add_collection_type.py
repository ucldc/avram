# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Collection.collection_type'
        db.add_column(u'library_collection_collection', 'collection_type',
                      self.gf('django.db.models.fields.CharField')(default='A', max_length=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Collection.collection_type'
        db.delete_column(u'library_collection_collection', 'collection_type')


    models = {
        u'library_collection.campus': {
            'Meta': {'object_name': 'Campus'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'library_collection.collection': {
            'Meta': {'object_name': 'Collection'},
            'access_restrictions': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['library_collection.Restriction']", 'null': 'True', 'blank': 'True'}),
            'appendix': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'campus': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['library_collection.Campus']", 'symmetrical': 'False'}),
            'collection_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'extent': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hosted': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata_level': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'metadata_standard': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'need_for_dams': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['library_collection.Need']", 'null': 'True', 'blank': 'True'}),
            'oai_set_spec': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'phase_one': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('name', 'description')", 'overwrite': 'False'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['library_collection.Status']", 'null': 'True', 'blank': 'True'}),
            'url_local': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'url_oac': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'url_oai': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'url_was': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'library_collection.need': {
            'Meta': {'object_name': 'Need'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'library_collection.restriction': {
            'Meta': {'object_name': 'Restriction'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'library_collection.status': {
            'Meta': {'object_name': 'Status'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['library_collection']