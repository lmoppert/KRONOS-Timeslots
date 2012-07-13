from datetime import timedelta, datetime, date
from django.db import models
from django.contrib.auth.models import User

class Station(models.Model):
    """
      The Station represents one address, where trucks can be loaded. 

      **Related Objects**
      
      ``dock``
      Every station consist of one or several :model:`timeslots.Dock`.
    """
    name = models.CharField(max_length=200)
    shortdescription = models.CharField(max_length=200, blank=True)
    longdescription = models.TextField(blank=True)
    booking_deadline = models.TimeField()
    rnvp = models.TimeField(help_text="RVNP = Rien ne vas plus -- time when a slot can not be edited any more")
    opened_on_weekend = models.BooleanField()

    def _get_longname(self):
        return self.name + " - " + self.shortdescription
    longname = property(_get_longname)
    
    def __unicode__(self):
        return self.name

class Dock(models.Model):
    """
      The Dock belongs to one :model:`timeslots.Station` and represents a dock, that is
      meant for a specific sort of loading like container or truck.

      **Related Objects**

      ``block``
      Timeslots of a dock are organized through a :model:`timeslots.Block`
    """
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

    def _get_can_see_all(self):
        if self.user.groups.filter(name='Administrator').count() == 0 and self.user.groups.filter(name='Lademeister').count() == 0:
            return False
        else:
            return True
    can_see_all = property(_get_can_see_all)

    def __unicode__(self):
        return "%s" % (self.company)

class Slot(models.Model):
    block = models.ForeignKey(Block)
    company = models.ForeignKey(UserProfile)
    
    date = models.DateField()
    timeslot = models.IntegerField()
    line = models.IntegerField()
    is_blocked = models.BooleanField(default=False)

    def _get_times(self):
        start = self.block.start_times[int(self.timeslot)-1].strftime("%H:%M")
        try:
            end = self.block.start_times[int(self.timeslot)]
        except IndexError:
            end = self.block.end
        return  "%s - %s" % (start, end.strftime("%H:%M"))
    times = property(_get_times)

    def status(self, user):
        if user.userprofile.can_see_all or self.company.id == user.id:
            return self.company.company
        else:
            if self.is_blocked:
                return "blocked"
            else:
                return "reserved"

    def past_deadline(self, curr_date, curr_time):
        deadline = datetime.combine(curr_date - timedelta(days=1), self.block.dock.station.booking_deadline)
        return curr_time > deadline

    def past_rnvp(self, curr_time):
        start = datetime.combine(self.date, self.block.start_times[int(self.timeslot)-1])
        delta = timedelta(hours=self.block.dock.station.rnvp.hour, minutes=self.block.dock.station.rnvp.minute)
        return start - curr_time < delta

    def __unicode__(self):
        return "%s - %s|%s|%s" % (unicode(self.date), self.block.id, self.timeslot, self.line)

    class Meta:
        ordering = ['date', 'timeslot', 'line']


class Job(models.Model):
    slot = models.ForeignKey(Slot)
    number = models.CharField(max_length=20, blank=True)
    description = models.CharField(max_length=200, blank=True)

class Logging(models.Model):
    user = models.ForeignKey(User)
    
    task = models.CharField(max_length=200)
    timestamp = models.TimeField()
