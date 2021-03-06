from django.db.models import F
from django.shortcuts import get_object_or_404, get_list_or_404, render
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
from datetime import datetime

from timeslots.models import *
from timeslots.forms import *
from timeslots.tables import *
from timeslots.utils import *
import csv


# Class-Based-Views
@cbv_decorator(login_required)
class UserProfile(UpdateView):
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        self.request.session['django_language'] = form.instance.language
        return super(UserProfile, self).form_valid(form)


@cbv_decorator(user_passes_test(lambda u: u.userprofile.is_master))
class DockProducts(UpdateView):
    form_class = DockProductsForm

    def get_object(self, queryset=None):
        dock = Dock.objects.get(pk=self.kwargs['dock_id'])
        date = self.kwargs['date']
        product, created = Product.objects.get_or_create(dock=dock, date=date)
        return product

    def get_context_data(self, **kwargs):
        kwargs['dock'] = Dock.objects.get(pk=self.kwargs['dock_id'])
        kwargs['date'] = self.kwargs['date']
        if 'form' not in kwargs:
            product_form = self.get_form()
            product_form.helper.form_action = reverse(
                'timeslots_products_form', kwargs={
                    'dock_id': self.kwargs['dock_id'],
                    'date': self.kwargs['date'],
                })
            kwargs['form'] = self.get_form()
        return super(DockProducts, self).get_context_data(**kwargs)


class LoggingArchive():
    model = Logging
    month_format = "%m"
    date_field = 'time'
    allow_empty = True
    template_name = 'timeslots/logging.html'


@cbv_decorator(user_passes_test(lambda u: u.userprofile.is_master))
class DayLoggingArchive(LoggingArchive, DayArchiveView):
    pass


@cbv_decorator(user_passes_test(lambda u: u.userprofile.is_master))
class MonthLoggingArchive(LoggingArchive, MonthArchiveView):
    pass


# View functions
def imprint(request):
    return render(request, 'timeslots/imprint.html')


def privacy(request):
    return render(request, 'timeslots/privacy.html')


@login_required
def logging_redirect(request):
    t = datetime.now()
    return HttpResponseRedirect(reverse('timeslots_logging_day', kwargs={
        'year': t.strftime("%Y"),
        'month': t.strftime("%m"),
        'day': t.strftime("%d")
    }))


@login_required
def logging_export(request, year, month):
    if not request.user.userprofile.is_master:
        msg = "User %s tried to export logfiles" % request.user
        msg += "but is not a member of a master group"
        log_task(request, msg)
        msg = _("You are not authorized to access this page!")
        messages.error(request, msg)
        return HttpResponseRedirect('/app/profile/')
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
    logout_then_login(request)


@login_required
def password_change_done(request):
    messages.success(request, _('Your password has been changed!'))
    return HttpResponseRedirect('/app/profile/')


@login_required
def profile(request):
    return render(request, 'timeslots/userprofile_detail.html')


@login_required
def users(request):
    if not request.user.userprofile.is_master:
        msg = "User %s tried to access the user list " % request.user
        msg += "but is not member of a master group"
        log_task(request, msg)
        msg = _("You are not authorized to access this page!")
        messages.error(request, msg)
        return HttpResponseRedirect('/app/profile/')
    users = get_list_or_404(User, is_active=True)
    table = UserTable(users)
    RequestConfig(request, paginate={"per_page": 10}).configure(table)
    return render(request, 'timeslots/user_list.html', {'table': table})


@login_required
def slotstatus(request, slot_id, station_id, date):
    slot = get_object_or_404(Slot, pk=slot_id)
    if request.user.userprofile.is_master:
        if slot.progress < 3:
            slot.progress = F('progress') + 1
            slot.save()
        else:
            slot.progress = 0
            slot.save()
        return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (
            station_id, date))
    else:
        msg = "User %s tried to change the status " % request.user
        msg += "of slot %s but is not allowed to." % slot
        log_task(request, msg)
        msg = _('You are not allowed to change the status of a slot!')
        messages.error(request, msg)
        return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (
            station_id, date))


@login_required
def index(request):
    jobs = []
    delete_slot_garbage(request)
    slots = request.user.userprofile.slot_set.filter(date__gt=datetime.now())
    for slot in slots:
        for job in slot.job_set.all():
            jobs.append(job)
    table = UserJobTable(jobs)
    RequestConfig(request, paginate={"per_page": 5}).configure(table)
    return render(request, 'index.html', {'table': table})


@login_required
def station_redirect(request):
    if request.method == 'POST':
        station = request.POST['selectedStation']
        date = request.POST['currentDate']
        try:
            del request.session['selectedDocks']
        except KeyError:
            pass
        return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (
            station, date))


@login_required
def blocking(request):
    if not request.user.userprofile.is_master:
        msg = "User %s tried to access the blocking view but " % request.user
        msg += "is not member of a master group"
        log_task(request, msg)
        msg = _("You are not authorized to access this page!")
        messages.error(request, msg)
        return HttpResponseRedirect('/app/profile/')
    if (request.method == 'POST' and
            'block' in request.POST and
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
                        slot, created = Slot.objects.get_or_create(
                            block=block,
                            date=day.strftime("%Y-%m-%d"),
                            timeslot=str(int(timeslot)),
                            line=str(line + 1),
                            defaults={'company': request.user.userprofile}
                        )
                        if not created and not slot.is_blocked:
                            reserved_slots.append(slot)
                        slot.is_blocked = 'blockSlots' in request.POST
                        slot.save()
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


def get_products(dock, date):
    details = ""
    products = Product.objects.filter(dock=dock, date=date)
    if not products:
        products = Product.objects.filter(dock=dock, date__lt=date)
    if products:
        details += "{}".format(products.last().details)
    else:
        details = _('No product details available')
    return details


@login_required
def station(request, station_id, date, view_mode):
    """
      Displays the blocks ( see :model:`timeslots.Block`) of
      a :model:`timeslots.Station` or the jobs (table- or listview) for a
      specific date
    """
    # check conditions
    station = get_object_or_404(Station, pk=station_id)
    if (not station.opened_on_weekend and
            not request.user.userprofile.is_master and
            datetime.strptime(date, "%Y-%m-%d").date().weekday() > 4):
        msg = "User %s tried to access the weekend view of " % request.user
        msg += "station %s, which is not opened on weekends." % station
        log_task(request, msg)
        messages.error(request, _('This station is closed on weekends!'))
        diff = 7 - datetime.strptime(date, "%Y-%m-%d").date().weekday()
        monday = datetime.strptime(date, "%Y-%m-%d").date() + timedelta(days=diff)
        date = monday.strftime("%Y-%m-%d")
        return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (station.id, date))
    if request.user.userprofile.stations.filter(id=station_id).count() == 0:
        msg = "User %s tried to access " % request.user
        msg += "station %s without authorization" % station
        log_task(request, msg)
        msg = _("You are not authorized to access this station!")
        messages.error(request, msg)
        return HttpResponseRedirect('/app/profile/')
    if (view_mode == 'slots' and not request.user.userprofile.is_master and
        station.past_deadline(datetime.strptime(date, "%Y-%m-%d"),
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
            docklist.append(station.dock_set.get(pk=dock_id))
        dock_count = len(docklist)
    else:
        docklist = station.dock_set.all()
        dock_count = docklist.count()

    delete_slot_garbage(request)
    if not view_mode == 'slots':
        slotlist = {}
        docks = []
        for dock in docklist:
            slotlist[dock.name] = []
            docks.append((dock.name, dock.id))

        # get all slots for one date
        if request.user.userprofile.is_master or request.user.userprofile.is_viewer:
            slots = list(Slot.objects.filter(date=date))
        else:
            slots = list(Slot.objects.filter(date=date).filter(
                company=request.user.userprofile.id))

        if view_mode == 'jobtable':
            jobs = []
            for slot in slots:
                if (slot.block.dock.name in slotlist and
                        slot.block.dock.station.id == station.id and
                        not slot.is_blocked):
                    for job in slot.job_set.all():
                        jobs.append(job)
            table = StationJobTable(jobs)
            #RequestConfig(request, paginate={"per_page": 25}).configure(table)
            RequestConfig(request, paginate=False).configure(table)
            return render(request, 'timeslots/job_table.html', {
                'station': station, 'date': date, 'table': table,
                'docks': docks, 'target': "jobtable"})
        else:
            for slot in slots:
                if (slot.block.dock.name in slotlist and
                        slot.block.dock.station.id == station.id and
                        (not slot.is_blocked or slot.job_set.count() > 0)):
                    slotlist[slot.block.dock.name].append(slot)

        return render(request, 'timeslots/job_list.html', {
            'station': station, 'date': date, 'slotlist': slotlist,
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
                            slot = block.slot_set.filter(date=date).get(
                                date=date,
                                timeslot=timeslot + 1,
                                line=line + 1,
                                block=block.id
                            )
                            company = slot.status(request.user)
                        except ObjectDoesNotExist:
                            company = ugettext_noop("free")
                        if company in ("free", "blocked"):
                            lines.append((company, None))
                        else:
                            lines.append((company, slot))
                    time = block.start_times[int(timeslot)].strftime("%H:%M")
                    timeslots.append((time, lines))
                blocks.append((str(block.id), timeslots))
            if dock.station.has_product:
                products = get_products(dock, date)
                docks.append(([dock.name, products, dock.id], blocks))
            else:
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
        'station': station, 'date': date, 'docks': docks, 'span': span,
        'target': "slots", 'hidden': hidden})


@login_required
def slot(request, date, block_id, timeslot, line):
    """
      Displays details for a :model:`timeslots.Slot`

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
    slot, created = Slot.objects.get_or_create(
        date=date, timeslot=timeslot, line=line, block=block,
        defaults={'company': request.user.userprofile}
    )

    # check conditions
    if request.user.userprofile.is_readonly:
        log_task(request, "Readonly user %s tried to access slot %s." % (request.user, slot))
        messages.error(request, _('You are not allowed to change this slot!'))
        return HttpResponseRedirect('/app/station/%s/date/%s/jobtable/' % (block.dock.station.id, date))
    if not slot.block.dock.station.opened_on_weekend and not request.user.userprofile.is_master and datetime.strptime(date, "%Y-%m-%d").date().weekday() > 4:
        if created:
            slot.delete()
        log_task(request, "User %s tried to access slot %s, which is not opened on weekends." % (request.user, slot))
        messages.error(request, _('This station is closed on weekends!'))
        return HttpResponseRedirect('/app/profile/')
    if not request.user.userprofile.is_master and slot.is_blocked:
        log_task(request, "User %s tried to access slot %s which is blocked." % (request.user, slot))
        messages.error(request, _('This slot has been blocked!'))
        return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (block.dock.station.id, date))
    if created and not request.user.userprofile.is_master and slot.block.dock.station.past_deadline(datetime.strptime(date, "%Y-%m-%d"), datetime.now()):
        slot.delete()
        log_task(request, "User %s tried to reserve slot %s after the booking deadline has been reached." % (request.user, slot))
        messages.error(request, _('The deadline for booking this slot has ended!'))
        return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (block.dock.station.id, date))
    if created and block.max_slots > 0 and block.get_slots(date) > block.max_slots:
        slot.delete()
        log_task(request, "User %s tried to reserve slot %s after the maximum number of blocks per day has been reached." % (request.user, slot))
        messages.error(request, _('The maximal number of Slots have been reserved, no more reservations will be accepted!'))
        return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (block.dock.station.id, date))
    if not created and not request.user.userprofile.is_master and slot.past_rnvp(datetime.now()):
        log_task(request, "User %s tried to change slot %s after the rnvp deadline has been reached." % (request.user, slot))
        messages.error(request, _('This slot can not be changed any more!'))
        return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (block.dock.station.id, date))
    if not request.user.userprofile.is_master and slot.company.user.id != request.user.id:
        if created:
            slot.delete()
        log_task(request, "User %s tried to access slot %s which is reserved for a different user." % (request.user, slot))
        messages.error(request, _('This slot was already booked by a different person!'))
        return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (block.dock.station.id, date))

    # process request
    if request.method == 'POST':
        if 'makeReservation' in request.POST:
            if block.dock.station.multiple_charges:
                formset = JobForm(request.POST, instance=slot)
            else:
                formset = SingleJobForm(request.POST, instance=slot)
            if formset.is_valid():
                if 'is_klv' in request.POST:
                    slot.is_klv = True
                slot.save()
                formset.save()
                log_task(request, "User %s has successfully reserved slot %s." % (request.user, slot))
                messages.success(request, _('The reservation has been saved successfully!'))
                return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (block.dock.station.id, date))
            else:
                log_task(request, "User %s has submitted a reservation form for slot %s which contained errors." % (request.user, slot))
        elif ('cancelReservation' in request.POST or
                'deleteSlot' in request.POST):
            slot.delete()
            for job in slot.job_set.all():
                job.delete()
            log_task(request, "User %s has successfully deleted the reservation for slot %s." % (request.user, slot))
            messages.success(request, _('The reservation has been deleted successfully!'))
            return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (block.dock.station.id, date))
        elif 'cancelEditing' in request.POST:
            return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (block.dock.station.id, date))
        elif 'releaseSlot' in request.POST:
            slot.is_blocked = False
            slot.save()
            log_task(request, "User %s has successfully released the blocking of slot %s." % (request.user, slot))
            messages.success(request, _('This slot is no longer blocked!'))
            return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (block.dock.station.id, date))
        elif 'keepSlotBlocked' in request.POST:
            return HttpResponseRedirect('/app/station/%s/date/%s/slots/' % (block.dock.station.id, date))
    else:
        # This one has to go into the else path, otherwise errors formset.non_form_errors are overwritten
        log_task(request, "User %s has opened the reservation form for slot %s." % (request.user, slot))
        if block.dock.station.multiple_charges:
            formset = JobForm(instance=slot)
        else:
            formset = SingleJobForm(instance=slot)

    return render(request, 'timeslots/slot_detail.html', {
        'date': date, 'curr_block': block, 'times': times,
        'station': block.dock.station, 'slot': slot, 'form': formset,
        'created': created})
