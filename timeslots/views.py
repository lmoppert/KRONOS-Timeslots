"""Module with class based views and view functions for the Timeslots app."""

from django.db.models import F
from django.shortcuts import (
    get_object_or_404, get_list_or_404, render, redirect)
from django.http import HttpResponseRedirect, HttpResponse

from django.views.generic.edit import UpdateView
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
from timeslots.utils import (daterange, delete_slot_garbage, log_task,
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
        msg = "User %s tried to export logfiles" % request.user
        msg += "but is not a member of a master group"
        log_task(request, msg)
        msg = _("You are not authorized to access this page!")
        messages.error(request, msg)
        return HttpResponseRedirect('/timeslots/profile/')
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
        msg = "User %s tried to access the user list " % request.user
        msg += "but is not member of a master group"
        log_task(request, msg)
        msg = _("You are not authorized to access this page!")
        messages.error(request, msg)
        return HttpResponseRedirect('/timeslots/profile/')
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
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (
            station_id, date))
    else:
        msg = "User %s tried to change the status " % request.user
        msg += "of slot %s but is not allowed to." % curr_slot
        log_task(request, msg)
        msg = _('You are not allowed to change the status of a slot!')
        messages.error(request, msg)
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (
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
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (
            curr_station, date))


@login_required
def blocking(request):
    """Return the slot blocking form."""
    if not request.user.userprofile.is_master:
        log = "User %s tried to access the blocking view but is not member " \
            "of a master group" % request.user
        log_task(request, log)
        msg = _("You are not authorized to access this page!")
        messages.error(request, msg)
        return HttpResponseRedirect('/timeslots/profile/')
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
                log = "User %s blocked slots %s from %s to %s for block %s"
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
                log = "User %s released slots %s from %s to %s for block %s"
                msg = _("successfully released the selected slots!")
            log_task(request,
                     log % (request.user, form['slots'].value(),
                            form['start'].value(), form['end'].value(), block))
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('timeslots_blocking'))
        else:
            form.helper.form_show_errors = False
    else:
        form = BlockSlotForm(
            stations=request.user.userprofile.stations.values('id'))
    return render(request, 'timeslots/blocking.html', {'form': form})


@login_required
def station(request, station_id, date, view_mode):
    """ Return the main view for a station.

    Displays the blocks ( see :model:`timeslots.Block`) of a
    :model:`timeslots.Station` or the jobs (table- or listview) for a specific
    date.

    """

    # check conditions
    curr_station = get_object_or_404(Station, pk=station_id)
    if (not curr_station.opened_on_weekend and
            not request.user.userprofile.is_master and
            datetime.strptime(date, "%Y-%m-%d").date().weekday() > 4):
        msg = "User %s tried to access the weekend view of " % request.user
        msg += "station %s, which is not opened on weekends." % curr_station
        log_task(request, msg)
        messages.error(request, _('This station is closed on weekends!'))
        diff = 7 - datetime.strptime(date, "%Y-%m-%d").date().weekday()
        monday = datetime.strptime(date, "%Y-%m-%d").date() + timedelta(
            days=diff)
        date = monday.strftime("%Y-%m-%d")
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/'
                                    % (curr_station.id, date))
    if request.user.userprofile.stations.filter(id=station_id).count() == 0:
        msg = "User %s tried to access " % request.user
        msg += "station %s without authorization" % curr_station
        log_task(request, msg)
        msg = _("You are not authorized to access this station!")
        messages.error(request, msg)
        return HttpResponseRedirect('/timeslots/profile/')
    if (curr_station.docks.count() == 0 and curr_station.scales.count() > 1):
        return HttpResponseRedirect('/station/%s/scales/' % curr_station.id)
    if (view_mode == 'slots' and not request.user.userprofile.is_master and
        curr_station.past_deadline(datetime.strptime(date, "%Y-%m-%d"),
                                   datetime.now())):
        messages.warning(request,
                         _('The reservation deadline has been reached, no '
                           'more reservations will be accepted!'))

    # prepare context items
    if request.method == 'POST':
        selected_docks = request.POST.getlist('selectedDocks')
        request.session['selectedDocks'] = selected_docks
    if 'selectedDocks' in request.session:
        docklist = []
        for dock_id in request.session['selectedDocks']:
            docklist.append(curr_station.dock_set.get(pk=dock_id))
        dock_count = len(docklist)
    else:
        docklist = curr_station.dock_set.all()
        dock_count = docklist.count()

    delete_slot_garbage(request)
    if not view_mode == 'slots':
        slotlist = {}
        docks = []
        for dock in docklist:
            slotlist[dock.name] = []
            docks.append((dock.name, dock.id))

        # get all slots for one date
        if request.user.userprofile.is_master or \
           request.user.userprofile.is_viewer:
            slots = list(Slot.objects.filter(date=date))
        else:
            slots = list(Slot.objects.filter(date=date).filter(
                company=request.user.userprofile.id))

        if view_mode == 'jobtable':
            jobs = []
            for curr_slot in slots:
                if ((curr_slot.block.dock.name in slotlist and
                     curr_slot.block.dock.station.id == curr_station.id
                     and not curr_slot.is_blocked)):
                    for job in curr_slot.job_set.all():
                        jobs.append(job)
            table = StationJobTable(jobs)
            #RequestConfig(request, paginate={"per_page": 25}).configure(table)
            RequestConfig(request, paginate=False).configure(table)
            return render(request, 'timeslots/job_table.html', {
                'station': curr_station, 'date': date, 'table': table,
                'docks': docks, 'target': "jobtable"})
        else:
            for curr_slot in slots:
                if (curr_slot.block.dock.name in slotlist and
                    curr_slot.block.dock.station.id == curr_station.id
                    and (not curr_slot.is_blocked
                         or curr_slot.job_set.count() > 0)):
                    slotlist[curr_slot.block.dock.name].append(curr_slot)

        return render(request, 'timeslots/job_list.html', {
            'station': curr_station, 'date': date, 'slotlist': slotlist,
            'docks': docks, 'target': "joblist"})
    else:
        docks = []
        for dock in docklist:
            blocks = []
            for block in dock.block_set.all():
                if (block.max_slots > 0 and
                        block.get_slots(date) >= block.max_slots):
                    msg = _('The maximal number of Slots have been reserved, '
                            'no more reservations will be accepted!')
                    messages.warning(request, msg)
                timeslots = []
                for timeslot in range(block.slotcount):
                    lines = []
                    for line in range(block.linecount):
                        try:
                            curr_slot = block.slot_set.filter(date=date).get(
                                date=date,
                                timeslot=timeslot + 1,
                                line=line + 1,
                                block=block.id
                            )
                            company = curr_slot.status(request.user)
                        except ObjectDoesNotExist:
                            company = ugettext_noop("free")
                        if company in ("free", "blocked"):
                            lines.append((company, None))
                        else:
                            lines.append((company, curr_slot))
                    time = block.start_times[int(timeslot)].strftime("%H:%M")
                    timeslots.append((time, lines))
                blocks.append((str(block.id), timeslots))
            docks.append((dock.name, blocks))
        if dock_count == 1:
            span = "span12"
        elif dock_count == 2:
            span = "span6"
        elif dock_count == 3:
            span = "span4"
        else:
            span = "span3"

    if request.user.userprofile.is_master:
        hidden = ()
    else:
        hidden = ("blocked", "reserved")
    return render(request, 'timeslots/station_detail.html', {
        'station': curr_station, 'date': date, 'docks': docks, 'span': span,
        'target': "slots", 'hidden': hidden})


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
        log_task(request, "Readonly user %s tried to access slot %s."
                 % (request.user, curr_slot))
        messages.error(request, _('You are not allowed to change this slot!'))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/jobtable/'
                                    % (block.dock.station.id, date))
    if ((not curr_slot.block.dock.station.opened_on_weekend
         and not request.user.userprofile.is_master
         and datetime.strptime(date, "%Y-%m-%d").date().weekday() > 4)):
        if created:
            curr_slot.delete()
        log_task(request, "User %s tried to access slot %s, which is not "
                 "opened on weekends." % (request.user, curr_slot))
        messages.error(request, _('This station is closed on weekends!'))
        return HttpResponseRedirect('/timeslots/profile/')
    if not request.user.userprofile.is_master and curr_slot.is_blocked:
        log_task(request, "User %s tried to access slot %s which is blocked."
                 % (request.user, curr_slot))
        messages.error(request, _('This slot has been blocked!'))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/'
                                    % (block.dock.station.id, date))
    if (created and not request.user.userprofile.is_master and
        curr_slot.block.dock.station.past_deadline(
            datetime.strptime(date, "%Y-%m-%d"), datetime.now())):
        curr_slot.delete()
        log_task(request, "User %s tried to reserve slot %s after the "
                 "booking deadline has been reached."
                 % (request.user, curr_slot))
        messages.error(request,
                       _("The deadline for booking this slot has ended!"))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/'
                                    % (block.dock.station.id, date))
    if ((created and block.max_slots > 0
         and block.get_slots(date) > block.max_slots)):
        curr_slot.delete()
        log_task(request, "User %s tried to reserve slot %s after the "
                 "maximum number of blocks per day has been reached."
                 % (request.user, curr_slot))
        messages.error(request, _("The maximal number of Slots have been "
                                  "reserved, no more reservations will be "
                                  "accepted!"))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/'
                                    % (block.dock.station.id, date))
    if ((not created and not request.user.userprofile.is_master
         and curr_slot.past_rnvp(datetime.now()))):
        log_task(request, "User %s tried to change slot %s after the rnvp "
                 "deadline has been reached." % (request.user, curr_slot))
        messages.error(request, _("This slot can not be changed any more!"))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/'
                                    % (block.dock.station.id, date))
    if ((not request.user.userprofile.is_master
         and curr_slot.company.user.id != request.user.id)):
        if created:
            curr_slot.delete()
        log_task(request, "User %s tried to access slot %s which is "
                 "reserved for a different user." % (request.user, curr_slot))
        messages.error(request, _("This slot was already booked by a "
                                  "different person!"))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/'
                                    % (block.dock.station.id, date))

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
                log_task(request, "User %s has successfully reserved slot %s."
                         % (request.user, curr_slot))
                messages.success(request, _("The reservation has been saved "
                                            "successfully!"))
                return HttpResponseRedirect(
                    '/timeslots/station/%s/date/%s/slots/'
                    % (block.dock.station.id, date))
            else:
                log_task(request, "User %s has submitted a reservation "
                         "form for slot %s which contained errors."
                         % (request.user, curr_slot))
        elif ('cancelReservation' in request.POST or
                'deleteSlot' in request.POST):
            curr_slot.delete()
            for job in curr_slot.job_set.all():
                job.delete()
            log_task(request, "User %s has successfully deleted the "
                     "reservation for slot %s." % (request.user, curr_slot))
            messages.success(request, _("The reservation has been deleted "
                                        "successfully!"))
            return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/'
                                        % (block.dock.station.id, date))
        elif 'cancelEditing' in request.POST:
            return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/'
                                        % (block.dock.station.id, date))
        elif 'releaseSlot' in request.POST:
            curr_slot.is_blocked = False
            curr_slot.save()
            log_task(request, "User %s has successfully released the "
                     "blocking of slot %s." % (request.user, curr_slot))
            messages.success(request, _('This slot is no longer blocked!'))
            return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/'
                                        % (block.dock.station.id, date))
        elif 'keepSlotBlocked' in request.POST:
            return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/'
                                        % (block.dock.station.id, date))
    else:
        # This one has to go into the else path, otherwise errors
        # formset.non_form_errors are overwritten
        log_task(request,
                 "User %s has opened the reservation form for slot %s."
                 % (request.user, curr_slot))
        if block.dock.station.multiple_charges:
            formset = JobForm(instance=curr_slot)
        else:
            formset = SingleJobForm(instance=curr_slot)

    return render(request, 'timeslots/slot_detail.html', {
        'date': date, 'curr_block': block, 'times': times,
        'station': block.dock.station, 'slot': curr_slot, 'form': formset,
        'created': created})
