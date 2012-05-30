# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Station'
        db.create_table('timeslots_station', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('shortdescription', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('longdescription', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('booking_deadline', self.gf('django.db.models.fields.TimeField')()),
            ('rnvp', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal('timeslots', ['Station'])

        # Adding model 'Dock'
        db.create_table('timeslots_dock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timeslots.Station'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('linecount', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('timeslots', ['Dock'])

        # Adding model 'Line'
        db.create_table('timeslots_line', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dock', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timeslots.Dock'])),
            ('start', self.gf('django.db.models.fields.TimeField')()),
            ('slotcount', self.gf('django.db.models.fields.IntegerField')()),
            ('slotduration', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('timeslots', ['Line'])

        # Adding model 'UserProfile'
        db.create_table('timeslots_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('ZIP', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('town', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('readonly', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('timeslots', ['UserProfile'])

        # Adding M2M table for field stations on 'UserProfile'
        db.create_table('timeslots_userprofile_stations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['timeslots.userprofile'], null=False)),
            ('station', models.ForeignKey(orm['timeslots.station'], null=False))
        ))
        db.create_unique('timeslots_userprofile_stations', ['userprofile_id', 'station_id'])

        # Adding model 'Slot'
        db.create_table('timeslots_slot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('line', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timeslots.Line'])),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['timeslots.UserProfile'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            ('job_number', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('blocked', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('timeslots', ['Slot'])

        # Adding model 'Logging'
        db.create_table('timeslots_logging', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('task', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('timestamp', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal('timeslots', ['Logging'])


    def backwards(self, orm):
        # Deleting model 'Station'
        db.delete_table('timeslots_station')

        # Deleting model 'Dock'
        db.delete_table('timeslots_dock')

        # Deleting model 'Line'
        db.delete_table('timeslots_line')

        # Deleting model 'UserProfile'
        db.delete_table('timeslots_userprofile')

        # Removing M2M table for field stations on 'UserProfile'
        db.delete_table('timeslots_userprofile_stations')

        # Deleting model 'Slot'
        db.delete_table('timeslots_slot')

        # Deleting model 'Logging'
        db.delete_table('timeslots_logging')


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
        'timeslots.dock': {
            'Meta': {'object_name': 'Dock'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linecount': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Station']"})
        },
        'timeslots.line': {
            'Meta': {'object_name': 'Line'},
            'dock': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Dock']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slotcount': ('django.db.models.fields.IntegerField', [], {}),
            'slotduration': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.TimeField', [], {})
        },
        'timeslots.logging': {
            'Meta': {'object_name': 'Logging'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'timestamp': ('django.db.models.fields.TimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'timeslots.slot': {
            'Meta': {'object_name': 'Slot'},
            'blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.UserProfile']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'job_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Line']"})
        },
        'timeslots.station': {
            'Meta': {'object_name': 'Station'},
            'booking_deadline': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'longdescription': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'rnvp': ('django.db.models.fields.TimeField', [], {}),
            'shortdescription': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'timeslots.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'ZIP': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'readonly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'stations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['timeslots.Station']", 'symmetrical': 'False'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['timeslots']