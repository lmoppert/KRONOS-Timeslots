"""Module with class based views and view functions for the Timeslots app."""

from django.db.models import F
from django.shortcuts import (
    get_object_or_404, get_list_or_404, render, redirect)
from django.http import HttpResponse

from django.views.generic import UpdateView, DetailView
from django.views.generic.dates import DayArchiveView, MonthArchiveView

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_noop

from django_tables2 import RequestConfig
from datetime import datetime, timedelta

from timeslots.models import Block, Logging, Slot, Station
from timeslots.forms import (UserProfileForm, BlockSlotForm, JobForm,
                             SingleJobForm)
from timeslots.tables import StationJobTable, UserJobTable, UserTable
from timeslots.utils import (daterange, delete_slot_garbage, log_msg,
                             cbv_decorator)
import csv


# Class-Based-Views
@cbv_decorator(login_required)
class UserProfile(UpdateView):

    """Class based view for the user profile."""

    form_class = UserProfileForm

    def get_object(self, queryset=None):
        """Return the user profile."""
        return self.request.user.userprofile

    def form_valid(self, form):
        """Return, whether the submited form is valid."""
        self.request.session['django_language'] = form.instance.language
        return super(UserProfile, self).form_valid(form)


class LoggingArchive():

    """Class based view for the log entries."""

    model = Logging
    month_format = "%m"
    date_field = 'time'
    allow_empty = True
    template_name = 'timeslots/logging.html'


@cbv_decorator(user_passes_test(lambda u: u.userprofile.is_master))
class DayLoggingArchive(LoggingArchive, DayArchiveView):

    """Class based view for the log entries for one day."""

    pass


@cbv_decorator(user_passes_test(lambda u: u.userprofile.is_master))
class MonthLoggingArchive(LoggingArchive, MonthArchiveView):

    """Class based view for the log entries for one month."""

    pass


@cbv_decorator(login_required)
class StationView(DetailView):
    """Base Class for all station related Views."""

    model = Station
    date = datetime.now().strftime('%Y-%m-%d')
    target = 'slots'
    docks = []  # List of tuples: (dock_name, dock_id)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'selectedDocks' in request.POST:
            docks = request.POST.getlist('selectedDocks')
            request.session['selectedDocks'] = docks
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.handle_session_data(request)
        url = self.handle_conditions(request, self.date)
        if url:
            return redirect(url)
        else:
            delete_slot_garbage(request)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_job_data(self, request):
        slotlist = {}
        for dock_name, dock_id in self.docks:
            slotlist[dock_name] = []
        profile = request.user.userprofile
        if profile.is_master or profile.is_viewer:
            slots = list(Slot.objects.filter(date=self.date))
        else:
            slots = list(Slot.objects.filter(date=self.date).filter(
                company=request.user.userprofile.id))
        return (slotlist, slots)

    def get_context_data(self, **kwargs):
        context = super(StationView, self).get_context_data(**kwargs)
        if 'date' in self.kwargs:
            self.date = self.kwargs['date']
        context['date'] = self.date
        context['target'] = self.target
        return context

    def handle_session_data(self, request):
        self.docks = []
        if 'selectedDocks' in request.session:
            for dock_id in request.session['selectedDocks']:
                try:
                    dock = self.object.dock_set.get(pk=dock_id)
                except:
                    continue
                self.docks.append((dock.name, dock.id))
        else:
            for dock in self.object.dock_set.all():
                self.docks.append((dock.name, dock.id))

    def handle_conditions(self, request, date):
        station = self.object
        user = request.user
        date = datetime.strptime(date, "%Y-%m-%d").date()
        if (not station.opened_on_weekend and not user.userprofile.is_master
                and date.weekday() > 4):
            msg = "User {user} tried to access the weekend view of station" \
                  "{object}, which is not opened on weekends."
            log_msg(request, msg, station)
            messages.error(request, _('This station is closed on weekends!'))
            monday = (date + timedelta(days=7 - date.weekday()))
            return '/timeslots/station/{station}/date/{date}/slots/'.format(
                station=station.id, date=monday.strftime("%Y-%m-%d"))
        if user.userprofile.stations.filter(id=station.id).count() == 0:
            msg = "User {user} tried to access station {station} without" \
                "authorization"
            log_msg(request, msg, station)
            msg = _("You are not authorized to access this station!")
            messages.error(request, msg)
            return '/timeslots/profile/'
        if self.object.dock_set.count() == 0:
            if self.object.scale_set.count() == 0:
                msg = "Station {station} has no docks or scales assigned to it"
                messages.error(request, msg % station.name)
                return 'timeslots_home'
            return '/station/{station}/scales/'.format(station=self.object.id)


class SlotView(StationView):
    """
    Displays the blocks ( see :model:`timeslots.Block`) of a
    :model:`timeslots.Station` for a specific date.
    """

    template_name = 'timeslots/station_detail.html'

    def handle_conditions(self, request, date):
        station = self.object
        user = request.user
        if (not user.userprofile.is_master and station.past_deadline(
                datetime.strptime(date, "%Y-%m-%d").date(), datetime.now())):
            msg = _("The reservation deadline has been reached, no more"
                    "reservations will be accepted!")
            messages.warning(request, msg)
        return super(SlotView, self).handle_conditions(request, date)

    def get_timeslots(self, block):
        timeslots = []
        for timeslot in range(block.slotcount):
            lines = []
            for line in range(block.linecount):
                try:
                    curr_slot = block.slot_set.filter(
                        date=self.date).get(
                        date=self.date,
                        timeslot=timeslot + 1,
                        line=line + 1,
                        block=block.id
                    )
                    company = curr_slot.status(self.request.user)
                except ObjectDoesNotExist:
                    company = ugettext_noop("free")
                if company in ("free", "blocked"):
                    lines.append((company, None))
                else:
                    lines.append((company, curr_slot))
            time = block.start_times[int(timeslot)].strftime("%H:%M")
            timeslots.append((time, lines))
        return timeslots

    def get_context_data(self, **kwargs):
        context = super(SlotView, self).get_context_data(**kwargs)
        docks = []
        for dock_name, dock_id in self.docks:
            blocks = []
            dock = self.object.dock_set.get(pk=dock_id)
            for block in dock.block_set.all():
                if (block.max_slots > 0 and
                        block.get_slots(self.date) >= block.max_slots):
                    msg = _('The maximal number of Slots have been reserved, '
                            'no more reservations will be accepted!')
                    messages.warning(self.request, msg)
                timeslots = self.get_timeslots(block)
                blocks.append((str(block.id), timeslots))
            docks.append((dock_name, blocks))
        spans = ["span12", "span12", "span6", "span4"]
        if len(self.docks) < 4:
            span = spans[len(docks)]
        else:
            span = "span3"
        if self.request.user.userprofile.is_master:
            hidden = ()
        else:
            hidden = ("blocked", "reserved")
        context['span'] = span
        context['hidden'] = hidden
        context['docks'] = docks
        return context


class JobListView(StationView):
    """
    Displays the jobs of a :model:`timeslots.Station` for a specific date as a
    List, grouped by dock.
    """

    template_name = 'timeslots/job_list.html'
    target = 'joblist'

    def get_context_data(self, **kwargs):
        context = super(JobListView, self).get_context_data(**kwargs)
        slotlist, slots = self.get_job_data(self.request)
        for slot in slots:
            if (slot.block.dock.name in slotlist and
                    slot.block.dock.station.id == self.object.id
                    and (not slot.is_blocked or slot.job_set.count() > 0)):
                slotlist[slot.block.dock.name].append(slot)
        context['slotlist'] = slotlist
        context['docks'] = self.docks
        return context


class JobTableView(StationView):
    """
    Displays the jobs of a :model:`timeslots.Station` for a specific date as a
    Table.
    """

    template_name = 'timeslots/job_table.html'
    target = 'jobtable'

    def get_context_data(self, **kwargs):
        context = super(JobTableView, self).get_context_data(**kwargs)
        jobs = []
        slotlist, slots = self.get_job_data(self.request)
        for slot in slots:
            if ((slot.block.dock.name in slotlist and
                    slot.block.dock.station.id == self.object.id
                    and not slot.is_blocked)):
                for job in slot.job_set.all():
                    jobs.append(job)
        table = StationJobTable(jobs)
        RequestConfig(self.request, paginate=False).configure(table)
        context['table'] = table
        context['docks'] = self.docks
        return context


# View functions
@login_required
def logging_redirect(request):
    """Return a redirect to the one day log view."""
    t = datetime.now()
    return redirect('timeslots_logging_day', year=t.strftime("%Y"),
                    month=t.strftime("%m"), day=t.strftime("%d"))


@login_required
def logging_export(request, year, month):
    """Return a response for the logfile export."""
    if not request.user.userprofile.is_master:
        msg = "User {user} tried to export logfiles"
        msg += "but is not a member of a master group"
        log_msg(request, msg)
        msg = _("You are not authorized to access this page!")
        messages.error(request, msg)
        return redirect('/timeslots/profile/')
    filename = 'timeslots-user-list.csv'
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    writer = csv.writer(response)
    writer.writerow(['User', 'Time', 'Host', 'Task'])
    data = Logging.objects.filter(time__year=year).filter(time__month=month)
    for d in data:
        row = []
        row.append(d.user.username.encode('utf-8'))
        row.append(d.time)
        row.append(d.host.encode('utf-8'))
        row.append(d.task.encode('utf-8'))
        writer.writerow(row)
    return response


def logout_page(request):
    """Log out function."""
    logout_then_login(request)


@login_required
def password_change_done(request):
    """Return the redirect after a password has been changed."""
    messages.success(request, _('Your password has been changed!'))
    return redirect('timeslots_userprofile_detail')


@login_required
def profile(request):
    """Return the user profile view."""
    return render(request, 'timeslots/userprofile_detail.html')


@login_required
def users(request):
    """Return the user list view."""
    if not request.user.userprofile.is_master:
        msg = "User {user} tried to access the user list "
        msg += "but is not member of a master group"
        log_msg(request, msg)
        msg = _("You are not authorized to access this page!")
        messages.error(request, msg)
        return redirect('/timeslots/profile/')
    userlist = get_list_or_404(User, is_active=True)
    table = UserTable(userlist)
    RequestConfig(request, paginate={"per_page": 10}).configure(table)
    return render(request, 'timeslots/user_list.html', {'table': table})


@login_required
def slotstatus(request, slot_id, station_id, date):
    """Return a status indicator (progress bar) for a slot."""
    curr_slot = get_object_or_404(Slot, pk=slot_id)
    if request.user.userprofile.is_master:
        if curr_slot.progress < 3:
            curr_slot.progress = F('progress') + 1
            curr_slot.save()
        else:
            curr_slot.progress = 0
            curr_slot.save()
        return redirect('/timeslots/station/%s/date/%s/slots/' % (
            station_id, date))
    else:
        msg = "User {user} tried to change the status of slot {object} but is"
        msg += " not allowed to."
        log_msg(request, msg, curr_slot)
        msg = _('You are not allowed to change the status of a slot!')
        messages.error(request, msg)
        return redirect('/timeslots/station/%s/date/%s/slots/' % (
            station_id, date))


@login_required
def index(request):
    """Return the landing page."""
    jobs = []
    delete_slot_garbage(request)
    slots = request.user.userprofile.slot_set.filter(date__gt=datetime.now())
    for curr_slot in slots:
        for job in curr_slot.job_set.all():
            jobs.append(job)
    table = UserJobTable(jobs)
    RequestConfig(request, paginate={"per_page": 5}).configure(table)
    return render(request, 'index.html', {'table': table})


@login_required
def station_redirect(request):
    """Return a redirect for the station selector in the top bar."""
    if request.method == 'POST':
        curr_station = request.POST['selectedStation']
        date = request.POST['currentDate']
        try:
            del request.session['selectedDocks']
        except KeyError:
            pass
        return redirect('/timeslots/station/%s/date/%s/slots/' % (
            curr_station, date))


@login_required
def blocking(request):
    """Return the slot blocking form."""
    if not request.user.userprofile.is_master:
        msg = "User {user} tried to access the blocking view but is not "
        msg += "member of a master group"
        log_msg(request, msg)
        msg = _("You are not authorized to access this page!")
        messages.error(request, msg)
        return redirect('/timeslots/profile/')
    if (request.method == 'POST' and 'block' in request.POST and
            request.POST.get('block') != ""):
        block = get_object_or_404(Block, pk=request.POST.get('block'))
        timeslots = []
        for t in block.start_times:
            timeslots.append(t.strftime("%H:%M"))
        form = BlockSlotForm(
            request.POST,
            stations=request.user.userprofile.stations.values('id'),
            timeslots=list(enumerate(timeslots, start=1))
        )
        if form.is_valid():
            reserved_slots = []
            for day in daterange(form['start'].value(), form['end'].value()):
                for timeslot in form['slots'].value():
                    for line in range(block.linecount):
                        curr_slot, created = Slot.objects.get_or_create(
                            block=block,
                            date=day.strftime("%Y-%m-%d"),
                            timeslot=str(int(timeslot)),
                            line=str(line + 1),
                            defaults={'company': request.user.userprofile}
                        )
                        if not created and not curr_slot.is_blocked:
                            reserved_slots.append(curr_slot)
                        curr_slot.is_blocked = 'blockSlots' in request.POST
                        curr_slot.save()
            if 'blockSlots' in request.POST:
                log = "User {user} blocked slots %s from %s to %s for block %s"
                msg = _("successfully blocked the selected slots!")
                if len(reserved_slots) > 0:
                    msg = _("The slots listed below had already been "
                            "reserved before you blocked them. You can "
                            "click on the link if you want to relase a "
                            "slot. use <CTRL><click> to open the slot-form "
                            "(in a new window or tab)")
                    messages.warning(request, msg)
                    return render(request, 'timeslots/blocked.html', {
                        'slots': reserved_slots})
            else:
                log = "User {user} released slots %s from %s to %s for block "
                log += "{object}"
                msg = _("successfully released the selected slots!")
            log_msg(request, log % (form['slots'].value(),
                                    form['start'].value(),
                                    form['end'].value()), block)
            messages.success(request, msg)
            return redirect(reverse('timeslots_blocking'))
        else:
            form.helper.form_show_errors = False
    else:
        form = BlockSlotForm(
            stations=request.user.userprofile.stations.values('id'))
    return render(request, 'timeslots/blocking.html', {'form': form})


@login_required
def slot(request, date, block_id, timeslot, line):
    """ Return details for a :model:`timeslots.Slot`.

    **Context**

    ``RequestContext``

    ``block``
    An instance of :model:`timeslots.Block`

    """

    # prepare context items
    block = get_object_or_404(Block, pk=block_id)
    try:
        end = block.start_times[int(timeslot)]
    except IndexError:
        end = block.end
    times = block.start_times[int(timeslot) - 1].strftime("%H:%M")
    times += " - " + end.strftime("%H:%M")
    delete_slot_garbage(request)
    curr_slot, created = Slot.objects.get_or_create(
        date=date, timeslot=timeslot, line=line, block=block,
        defaults={'company': request.user.userprofile}
    )

    # check conditions
    if request.user.userprofile.is_readonly:
        msg = "Readonly user {user} tried to access slot {object}."
        log_msg(request, msg, curr_slot)
        messages.error(request, _('You are not allowed to change this slot!'))
        return redirect('/timeslots/station/%s/date/%s/jobtable/' % (
            block.dock.station.id, date))
    if ((not curr_slot.block.dock.station.opened_on_weekend
         and not request.user.userprofile.is_master
         and datetime.strptime(date, "%Y-%m-%d").date().weekday() > 4)):
        if created:
            curr_slot.delete()
        msg = "User {user} tried to access slot {object}, which is not opened "
        msg += "on weekends."
        log_msg(request, msg, curr_slot)
        messages.error(request, _('This station is closed on weekends!'))
        return redirect('/timeslots/profile/')
    if not request.user.userprofile.is_master and curr_slot.is_blocked:
        msg = "User {user} tried to access slot {object} which is blocked."
        log_msg(request, msg, curr_slot)
        messages.error(request, _('This slot has been blocked!'))
        return redirect('/timeslots/station/%s/date/%s/slots/' % (
            block.dock.station.id, date))
    if (created and not request.user.userprofile.is_master and
        curr_slot.block.dock.station.past_deadline(
            datetime.strptime(date, "%Y-%m-%d"), datetime.now())):
        curr_slot.delete()
        msg = "User {user} tried to reserve slot {object} after the "
        msg += "booking deadline has been reached."
        log_msg(request, msg, curr_slot)
        msg = _("The deadline for booking this slot has ended!")
        messages.error(request, msg)
        return redirect('/timeslots/station/%s/date/%s/slots/' % (
            block.dock.station.id, date))
    if ((created and block.max_slots > 0
         and block.get_slots(date) > block.max_slots)):
        curr_slot.delete()
        msg = "User {user} tried to reserve slot {object} after the "
        msg += "maximum number of blocks per day has been reached."
        log_msg(request, msg, curr_slot)
        msg = _("The maximal number of Slots have been reserved, no more "
                "reservations will be accepted!")
        messages.error(request, msg)
        return redirect('/timeslots/station/%s/date/%s/slots/' % (
            block.dock.station.id, date))
    if ((not created and not request.user.userprofile.is_master
         and curr_slot.past_rnvp(datetime.now()))):
        msg = "User {user} tried to change slot {object} after the rnvp "
        msg += "deadline has been reached."
        log_msg(request, msg, curr_slot)
        msg = _("This slot can not be changed any more!")
        messages.error(request, msg)
        return redirect('/timeslots/station/%s/date/%s/slots/' % (
            block.dock.station.id, date))
    if ((not request.user.userprofile.is_master
         and curr_slot.company.user.id != request.user.id)):
        if created:
            curr_slot.delete()
        msg = "User {user} tried to access slot {object} which is "
        msg += "reserved for a different user."
        log_msg(request, msg, curr_slot)
        msg = _("This slot was already booked by a different person!")
        messages.error(request, msg)
        return redirect('/timeslots/station/%s/date/%s/slots/' % (
            block.dock.station.id, date))

    # process request
    if request.method == 'POST':
        if 'makeReservation' in request.POST:
            if block.dock.station.multiple_charges:
                formset = JobForm(request.POST, instance=curr_slot)
            else:
                formset = SingleJobForm(request.POST, instance=curr_slot)
            if formset.is_valid():
                if 'is_klv' in request.POST:
                    curr_slot.is_klv = True
                curr_slot.save()
                formset.save()
                msg = "User {user} has successfully reserved slot {object}."
                log_msg(request, msg, curr_slot)
                msg = _("The reservation has been saved successfully!")
                messages.success(request, msg)
                return redirect('/timeslots/station/%s/date/%s/slots/' % (
                    block.dock.station.id, date))
            else:
                msg = "User {user} has submitted a reservation form for slot "
                msg += "{object} which contained errors."
                log_msg(request, msg, curr_slot)
        elif ('cancelReservation' in request.POST or
                'deleteSlot' in request.POST):
            curr_slot.delete()
            for job in curr_slot.job_set.all():
                job.delete()
            msg = "User {user} has successfully deleted the reservation for "
            msg += "slot {object}."
            log_msg(request, msg, curr_slot)
            msg = _("The reservation has been deleted successfully!")
            messages.success(request, msg)
            return redirect('/timeslots/station/%s/date/%s/slots/' % (
                block.dock.station.id, date))
        elif 'cancelEditing' in request.POST:
            return redirect('/timeslots/station/%s/date/%s/slots/' % (
                block.dock.station.id, date))
        elif 'releaseSlot' in request.POST:
            curr_slot.is_blocked = False
            curr_slot.save()
            msg = "User {user} has successfully released the blocking of "
            msg += "slot {object}."
            log_msg(request, msg, curr_slot)
            messages.success(request, _('This slot is no longer blocked!'))
            return redirect('/timeslots/station/%s/date/%s/slots/' % (
                block.dock.station.id, date))
        elif 'keepSlotBlocked' in request.POST:
            return redirect('/timeslots/station/%s/date/%s/slots/' % (
                block.dock.station.id, date))
    else:
        # This one has to go into the else path, otherwise errors
        # formset.non_form_errors are overwritten
        msg = "User {user} has opened the reservation form for slot {object}."
        log_msg(request, msg, curr_slot)
        if block.dock.station.multiple_charges:
            formset = JobForm(instance=curr_slot)
        else:
            formset = SingleJobForm(instance=curr_slot)

    return render(request, 'timeslots/slot_detail.html', {
        'date': date, 'curr_block': block, 'times': times,
        'station': block.dock.station, 'slot': curr_slot, 'form': formset,
        'created': created})
