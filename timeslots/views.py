from django.db.models import Count, F
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.views.generic.edit import UpdateView

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_noop
from django.utils.timezone import now

from django_tables2 import RequestConfig
from datetime import datetime, time, timedelta

from timeslots.models import Station, Block, Slot, Logging, UserProfile
from timeslots.forms import *
from timeslots.tables import *


# Helper functions
def log_task(request, message):
    logentry = Logging.objects.create(
            user=request.user, 
            host=request.META.get('REMOTE_ADDR'), 
            task = message)
    logentry.save()

def daterange(start, end):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    for n in range(int ((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)

def delete_slot_garbage(request):
    # annotate creates a filterable value (properties cannot be accessed in filters)
    slots = Slot.objects.annotate(num_jobs=Count('job')).filter(num_jobs__exact=0)
    for slot in slots:
        if not slot.is_blocked and now() - slot.created > timedelta(minutes=5):
            log_task(request, "The garbage collector has deleted slot %s" % slot)
            slot.delete()

# Class-Based Views
class UserProfile(UpdateView):
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        return self.request.user.userprofile


# View functions
def logout_page(request):
    logout_then_login(request)

@login_required
def profile(request):
    return render(request, 'timeslots/user_detail.html')

@login_required
def slotstatus(request, slot_id, station_id, date):
    slot = get_object_or_404(Slot, pk=slot_id)
    if request.user.userprofile.is_master:
        if slot.progress < 4:
            slot.progress = F('progress') + 1
            slot.save()
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (station_id, date))
    else:
        log_task(request, "User %s tried to change the status of slot %s but is not allowed to." % (request.user, slot))
        messages.error(request, _('You are not allowed to change the status of a slot!'))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (station_id, date))

@login_required
def index(request):
    jobs = []
    delete_slot_garbage(request)
    slots =  request.user.userprofile.slot_set.filter(date__gt=datetime.now())
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
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (station, date))

@login_required
def blocking(request):
    if not request.user.userprofile.is_master:
        log_task(request, "User %s tried to access the blocking view but is not member of a master group" % request.user)
        messages.error(request, _("You are not authorized to access this page!"))
        return HttpResponseRedirect('/timeslots/profile/%s' % (request.user.id))
    if request.method == 'POST' and request.POST.has_key('block') and request.POST.get('block') != "":
        block = get_object_or_404(Block, pk=request.POST.get('block'))
        timeslots = []
        for t in block.start_times:
            timeslots.append(t.strftime("%H:%M"))
        form = BlockSlotForm(request.POST, 
                stations=request.user.userprofile.stations.values('id'), 
                timeslots=list(enumerate(timeslots, start=1))
                )
        if form.is_valid():
            reserved_slots = []
            for day in daterange(form['start'].value(), form['end'].value()):
                date=day.strftime("%Y-%m-%d") 
                for timeslot in form['slots'].value():
                    for line in range(block.linecount): 
                        slot, created = Slot.objects.get_or_create(
                                block=block,
                                date=day.strftime("%Y-%m-%d"),
                                timeslot=str(int(timeslot)),
                                line=str(line+1),
                                defaults={'company': request.user.userprofile}
                                )
                        if not created and not slot.is_blocked:
                            reserved_slots.append(slot)
                        slot.is_blocked = request.POST.has_key('blockSlots')
                        slot.save()
            if request.POST.has_key('blockSlots'):
                logmessage = "User %s blocked slots %s from %s to %s for block %s"
                usermessage = _("successfully blocked the selected slots!")
                if len(reserved_slots) > 0:
                    usermessage = _("The slots listed below had already been reserved before you blocked them. ")
                    usermessage += _("You can click on the link if you want to relase a slot. ")
                    usermessage += _("(use <CTRL><click> to open the slot-form in a new window or tab)")
                    messages.warning(request, usermessage)
                    return render(request, 'timeslots/blocked.html', {'slots': reserved_slots}) 
            else:
                logmessage = "User %s released slots %s from %s to %s for block %s"
                usermessage = _("successfully released the selected slots!")
            log_task(request, logmessage % (request.user, form['slots'].value(), form['start'].value(), form['end'].value(), block))
            messages.success(request, usermessage)
            return HttpResponseRedirect(reverse('timeslots_blocking'))
        else:
            form.helper.form_show_errors = False
    else:
        form = BlockSlotForm(stations=request.user.userprofile.stations.values('id'))
    return render(request, 'timeslots/blocking.html', {'form': form}) 

@login_required
def station(request, station_id, date, view_mode):
    """
      Displays the blocks ( see :model:`timeslots.Block`) of a :model:`timeslots.Station` 
      or the jobs (table- or listview) for a specific date
    """
    # check conditions
    station = get_object_or_404(Station, pk=station_id)
    if not station.opened_on_weekend and not request.user.userprofile.is_master and datetime.strptime(date, "%Y-%m-%d").date().weekday() > 4:
        log_task(request, "User %s tried to access the weekend view of station %s, which is not opened on weekends." % (request.user, station))
        messages.error(request, _('This station is closed on weekends!'))
        return HttpResponseRedirect('/timeslots/profile/%s' % (request.user.id))
    if request.user.userprofile.stations.filter(id=station_id).count() == 0:
        log_task(request, "User %s tried to access station %s without authorization" % (request.user, station))
        messages.error(request, _('You are not authorized to access this station!'))
        return HttpResponseRedirect('/timeslots/profile/%s' % (request.user.id))
    if view_mode == 'slots' and not request.user.userprofile.is_master and station.past_deadline(datetime.strptime(date, "%Y-%m-%d"), datetime.now()):
        messages.warning(request, _('The reservation deadline has been reached, no more reservations will be accepted!'))

    # prepare context items
    if request.method == 'POST':
        request.session['selectedDocks'] = request.POST.getlist('selectedDocks')
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

        if request.user.userprofile.is_master:
            slots = list(Slot.objects.filter(date=date)) 
        else:
            slots = list(Slot.objects.filter(date=date).filter(company=request.user.userprofile.id)) 

        if view_mode == 'jobtable':
            jobs = []
            for slot in slots:
                if slot.block.dock.name in slotlist and not slot.is_blocked:
                    for job in slot.job_set.all():
                        jobs.append(job)
            table = StationJobTable(jobs)
            RequestConfig(request, paginate={"per_page": 25}).configure(table)
            return render(request, 'timeslots/job_table.html', 
                    { 'station': station, 'date': date, 'table': table, 'docks': docks, 'target': "jobtable"}) 
        else:
            for slot in slots:
                if slot.block.dock.name in slotlist and (not slot.is_blocked or slot.job_set.count() >0):
                    slotlist[slot.block.dock.name].append(slot)

        return render(request, 'timeslots/job_list.html', 
                { 'station': station, 'date': date, 'slotlist': slotlist, 'docks': docks, 'target': "joblist"}) 
    else:
        docks = []
        for dock in docklist:
            blocks = []
            for block in dock.block_set.all(): 
                if block.max_slots > 0 and block.get_slots(date) >= block.max_slots:
                    messages.warning(request, _('The maximal number of Slots have been reserved, no more reservations will be accepted!'))
                timeslots = []
                for timeslot in range(block.slotcount): 
                    lines = []
                    for line in range(block.linecount): 
                        try:
                            slot = block.slot_set.filter(date=date).get(date=date, timeslot=timeslot+1, line=line+1, block=block.id)
                            company = slot.status(request.user)
                        except ObjectDoesNotExist:
                            company = ugettext_noop("free")
                        if company in ("free", "reserved", "blocked"):
                            lines.append((company, None))
                        else:
                            lines.append((company, slot))
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
    return render(request, 'timeslots/station_detail.html', 
            { 'station': station, 'date': date, 'docks': docks, 'span': span, 'target': "slots", 'hidden': hidden}) 


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
    times = block.start_times[int(timeslot)-1].strftime("%H:%M") + " - " + end.strftime("%H:%M")
    delete_slot_garbage(request)
    slot, created = Slot.objects.get_or_create(date=date, timeslot=timeslot, line=line, block=block, 
                    defaults={'company': request.user.userprofile})

    # check conditions
    if not slot.block.dock.station.opened_on_weekend and not request.user.userprofile.is_master and datetime.strptime(date, "%Y-%m-%d").date().weekday() > 4:
        if created:
            slot.delete()
        log_task(request, "User %s tried to access slot %s, which is not opened on weekends." % (request.user, slot))
        messages.error(request, _('This station is closed on weekends!'))
        return HttpResponseRedirect('/timeslots/profile/%s' % (request.user.id))
    if not request.user.userprofile.is_master and slot.is_blocked:
        log_task(request, "User %s tried to access slot %s which is blocked." % (request.user, slot))
        messages.error(request, _('This slot has been blocked!'))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (block.dock.station.id, date))
    if created and not request.user.userprofile.is_master and slot.block.dock.station.past_deadline(datetime.strptime(date, "%Y-%m-%d"), datetime.now()):
        slot.delete()
        log_task(request, "User %s tried to reserve slot %s after the booking deadline has been reached." % (request.user, slot))
        messages.error(request, _('The deadline for booking this slot has ended!'))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (block.dock.station.id, date))
    if created and block.max_slots > 0 and block.get_slots(date) >= block.max_slots:
        slot.delete()
        log_task(request, "User %s tried to reserve slot %s after the maximum number of blocks per day has been reached." % (request.user, slot))
        messages.error(request, _('The maximal number of Slots have been reserved, no more reservations will be accepted!'))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (block.dock.station.id, date))
    if not created and not request.user.userprofile.is_master and slot.past_rnvp(datetime.now()):
        log_task(request, "User %s tried to change slot %s after the rnvp deadline has been reached." % (request.user, slot))
        messages.error(request, _('This slot can not be changed any more!'))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (block.dock.station.id, date))
    if not request.user.userprofile.is_master and slot.company.user.id != request.user.id:
        if created:
            slot.delete()
        log_task(request, "User %s tried to access slot %s which is reserved for a different user." % (request.user, slot))
        messages.error(request, _('This slot was already booked by a different person!'))
        return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (block.dock.station.id, date))

    # process request
    if request.method == 'POST':
        if request.POST.has_key('makeReservation'):
            if block.dock.station.multiple_charges:
                formset = JobFormSet(request.POST, instance=slot)
            else:
                formset = SingleJobForm(request.POST, instance=slot)
            if formset.is_valid():
                slot.save()
                formset.save()
                log_task(request, "User %s has successfully reserved slot %s." % (request.user, slot))
                messages.success(request, _('The reservation has been saved successfully!'))
                return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (block.dock.station.id, date))
            else:
                log_task(request, "User %s has submitted a reservation form for slot %s which contained errors." % (request.user, slot))
        elif request.POST.has_key('cancelReservation') or request.POST.has_key('deleteSlot'):
            slot.delete()
            for job in slot.job_set.all():
                job.delete()
            log_task(request, "User %s has successfully deleted the reservation for slot %s." % (request.user, slot))
            messages.success(request, _('The reservation has been deleted successfully!'))
            return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (block.dock.station.id, date))
        elif request.POST.has_key('releaseSlot'):
            slot.is_blocked = False
            slot.save()
            log_task(request, "User %s has successfully released the blocking of slot %s." % (request.user, slot))
            messages.success(request, _('This slot is no longer blocked!'))
            return HttpResponseRedirect('/timeslots/station/%s/date/%s/slots/' % (block.dock.station.id, date))
    else:
        # This one has to go into the else path, otherwise errors formset.non_form_errors are overwritten
        log_task(request, "User %s has opened the reservation form for slot %s." % (request.user, slot))
        if block.dock.station.multiple_charges:
            formset = JobFormSet(instance=slot)
        else:
            formset = SingleJobForm(instance=slot)

    return render(request, 'timeslots/slot_detail.html', 
            {'date': date, 'curr_block': block, 'times': times, 'station': block.dock.station, 'slot': slot, 'form': formset, 'created': created}) 
