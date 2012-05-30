from datetime import timedelta, datetime, date
from django.db import models
from django.contrib.auth.models import User

class Station(models.Model):
    name = models.CharField(max_length=200)
    shortdescription = models.CharField(max_length=200, blank=True)
    longdescription = models.TextField(blank=True)
    booking_deadline = models.TimeField()
    rnvp = models.TimeField()

    def _get_longname(self):
        return self.name + " - " + self.shortdescription
    longname = property(_get_longname)
    
    def __unicode__(self):
        return self.name

class Dock(models.Model):
    station = models.ForeignKey(Station)
    
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return  '%s - %s' % (self.station.name, self.name)

class Block(models.Model):
    dock = models.ForeignKey(Dock)
    
    start = models.TimeField()
    linecount = models.IntegerField()
    slotcount = models.IntegerField()
    slotduration = models.IntegerField()
    
    def _get_end(self):
        delta = self.slotcount * self.slotduration
        endtime = datetime.combine(date.today(), self.start) + timedelta(minutes=delta)
        return endtime.time()
    end = property(_get_end)

    def __unicode__(self):
        return "%s (%s - %s)" % (unicode(self.dock), self.start.strftime("%H:%M"), self.end.strftime("%H:%M"))

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    stations = models.ManyToManyField(Station)
    
    company = models.CharField(max_length=200)
    street = models.CharField(max_length=200, blank=True)
    ZIP = models.CharField(max_length=20, blank=True)
    town = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=200, blank=True)
    readonly = models.BooleanField()

    def __unicode__(self):
        return "%s" % (self.user.username)

class Slot(models.Model):
    line = models.ForeignKey(Line)
    company = models.ForeignKey(UserProfile)
    
    date = models.DateField()
    index = models.IntegerField()
    job_number = models.CharField(max_length=20, blank=True)
    blocked = models.BooleanField()

class Logging(models.Model):
    user = models.ForeignKey(User)
    
    task = models.CharField(max_length=200)
    timestamp = models.TimeField()
