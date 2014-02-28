# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Availability'
        db.create_table('timeslots_availability', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timeslots.Scale'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timeslots.Product'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('timeslots', ['Availability'])

        # Adding model 'SiloJob'
        db.create_table('timeslots_silojob', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timeslots.Scale'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timeslots.Product'])),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timeslots.UserProfile'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('timeslots', ['SiloJob'])

        # Adding model 'Product'
        db.create_table('timeslots_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('load_time', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('timeslots', ['Product'])

        # Adding model 'Scale'
        db.create_table('timeslots_scale', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timeslots.Station'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('start', self.gf('django.db.models.fields.TimeField')()),
            ('concurrent_products', self.gf('django.db.models.fields.IntegerField')()),
            ('slicecount', self.gf('django.db.models.fields.IntegerField')()),
            ('sliceduration', self.gf('django.db.models.fields.IntegerField')(default=30)),
        ))
        db.send_create_signal('timeslots', ['Scale'])


    def backwards(self, orm):
        # Deleting model 'Availability'
        db.delete_table('timeslots_availability')

        # Deleting model 'SiloJob'
        db.delete_table('timeslots_silojob')

        # Deleting model 'Product'
        db.delete_table('timeslots_product')

        # Deleting model 'Scale'
        db.delete_table('timeslots_scale')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'timeslots.availability': {
            'Meta': {'object_name': 'Availability'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Product']"}),
            'scale': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Scale']"})
        },
        'timeslots.block': {
            'Meta': {'object_name': 'Block'},
            'dock': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Dock']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linecount': ('django.db.models.fields.IntegerField', [], {}),
            'max_slots': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slotcount': ('django.db.models.fields.IntegerField', [], {}),
            'slotduration': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.TimeField', [], {})
        },
        'timeslots.dock': {
            'Meta': {'object_name': 'Dock'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Station']"})
        },
        'timeslots.job': {
            'Meta': {'object_name': 'Job'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'payload': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '25'}),
            'slot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Slot']"})
        },
        'timeslots.logging': {
            'Meta': {'object_name': 'Logging'},
            'host': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'timeslots.product': {
            'Meta': {'object_name': 'Product'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load_time': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'timeslots.scale': {
            'Meta': {'object_name': 'Scale'},
            'concurrent_products': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slicecount': ('django.db.models.fields.IntegerField', [], {}),
            'sliceduration': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'start': ('django.db.models.fields.TimeField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Station']"})
        },
        'timeslots.silojob': {
            'Meta': {'object_name': 'SiloJob'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.UserProfile']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Product']"}),
            'scale': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Scale']"})
        },
        'timeslots.slot': {
            'Meta': {'ordering': "['date', 'timeslot', 'line']", 'unique_together': "(('date', 'block', 'timeslot', 'line'),)", 'object_name': 'Slot'},
            'block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Block']"}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.UserProfile']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_klv': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'line': ('django.db.models.fields.IntegerField', [], {}),
            'progress': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'timeslot': ('django.db.models.fields.IntegerField', [], {})
        },
        'timeslots.station': {
            'Meta': {'object_name': 'Station'},
            'booking_deadline': ('django.db.models.fields.TimeField', [], {}),
            'has_klv': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'longdescription': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'multiple_charges': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'opened_on_weekend': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rnvp': ('django.db.models.fields.TimeField', [], {}),
            'shortdescription': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'timeslots.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'ZIP': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'de'", 'max_length': '2'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'stations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['timeslots.Station']", 'symmetrical': 'False'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['timeslots']