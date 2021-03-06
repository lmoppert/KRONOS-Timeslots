from datetime import timedelta, datetime, date, time

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop


class Station(models.Model):
    """
    The Station represents one address, where trucks can be loaded.

    Every station consist of one or several `timeslots.Dock`

    """
    name = models.CharField(max_length=200)
    shortdescription = models.CharField(max_length=200, blank=True)
    longdescription = models.TextField(blank=True)
    booking_deadline = models.TimeField(
        help_text=_(
            "Booking deadline = time on the day before from which on a slot "
            "can not be reserved any more. Set this to midnight to turn off "
            "this feature completely for this station"
        )
    )
    rnvp = models.TimeField(
        help_text=_(
            "RVNP = Rien ne vas plus -- time when a slot can not be edited "
            "any more, set to Midnight to have the deadline as RNVP"
        )
    )
    opened_on_weekend = models.BooleanField(
        default=False,
        help_text=_(
            "Choose this option if this station will be opened on weekends"
        )
    )
    multiple_charges = models.BooleanField(
        default=True,
        help_text=_(
            "If this option is marked, the reservation form offers the "
            "opportunity to add more than one job"
        )
    )
    has_status = models.BooleanField(
        default=False,
        help_text=_(
            "This option adds a Statusbar to the job view, which shows the "
            "current loading status"
        )
    )
    has_klv = models.BooleanField(
        default=False,
        help_text=_(
            "Choose this option if you want to be able to mark charges with "
            "an KLV/NV flag"
        )
    )
    has_product = models.BooleanField(
        default=False,
        help_text=_(
            "Choose this option if you want to be able to add information "
            "about available products to the docks of this station"
        )
    )

    def past_deadline(self, curr_date, curr_time):
        my_dl = self.booking_deadline
        if my_dl == time(0, 0):
            deadline = datetime.combine(curr_date + timedelta(days=1), my_dl)
        else:
            deadline = datetime.combine(curr_date - timedelta(days=1), my_dl)
        return curr_time > deadline

    @models.permalink
    def get_absolute_url(self):
        return ('timeslots_station_detail', (), {'station_id': self.id})

    def _get_longname(self):
        return self.name + " - " + self.shortdescription
    longname = property(_get_longname)

    def __unicode__(self):
        return "%s - %s" % (self.name, self.shortdescription)

    class Meta:
        verbose_name = _("Station")
        verbose_name_plural = _("Stations")


class Dock(models.Model):
    """
    The Dock belongs to one `timeslots.Station` and represents a dock, that is
    meant for a specific sort of loading like container or truck.

    Timeslots of a dock are organized through a `timeslots.Block`

    """
    station = models.ForeignKey(Station)

    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.station.name, self.name)

    class Meta:
        verbose_name = _("Dock")
        verbose_name_plural = _("Docks")


class Product(models.Model):
    """
    The Product contains infromation on products offered on a specific
    `timeslots.Dock` on a certain day.
    """
    dock = models.ForeignKey(Dock)
    date = models.DateField()
    details = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return "%s (%s): %s)" % (unicode(self.dock),
                                 unicode(self.date),
                                 self.details)

    def get_absolute_url(self):
        return reverse('timeslots_slot_view', kwargs={
            'station_id': self.dock.station.id,
            'date': self.date.strftime("%Y-%m-%d"),
        })

    class Meta:
        ordering = ['date']


class Block(models.Model):
    """
    The Block is a collection of timeslots that belongs to a specific
    `timeslots.Dock`.

    The number of Lines (possible patallel loadings) is also defined hereour
    """
    dock = models.ForeignKey(Dock)

    start = models.TimeField()
    linecount = models.IntegerField()
    slotcount = models.IntegerField()
    slotduration = models.IntegerField()
    max_slots = models.IntegerField(default=0, help_text=_("0 for unlimited"))

    def get_slots(self, date):
        return self.slot_set.filter(date=date).count()

    def _get_end(self):
        delta = self.slotcount * self.slotduration
        endtime = (datetime.combine(date.today(), self.start) +
                   timedelta(minutes=delta))
        return endtime.time()
    end = property(_get_end)

    def _get_start_times(self):
        start_times = []
        for i in range(self.slotcount):
            delta = i * self.slotduration
            starttime = datetime.combine(
                date.today(), self.start) + timedelta(minutes=delta)
            start_times.append(starttime.time())
        return start_times
    start_times = property(_get_start_times)

    def __unicode__(self):
        return "%s (%s - %s)" % (unicode(self.dock),
                                 self.start.strftime("%H:%M"),
                                 self.end.strftime("%H:%M"))

    class Meta:
        verbose_name = _("Block")
        verbose_name_plural = _("Blocks")


class UserProfile(models.Model):
    """
    This model adds additional fields to the buil in `auth.User` model.

    The most important additions are the language (prefered user-interface
    language) and the company field.
    """
    GROUPS = (_("administrator"), _("loadmaster"), _("charger"), _("user"),
              _("viewer"))
    LANGUAGES = ((u'de', u'Deutsch'), (u'en', u'English'))
    user = models.OneToOneField(User)
    stations = models.ManyToManyField(Station)

    language = models.CharField(
        max_length=2,
        choices=LANGUAGES,
        default='de',
        verbose_name=_("Language")
    )
    street = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Street")
    )
    country = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Country")
    )
    phone = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Phone")
    )
    company = models.CharField(max_length=200, verbose_name=_("Company"))
    ZIP = models.CharField(max_length=20, blank=True, verbose_name=_("ZIP"))
    town = models.CharField(max_length=200, blank=True, verbose_name=_("Town"))

    def _get_is_master(self):
        if (self.user.groups.filter(name='administrator').count() == 0 and
                self.user.groups.filter(name='loadmaster').count() == 0 and
                self.user.groups.filter(name='charger').count() == 0):
            return False
        else:
            return True
    is_master = property(_get_is_master)

    def _get_is_viewer(self):
        return not self.user.groups.filter(name='viewer').count() == 0
    is_viewer = property(_get_is_viewer)

    def _get_is_readonly(self):
        return not (self.user.groups.filter(name='charger').count() == 0 and
                    self.user.groups.filter(name='viewer').count() == 0)
    is_readonly = property(_get_is_readonly)

    @models.permalink
    def get_absolute_url(self):
        return ('timeslots_userprofile_detail', (), {})

    def __unicode__(self):
        return "%s %s (%s)" % (self.user.first_name, self.user.last_name,
                               self.company)


@receiver(user_logged_in)
def setlang(sender, **kwargs):
    lang = kwargs['user'].userprofile.language
    kwargs['request'].session['django_language'] = lang


class Slot(models.Model):
    """
    This is the representation of a dedicated reservation. The Slot is part of
    a block and identified by the timeslot number and the line number, which
    results in a triple as the index (block_id, timeslot, line)
    """
    block = models.ForeignKey(Block)
    company = models.ForeignKey(UserProfile)

    date = models.DateField()
    timeslot = models.IntegerField()
    line = models.IntegerField()
    progress = models.PositiveIntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    is_klv = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def _get_times(self):
        slotnumber = int(self.timeslot)
        start = self.block.start_times[slotnumber - 1].strftime("%H:%M")
        try:
            end = self.block.start_times[slotnumber]
        except IndexError:
            end = self.block.end
        return "%s - %s" % (start, end.strftime("%H:%M"))
    times = property(_get_times)

    def _get_times_flagged(self):
        if self.is_klv:
            return "%s (KLV/NV)" % (self.times)
        else:
            return self.times
    times_flagged = property(_get_times_flagged)

    def _get_date_string(self):
        return self.date.strftime("%Y-%m-%d")
    date_string = property(_get_date_string)

    def status(self, user):
        if self.is_blocked:
            return ugettext_noop("blocked")
        else:
            if (user.userprofile.is_master or user.userprofile.is_viewer or
                    self.company.id == user.userprofile.id):
                try:
                    first_job = self.job_set.all()[0].number
                except IndexError:
                    first_job = "..."
                if self.is_klv:
                    return "%s - %s (KLV/NV)" % (
                        self.company.company, first_job)
                else:
                    return "%s - %s" % (self.company.company, first_job)
            else:
                return ugettext_noop("reserved")

    def past_rnvp(self, curr_time):
        start = datetime.combine(
            self.date,
            self.block.start_times[int(self.timeslot) - 1]
        )
        delta = timedelta(
            hours=self.block.dock.station.rnvp.hour,
            minutes=self.block.dock.station.rnvp.minute
        )
        if delta < timedelta(minutes=1):
            return self.block.dock.station.past_deadline(self.date, curr_time)
        else:
            return start - curr_time < delta

    @models.permalink
    def get_absolute_url(self):
        return ('timeslots_slot_detail', (), {
                'block_id': self.block.id,
                'timeslot': str(self.timeslot),
                'line': str(self.line),
                'date': self.date.strftime("%Y-%m-%d")
                })

    def __unicode__(self):
        return "%(date)s [%(time)s] %(station)s - %(dock)s" % {
            'date': unicode(self.date),
            'dock': self.block.dock.name,
            'station': self.block.dock.station.name,
            'time': self.times
        }

    class Meta:
        unique_together = ('date', 'block', 'timeslot', 'line',)
        ordering = ['date', 'timeslot', 'line']
        verbose_name = _("Slot")
        verbose_name_plural = _("Slots")


class Job(models.Model):
    """
    A job contains informations about a charge that will be loaden within a
    slot. There can be several jobs per slot but every slot muste contain
    at least one valid job.
    """
    FTL = 40
    Payload_Choices = [(x + 1, "%s t" % (x + 1)) for x in range(FTL)]
    slot = models.ForeignKey(Slot)

    number = models.CharField(max_length=20)
    payload = models.PositiveSmallIntegerField(
        default=25,
        choices=Payload_Choices
    )
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")


class Logging(models.Model):
    user = models.ForeignKey(User)

    time = models.DateTimeField(editable=False)
    host = models.CharField(max_length=40, blank=True)
    task = models.CharField(max_length=500)

    def save(self, *args, **kwargs):
        self.time = datetime.today()
        super(Logging, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Logging")
        verbose_name_plural = _("Loggings")
