from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from timeslots.models import Station, Dock, Block, Slot
from timeslots.forms import *

def logout_page(request):
    logout_then_login(request)

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
def station(request, pk, date):
    """
    Displays the blocks ( see :model:`timeslots.Block`) of a :model:`timeslots.Station` 
    for a specific date
    """
    # prepare context items
    station = get_object_or_404(Station, pk=pk)
    docks = []
    for dock in station.dock_set.all(): 
        blocks = []
        for block in dock.block_set.all(): 
            timeslots = []
            for timeslot in range(block.slotcount): 
                lines = []
                for line in range(block.linecount): 
                    try:
                        slot = block.slot_set.filter(date=date).get(date=date, index=timeslot+1, line=line+1, block=block.id).company.company 
                    except ObjectDoesNotExist:
                        slot = "Freier Slot"
                    lines.append(slot)
                time = block.start_times[int(timeslot)].strftime("%H:%M")
                timeslots.append((time, lines))
            blocks.append((str(block.id), timeslots))
        docks.append((dock.name, blocks))
    dock_count = station.dock_set.count()
    if dock_count < 3:
        span = "span6" 
    elif dock_count == 3:
        span = "span4" 
    else:
        span = "span3" 

    # ToDo: add an oportunety to filter specific docks
    # ToDo: make table-width depend on number of docks shown

    # process request
    return render_to_response('timeslots/station_detail.html', 
            { 'station': station, 'date': date, 'docks': docks, 'span': span}, 
            context_instance=RequestContext(request))

@login_required
def slot(request, date, block_id, index, line):
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
        end = block.start_times[int(index)]
    except IndexError:
        end = block.end
    timeslot = block.start_times[int(index)-1].strftime("%H:%M") + " - " + end.strftime("%H:%M")
    slot, created = Slot.objects.get_or_create(date=date, index=index, line=line, block=block, 
                    defaults={'company': request.user.userprofile})

    # process request
    if request.method == 'POST':
        formset = JobFormSet(request.POST, instance=slot)
        if formset.is_valid():
            slot.save()
            formset.save()
            return HttpResponseRedirect('/timeslots/station/%s/date/%s' % (block.dock.station.id, date))

    # ToDo: AJAXify the job table
    formset = JobFormSet(instance=slot)
    return render_to_response('timeslots/slot_detail.html', 
            {'date': date, 'curr_block': block, 'timeslot': timeslot, 'station': block.dock.station, 'slot': slot, 'form': formset}, 
            context_instance=RequestContext(request))

# ToDo: generate a view for the jobs of a date
# ToDo: generate a view for the jobs of a company
# ToDo: implement i18n for all views
# ToDo: restrict tasks with roles and permissions
# ToDo: restrict reservation by deadline
# ToDo: restrict slot changes by rnvp
# ToDo: add a logging feature
