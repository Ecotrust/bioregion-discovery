# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Languages.cnt'
        db.alter_column('analysis_languages', 'cnt', self.gf('django.db.models.fields.CharField')(max_length=8, null=True))

        # Changing field 'Languages.lmp_class'
        db.alter_column('analysis_languages', 'lmp_class', self.gf('django.db.models.fields.CharField')(max_length=5, null=True))

        # Changing field 'Languages.name2'
        db.alter_column('analysis_languages', 'name2', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

        # Changing field 'Languages.lmp_c1'
        db.alter_column('analysis_languages', 'lmp_c1', self.gf('django.db.models.fields.CharField')(max_length=32, null=True))

        # Changing field 'Languages.c1'
        db.alter_column('analysis_languages', 'c1', self.gf('django.db.models.fields.CharField')(max_length=33, null=True))


    def backwards(self, orm):
        
        # Changing field 'Languages.cnt'
        db.alter_column('analysis_languages', 'cnt', self.gf('django.db.models.fields.CharField')(max_length=8))

        # Changing field 'Languages.lmp_class'
        db.alter_column('analysis_languages', 'lmp_class', self.gf('django.db.models.fields.CharField')(max_length=5))

        # Changing field 'Languages.name2'
        db.alter_column('analysis_languages', 'name2', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Changing field 'Languages.lmp_c1'
        db.alter_column('analysis_languages', 'lmp_c1', self.gf('django.db.models.fields.CharField')(max_length=32))

        # Changing field 'Languages.c1'
        db.alter_column('analysis_languages', 'c1', self.gf('django.db.models.fields.CharField')(max_length=33))


    models = {
        'analysis.ecoregions': {
            'Meta': {'object_name': 'EcoRegions'},
            'area': ('django.db.models.fields.FloatField', [], {}),
            'area_km2': ('django.db.models.fields.IntegerField', [], {}),
            'eco_code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'eco_name': ('django.db.models.fields.CharField', [], {'max_length': '99'}),
            'geometry': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '54009', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perimeter': ('django.db.models.fields.FloatField', [], {}),
            'rangeland': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'realm': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        },
        'analysis.languages': {
            'Meta': {'object_name': 'Languages'},
            'c1': ('django.db.models.fields.CharField', [], {'max_length': '33', 'null': 'True', 'blank': 'True'}),
            'cnt': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'family': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'familyprop': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'g': ('django.db.models.fields.CharField', [], {'max_length': '225', 'null': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '54009', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lmp_c1': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'lmp_class': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'lmp_pop1': ('django.db.models.fields.FloatField', [], {}),
            'nam_ansi': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'nam_label': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name2': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'name_prop': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'pop': ('django.db.models.fields.CharField', [], {'max_length': '86', 'null': 'True', 'blank': 'True'})
        },
        'analysis.reportcache': {
            'Meta': {'object_name': 'ReportCache'},
            'context': ('picklefield.fields.PickledObjectField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'wkt_hash': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['analysis']
