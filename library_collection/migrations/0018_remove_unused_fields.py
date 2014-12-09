# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Need'
        db.delete_table(u'library_collection_need')

        # Deleting model 'Restriction'
        db.delete_table(u'library_collection_restriction')

        # Deleting model 'Status'
        db.delete_table(u'library_collection_status')

        # Deleting field 'Collection.status'
        db.delete_column(u'library_collection_collection', 'status_id')

        # Deleting field 'Collection.need_for_dams'
        db.delete_column(u'library_collection_collection', 'need_for_dams_id')

        # Deleting field 'Collection.metadata_level'
        db.delete_column(u'library_collection_collection', 'metadata_level')

        # Deleting field 'Collection.access_restrictions'
        db.delete_column(u'library_collection_collection', 'access_restrictions_id')

        # Deleting field 'Collection.phase_one'
        db.delete_column(u'library_collection_collection', 'phase_one')

        # Deleting field 'Collection.url_oai'
        db.delete_column(u'library_collection_collection', 'url_oai')

        # Deleting field 'Collection.appendix'
        db.delete_column(u'library_collection_collection', 'appendix')

        # Deleting field 'Collection.collection_type'
        db.delete_column(u'library_collection_collection', 'collection_type')

        # Deleting field 'Collection.url_was'
        db.delete_column(u'library_collection_collection', 'url_was')

        # Deleting field 'Collection.metadata_standard'
        db.delete_column(u'library_collection_collection', 'metadata_standard')


    def backwards(self, orm):
        # Adding model 'Need'
        db.create_table(u'library_collection_need', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'library_collection', ['Need'])

        # Adding model 'Restriction'
        db.create_table(u'library_collection_restriction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'library_collection', ['Restriction'])

        # Adding model 'Status'
        db.create_table(u'library_collection_status', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'library_collection', ['Status'])

        # Adding field 'Collection.status'
        db.add_column(u'library_collection_collection', 'status',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['library_collection.Status'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Collection.need_for_dams'
        db.add_column(u'library_collection_collection', 'need_for_dams',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['library_collection.Need'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Collection.metadata_level'
        db.add_column(u'library_collection_collection', 'metadata_level',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Collection.access_restrictions'
        db.add_column(u'library_collection_collection', 'access_restrictions',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['library_collection.Restriction'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Collection.phase_one'
        db.add_column(u'library_collection_collection', 'phase_one',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Collection.url_oai'
        db.add_column(u'library_collection_collection', 'url_oai',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Collection.appendix'
        db.add_column(u'library_collection_collection', 'appendix',
                      self.gf('django.db.models.fields.CharField')(default='?', max_length=1),
                      keep_default=False)

        # Adding field 'Collection.collection_type'
        db.add_column(u'library_collection_collection', 'collection_type',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1, blank=True),
                      keep_default=False)

        # Adding field 'Collection.url_was'
        db.add_column(u'library_collection_collection', 'url_was',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Collection.metadata_standard'
        db.add_column(u'library_collection_collection', 'metadata_standard',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


    models = {
        u'library_collection.campus': {
            'Meta': {'object_name': 'Campus'},
            'ark': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'library_collection.collection': {
            'Meta': {'object_name': 'Collection'},
            'campus': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['library_collection.Campus']", 'symmetrical': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enrichments_item': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'extent': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'files_in_dams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'files_in_hand': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'formats': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['library_collection.Format']", 'null': 'True', 'blank': 'True'}),
            'harvest_extra_data': ('django.db.models.fields.CharField', [], {'max_length': '511', 'blank': 'True'}),
            'harvest_type': ('django.db.models.fields.CharField', [], {'default': "'X'", 'max_length': '3'}),
            'hosted': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata_in_dams': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'qa_completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ready_for_publication': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repository': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['library_collection.Repository']", 'null': 'True', 'blank': 'True'}),
            'rights_statement': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rights_status': ('django.db.models.fields.CharField', [], {'default': "'UN'", 'max_length': '3'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "'name'", 'overwrite': 'False'})
        }
    }

    complete_apps = ['library_collection']