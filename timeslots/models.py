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

    def _get_start_times(self):
        start_times = []
        for i in range(self.slotcount):
            delta = i * self.slotduration
            starttime = datetime.combine(date.today(), self.start) + timedelta(minutes=delta)
            start_times.append(starttime.time())
        return start_times
    start_times = property(_get_start_times)

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
    block = models.ForeignKey(Block)
    company = models.ForeignKey(UserProfile)
    
    date = models.DateField()
    index = models.IntegerField()
    blocked = models.BooleanField()

class Job(models.Model):
    slot = models.ForeignKey(Slot)
    number = models.CharField(max_length=20, blank=True)
    description = models.CharField(max_length=200, blank=True)

class Logging(models.Model):
    user = models.ForeignKey(User)
    
    task = models.CharField(max_length=200)
    timestamp = models.TimeField()
