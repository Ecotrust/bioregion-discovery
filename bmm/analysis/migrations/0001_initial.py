# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Languages'
        db.create_table('analysis_languages', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nam_label', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('name_prop', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('name2', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('nam_ansi', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('cnt', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('c1', self.gf('django.db.models.fields.CharField')(max_length=33)),
            ('pop', self.gf('django.db.models.fields.CharField')(max_length=86, null=True, blank=True)),
            ('lmp_pop1', self.gf('django.db.models.fields.FloatField')()),
            ('g', self.gf('django.db.models.fields.CharField')(max_length=225, null=True, blank=True)),
            ('lmp_class', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('familyprop', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('family', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('lmp_c1', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=54009, null=True, blank=True)),
        ))
        db.send_create_signal('analysis', ['Languages'])

        # Adding model 'EcoRegions'
        db.create_table('analysis_ecoregions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('area', self.gf('django.db.models.fields.FloatField')()),
            ('perimeter', self.gf('django.db.models.fields.FloatField')()),
            ('eco_name', self.gf('django.db.models.fields.CharField')(max_length=99)),
            ('realm', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('area_km2', self.gf('django.db.models.fields.IntegerField')()),
            ('eco_code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('rangeland', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=54009, null=True, blank=True)),
        ))
        db.send_create_signal('analysis', ['EcoRegions'])


    def backwards(self, orm):
        
        # Deleting model 'Languages'
        db.delete_table('analysis_languages')

        # Deleting model 'EcoRegions'
        db.delete_table('analysis_ecoregions')


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
            'c1': ('django.db.models.fields.CharField', [], {'max_length': '33'}),
            'cnt': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'family': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'familyprop': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'g': ('django.db.models.fields.CharField', [], {'max_length': '225', 'null': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '54009', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lmp_c1': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'lmp_class': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'lmp_pop1': ('django.db.models.fields.FloatField', [], {}),
            'nam_ansi': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'nam_label': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name2': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'name_prop': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'pop': ('django.db.models.fields.CharField', [], {'max_length': '86', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['analysis']
