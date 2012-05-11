from django.db import models

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

class Slot(models.Model):
    line = models.ForeignKey(Line)
    company = models.ForeignKey(UserProfile)
    
    index = model.IntegerField()
    job_number = model.CharField(max_length=20, blank=True)
    blocked = model.BooleanField()

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    station = models.ManyToManyField(Station)
    
    company = model.CharField(max_length=200)
    street = model.CharField(max_length=200, blank=True)
    ZIP = model.CharField(max_length=20, blank=True)
    town = model.CharField(max_length=200, blank=True)
    country = model.CharField(max_length=200, blank=True)
    phone = model.CharField(max_length=200, blank=True)
    role = model.IntegerField()
    readonly = model.BooleanField()
    def __unicode__(self):
        return "%s" % (self.company)

class Logging(models.Model):
    user = models.ForeignKey(User)
    
    task = model.CharField(max_length=200)
    timestamp = models.TimeField()
