from django.db import models
from django.contrib.auth.models import User

class Station(models.Model):
    name = models.CharField(max_length=200)
    shortdescription = models.CharField(max_length=200, blank=True)
    longdescription = models.TextField(blank=True)
    booking_deadline = models.TimeField()
    rnvp = models.TimeField()
    def __unicode__(self):
        return self.name

class Dock(models.Model):
    station = models.ForeignKey(Station)
    
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)
    linecount = models.IntegerField()
    def __unicode__(self):
        return self.name

class Line(models.Model):
    dock = models.ForeignKey(Dock)
    
    start = models.TimeField()
    end = models.TimeField()
    duration = models.IntegerField()
    def __unicode__(self):
        return "%s" % (self.dock)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    station = models.ManyToManyField(Station)
    
    company = models.CharField(max_length=200)
    street = models.CharField(max_length=200, blank=True)
    ZIP = models.CharField(max_length=20, blank=True)
    town = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=200, blank=True)
    role = models.IntegerField()
    readonly = models.BooleanField()
    def __unicode__(self):
        return "%s" % (self.company)

class Slot(models.Model):
    line = models.ForeignKey(Line)
    company = models.ForeignKey(UserProfile)
    
    index = models.IntegerField()
    job_number = models.CharField(max_length=20, blank=True)
    blocked = models.BooleanField()

class Logging(models.Model):
    user = models.ForeignKey(User)
    
    task = models.CharField(max_length=200)
    timestamp = models.TimeField()
