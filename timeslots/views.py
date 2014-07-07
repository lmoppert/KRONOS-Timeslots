"""Module with class based views and view functions for the Timeslots app."""

from django.db.models import F
from django.shortcuts import (get_object_or_404, get_list_or_404, render,
                              redirect)
from django.http import HttpResponse

from django.views.generic import UpdateView, DetailView, FormView  # , View
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
            self.docks = request.POST.getlist('selectedDocks')
            request.session['selectedDocks'] = self.docks
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
        context['date'] = str(self.date)
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


class SlotList(StationView):
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
            msg = _("The reservation deadline has been reached, no more "
                    "reservations will be accepted!")
            messages.warning(request, msg)
        return super(SlotList, self).handle_conditions(request, date)

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
        context = super(SlotList, self).get_context_data(**kwargs)
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


@cbv_decorator(login_required)
class BlockingForm(FormView):
    """Return the slot blocking form."""

    template_name = 'timeslots/blocking.html'
    form_class = BlockSlotForm

    def dispatch(self, request, *args, **kwargs):
        url = self.handle_conditions(request)
        if url:
            return redirect(url)
        return super(BlockingForm, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if ('block' in request.POST and request.POST.get('block') != ""):
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
                return self.form_valid(form, block, timeslots)
            else:
                return self.form_invalid(form)

    def form_invalid(self, form):
        form.helper.form_show_errors = False
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form, block, timeslots):
        reserved_slots = []
        for day in daterange(form['start'].value(),
                             form['end'].value()):
            for timeslot in form['slots'].value():
                for line in range(block.linecount):
                    curr_slot, created = Slot.objects.get_or_create(
                        block=block,
                        date=day.strftime("%Y-%m-%d"),
                        timeslot=str(int(timeslot)),
                        line=str(line + 1),
                        defaults={'company': self.request.user.userprofile}
                    )
                    if not created and not curr_slot.is_blocked:
                        reserved_slots.append(curr_slot)
                    curr_slot.is_blocked = 'blockSlots' in self.request.POST
                    curr_slot.save()
        log = "User {user} %s slots %s from %s to %s for block %s"
        if 'blockSlots' in self.request.POST:
            task = "blocked"
            msg = _("successfully blocked the selected slots!")
            if len(reserved_slots) > 0:
                msg = _("The slots listed below had already been "
                        "reserved before you blocked them. You can "
                        "click on the link if you want to relase a "
                        "slot. use <CTRL><click> to open the "
                        "slot-form (in a new window or tab)")
                messages.warning(self.request, msg)
                return render(self.request, 'timeslots/blocked.html', {
                    'slots': reserved_slots})
        else:
            task = "released"
            log += "{object}"
        log_msg(self.request, log % (task, form['slots'].value(),
                                     form['start'].value(),
                                     form['end'].value(), block))
        msg = _("successfully %s the selected slots!")
        messages.success(self.request, msg % task)
        return redirect(reverse('timeslots_blocking'))

    def get(self, request, *args, **kwargs):
        form = BlockSlotForm(
            stations=request.user.userprofile.stations.values('id'))
        return render(request, self.template_name, {'form': form})

    def handle_conditions(self, request):
        if not request.user.userprofile.is_master:
            msg = "User {user} tried to access the blocking view but is not "
            msg += "member of a master group"
            log_msg(request, msg)
            msg = _("You are not authorized to access this page!")
            messages.error(request, msg)
            return '/timeslots/profile/'


@cbv_decorator(login_required)
class SlotView(DetailView):
    """ Return details for a :model:`timeslots.Slot`.

    **Context**

    ``RequestContext``

    ``block``
    An instance of :model:`timeslots.Block`

    """

    model = Slot
    created = False
    date = datetime.now().strftime('%Y-%m-%d')
    template_name = 'timeslots/slot_detail.html'

    def slot_reservation(self, request, *args, **kwargs):
        if self.block.dock.station.multiple_charges:
            formset = JobForm(self.request.POST, instance=self.object)
        else:
            formset = SingleJobForm(self.request.POST, instance=self.object)
        if formset.is_valid():
            if 'is_klv' in request.POST:
                self.object.is_klv = True
            self.object.save()
            formset.save()
            log = "User {user} has successfully reserved slot {object}."
            msg = _("The reservation has been saved successfully!")
            log_msg(request, log, self.object)
            messages.success(request, msg)
            return redirect('/timeslots/station/%s/date/%s/slots/' % (
                self.block.dock.station.id, self.date))
        else:
            log = "User {user} has submitted a reservation form for slot "
            log += "{object} which contained errors."
            log_msg(request, log, self.object)
            return self.get(request, *args, **kwargs)

    def slot_delete(self, request):
        self.object.delete()
        for job in self.object.job_set.all():
            job.delete()
        msg = "User {user} has successfully deleted the reservation for "
        msg += "slot {object}."
        log_msg(request, msg, self.object)
        msg = _("The reservation has been deleted successfully!")
        messages.success(request, msg)
        return redirect('/timeslots/station/%s/date/%s/slots/' % (
            self.block.dock.station.id, self.date))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(**kwargs)
        self.get_context_data(object=self.object)
        if 'makeReservation' in request.POST:
            return self.slot_reservation(request, *args, **kwargs)
        elif ('cancelReservation' in request.POST
                or 'deleteSlot' in request.POST):
            return self.slot_delete(request)
        elif 'cancelEditing' in request.POST:
            return redirect('/timeslots/station/%s/date/%s/slots/' % (
                self.block.dock.station.id, self.date))
        elif 'releaseSlot' in request.POST:
            self.object.is_blocked = False
            self.object.save()
            msg = "User {user} has successfully released the blocking of "
            msg += "slot {object}."
            log_msg(request, msg, self.object)
            messages.success(request, _('This slot is no longer blocked!'))
            return redirect('/timeslots/station/%s/date/%s/slots/' % (
                self.block.dock.station.id, self.date))
        elif 'keepSlotBlocked' in request.POST:
            return redirect('/timeslots/station/%s/date/%s/slots/' % (
                self.block.dock.station.id, self.date))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(**kwargs)
        context = self.get_context_data(object=self.object)
        if not self.request.user.userprofile.is_master:
            url = self.handle_conditions(request, self.date)
            if url:
                return redirect(url)
        delete_slot_garbage(request)
        msg = "User {user} has opened the reservation form for slot {object}."
        log_msg(request, msg, self.object)
        return self.render_to_response(context)

    def get_object(self, **kwargs):
        self.date = self.kwargs['date']
        self.block = get_object_or_404(Block, pk=kwargs['block_id'])
        self.timeslot = kwargs['timeslot']
        self.line = kwargs['line']
        slot, self.created = Slot.objects.get_or_create(
            date=self.date,
            timeslot=self.timeslot,
            line=self.line,
            block=self.block,
            defaults={'company': self.request.user.userprofile}
        )
        return slot

    def get_context_data(self, **kwargs):
        context = super(SlotView, self).get_context_data(**kwargs)
        try:
            end = self.block.start_times[int(self.timeslot)]
        except IndexError:
            end = self.block.end
        times = self.block.start_times[int(self.timeslot) - 1].strftime(
            "%H:%M") + " - " + end.strftime("%H:%M")
        context['times'] = times
        if self.block.dock.station.multiple_charges:
            formset = JobForm(instance=self.object)
        else:
            formset = SingleJobForm(instance=self.object)
        context['form'] = formset
        context['slot'] = self.object
        context['object'] = self.object
        context['date'] = self.date
        context['curr_block'] = self.block
        context['station'] = self.block.dock.station
        context['created'] = self.created
        return context

    def handle_conditions_with_deletion(self, request):
        redirect = False
        if ((self.created and self.block.max_slots > 0
                and self.block.get_slots(self.date) > self.block.max_slots)):
            log = "User {user} tried to reserve slot {object} after the "
            log += "maximum number of blocks per day has been reached."
            msg = _("The maximal number of Slots have been reserved, no more "
                    "reservations will be accepted!")
            redirect = True
        if ((not self.object.block.dock.station.opened_on_weekend
                and datetime.strptime(self.date,
                                      "%Y-%m-%d").date().weekday() > 4)):
            log = "User {user} tried to access slot {object}, which is not "
            log += "opened on weekends."
            msg = _('This station is closed on weekends!')
            redirect = True
        if (self.created and self.object.block.dock.station.past_deadline(
                datetime.strptime(self.date, "%Y-%m-%d"), datetime.now())):
            log = "User {user} tried to reserve slot {object} after the "
            log += "booking deadline has been reached."
            msg = _("The deadline for booking this slot has ended!")
            redirect = True
        if (self.object.company.user.id != request.user.id):
            log = "User {user} tried to access slot {object} which is "
            log += "reserved for a different user."
            msg = _("This slot was already booked by a different person!")
            redirect = True
        if redirect:
            log_msg(request, log, self.object)
            messages.error(request, msg)
            if self.created:
                self.object.delete()
            url = '/timeslots/station/%s/date/%s/slots/'
            return url % (self.block.dock.station.id, self.date)

    def handle_conditions(self, request):
        redirect = False
        if request.user.userprofile.is_readonly:
            log = "Readonly user {user} tried to access slot {object}."
            msg = _('You are not allowed to change this slot!')
            redirect = True
        if (self.object.is_blocked):
            log = "User {user} tried to access slot {object} which is blocked."
            msg = _('This slot has been blocked!')
            redirect = True
        if (not self.created and self.object.past_rnvp(datetime.now())):
            log = "User {user} tried to change slot {object} after the rnvp "
            log += "deadline has been reached."
            msg = _("This slot can not be changed any more!")
            redirect = True
        if redirect:
            log_msg(request, log, self.object)
            messages.error(request, msg)
            url = '/timeslots/station/%s/date/%s/slots/'
            return url % (self.block.dock.station.id, self.date)
        else:
            return self.handle_conditions_with_deletion(request)


@cbv_decorator(login_required)
class SiloView(DetailView):
    """Base Class for stations with scales."""

    model = Station
    date = datetime.now().strftime('%Y-%m-%d')
    target = 'silos'
    scales = []  # List of tuples: (dock_name, dock_id)


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
        if 'selectedDocks' in request.session:
            del request.session['selectedDocks']
        return redirect('/timeslots/station/%s/date/%s/slots/' % (
            curr_station, date))
