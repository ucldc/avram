# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Format'
        db.create_table(u'library_collection_format', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'library_collection', ['Format'])

        # Adding field 'Collection.staging_notes'
        db.add_column(u'library_collection_collection', 'staging_notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Collection.files_in_hand'
        db.add_column(u'library_collection_collection', 'files_in_hand',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Collection.files_in_dams'
        db.add_column(u'library_collection_collection', 'files_in_dams',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Collection.metadata_in_dams'
        db.add_column(u'library_collection_collection', 'metadata_in_dams',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Collection.qa_completed'
        db.add_column(u'library_collection_collection', 'qa_completed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Collection.ready_for_publication'
        db.add_column(u'library_collection_collection', 'ready_for_publication',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Collection.rights_status'
        db.add_column(u'library_collection_collection', 'rights_status',
                      self.gf('django.db.models.fields.CharField')(default='UN', max_length=3),
                      keep_default=False)

        # Adding field 'Collection.rights_statement'
        db.add_column(u'library_collection_collection', 'rights_statement',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding M2M table for field formats on 'Collection'
        m2m_table_name = db.shorten_name(u'library_collection_collection_formats')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('collection', models.ForeignKey(orm[u'library_collection.collection'], null=False)),
            ('format', models.ForeignKey(orm[u'library_collection.format'], null=False))
        ))
        db.create_unique(m2m_table_name, ['collection_id', 'format_id'])


    def backwards(self, orm):
        # Deleting model 'Format'
        db.delete_table(u'library_collection_format')

        # Deleting field 'Collection.staging_notes'
        db.delete_column(u'library_collection_collection', 'staging_notes')

        # Deleting field 'Collection.files_in_hand'
        db.delete_column(u'library_collection_collection', 'files_in_hand')

        # Deleting field 'Collection.files_in_dams'
        db.delete_column(u'library_collection_collection', 'files_in_dams')

        # Deleting field 'Collection.metadata_in_dams'
        db.delete_column(u'library_collection_collection', 'metadata_in_dams')

        # Deleting field 'Collection.qa_completed'
        db.delete_column(u'library_collection_collection', 'qa_completed')

        # Deleting field 'Collection.ready_for_publication'
        db.delete_column(u'library_collection_collection', 'ready_for_publication')

        # Deleting field 'Collection.rights_status'
        db.delete_column(u'library_collection_collection', 'rights_status')

        # Deleting field 'Collection.rights_statement'
        db.delete_column(u'library_collection_collection', 'rights_statement')

        # Removing M2M table for field formats on 'Collection'
        db.delete_table(db.shorten_name(u'library_collection_collection_formats'))


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
            'access_restrictions': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['library_collection.Restriction']", 'null': 'True', 'blank': 'True'}),
            'appendix': ('django.db.models.fields.CharField', [], {'default': "'?'", 'max_length': '1'}),
            'campus': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['library_collection.Campus']", 'symmetrical': 'False', 'blank': 'True'}),
            'collection_type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
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
            'metadata_level': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'metadata_standard': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'need_for_dams': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['library_collection.Need']", 'null': 'True', 'blank': 'True'}),
            'phase_one': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'qa_completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ready_for_publication': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repository': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['library_collection.Repository']", 'null': 'True', 'blank': 'True'}),
            'rights_statement': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rights_status': ('django.db.models.fields.CharField', [], {'default': "'UN'", 'max_length': '3'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('name', 'description')", 'overwrite': 'False'}),
            'staging_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['library_collection.Status']", 'null': 'True', 'blank': 'True'}),
            'url_harvest': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'url_local': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'url_oac': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'url_oai': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'url_was': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'library_collection.format': {
            'Meta': {'object_name': 'Format'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'library_collection.need': {
            'Meta': {'object_name': 'Need'},
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
