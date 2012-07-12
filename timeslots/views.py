from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from timeslots.models import Station, Dock, Block, Slot
from timeslots.forms import *

def logout_page(request):
    logout_then_login(request)

@login_required
def keco(request):
    return render_to_response('bars.html', context_instance=RequestContext(request))

@login_required
def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

@login_required
def station_redirect(request):
    if request.method == 'POST':
        station = request.POST['selectedStation']
        date = request.POST['currentDate']
        return HttpResponseRedirect('/timeslots/station/%s/date/%s' % (station, date))

@login_required
def station(request, station_id, date):
    """
      Displays the blocks ( see :model:`timeslots.Block`) of a :model:`timeslots.Station` 
      for a specific date
    """
    # check permissions
    if request.user.userprofile.stations.filter(id=station_id).count() == 0:
        messages.error(request, 'Auf diese Ladestelle haben Sie keinen Zugriff!')
        return HttpResponseRedirect('/timeslots/user/%s' % (request.user.id))

    # prepare context items
    station = get_object_or_404(Station, pk=station_id)
    if request.method == 'POST':
        # ToDo: write docklist into session variable and do let the following processing depend on that with fallback <all>
        docklist = []
        for dock_id in request.POST.getlist('selectedDocks'):
            docklist.append(station.dock_set.get(pk=dock_id))
        dock_count = len(docklist)
    else:
        docklist = station.dock_set.all()
        dock_count = docklist.count()
    docks = []
    for dock in docklist:
        blocks = []
        for block in dock.block_set.all(): 
            timeslots = []
            for timeslot in range(block.slotcount): 
                lines = []
                for line in range(block.linecount): 
                    try:
                        slot = block.slot_set.filter(date=date).get(date=date, timeslot=timeslot+1, line=line+1, block=block.id)
                        company = slot.status(request.user)
                    except ObjectDoesNotExist:
                        company = "free"
                    lines.append(company)
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

    # process request
    return render_to_response('timeslots/station_detail.html', 
            { 'station': station, 'date': date, 'docks': docks, 'span': span}, 
            context_instance=RequestContext(request))

@login_required
def jobs(request, station_id, date):
    """
      Displays all jobs for the current company for a given date
    """
    # check permissions
    if request.user.userprofile.stations.filter(id=station_id).count() == 0:
        messages.error(request, 'Auf diese Ladestelle haben Sie keinen Zugriff!')
        return HttpResponseRedirect('/timeslots/user/%s' % (request.user.id))

    # prepare context items
    station = get_object_or_404(Station, pk=station_id)
    if request.method == 'POST':
        docklist = []
        for dock_id in request.POST.getlist('selectedDocks'):
            docklist.append(station.dock_set.get(pk=dock_id))
    else:
        docklist = station.dock_set.all()
    slotlist = {}
    docks = []
    for dock in docklist:
        slotlist[dock.name] = []
        docks.append((dock.name, dock.id))
    slots = list(Slot.objects.filter(date=date)) 
    for slot in slots:
        slotlist[slot.block.dock.name].append(slot)

    # process request
    return render_to_response('timeslots/job_list.html', 
            { 'station': station, 'date': date, 'slotlist': slotlist, 'docks': docks, 'target': "jobs"}, 
            context_instance=RequestContext(request))

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
    slot, created = Slot.objects.get_or_create(date=date, timeslot=timeslot, line=line, block=block, 
                    defaults={'company': request.user.userprofile})

    # check permissions
    if slot.company.user.id != request.user.id:
        messages.error(request, 'Dieser Slot ist bereits durch jemand anderen reserviert worden!')
        return HttpResponseRedirect('/timeslots/station/%s/date/%s' % (block.dock.station.id, date))

    # process request
    if request.method == 'POST' and request.POST.has_key('makeReservation'):
        formset = JobFormSet(request.POST, instance=slot)
        if formset.is_valid():
            slot.save()
            formset.save()
            messages.success(request, 'Die Reservierung wurde erfolgreich gespeichert!')
            return HttpResponseRedirect('/timeslots/station/%s/date/%s' % (block.dock.station.id, date))
    elif request.method == 'POST' and request.POST.has_key('cancelReservation'):
        slot.delete()
        for job in slot.job_set.all():
            job.delete()
        messages.success(request, 'Die Reservierung wurde erfolgreich geloescht!')
        return HttpResponseRedirect('/timeslots/station/%s/date/%s' % (block.dock.station.id, date))

    # ToDo: AJAXify the job table (add and remove jobs from the list)
    formset = JobFormSet(instance=slot)
    return render_to_response('timeslots/slot_detail.html', 
            {'date': date, 'curr_block': block, 'times': times, 'station': block.dock.station, 'slot': slot, 'form': formset, 'created': created}, 
            context_instance=RequestContext(request))

# ToDo: implement i18n for all views
# ToDo: add a logging feature
# ToDo: make blocking of slots possible for loadmasters
# ToDo: restrict tasks with roles and permissions
# ToDo: restrict reservation by deadline
# ToDo: restrict slot changes by rnvp
# ToDo: generate a view for the jobs of a company
