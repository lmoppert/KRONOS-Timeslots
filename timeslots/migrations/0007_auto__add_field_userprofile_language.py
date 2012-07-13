# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'UserProfile.language'
        db.add_column('timeslots_userprofile', 'language',
                      self.gf('django.db.models.fields.CharField')(default='DE', max_length=2),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'UserProfile.language'
        db.delete_column('timeslots_userprofile', 'language')


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
        'timeslots.block': {
            'Meta': {'object_name': 'Block'},
            'dock': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Dock']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linecount': ('django.db.models.fields.IntegerField', [], {}),
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
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'slot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Slot']"})
        },
        'timeslots.logging': {
            'Meta': {'object_name': 'Logging'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'timestamp': ('django.db.models.fields.TimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'timeslots.slot': {
            'Meta': {'ordering': "['date', 'timeslot', 'line']", 'object_name': 'Slot'},
            'block': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.Block']"}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['timeslots.UserProfile']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'line': ('django.db.models.fields.IntegerField', [], {}),
            'timeslot': ('django.db.models.fields.IntegerField', [], {})
        },
        'timeslots.station': {
            'Meta': {'object_name': 'Station'},
            'booking_deadline': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'longdescription': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
            'language': ('django.db.models.fields.CharField', [], {'default': "'DE'", 'max_length': '2'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'readonly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'stations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['timeslots.Station']", 'symmetrical': 'False'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['timeslots']