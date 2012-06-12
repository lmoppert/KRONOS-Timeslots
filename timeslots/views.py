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
    station = get_object_or_404(Station, pk=pk)
    return render_to_response('timeslots/station_detail.html', 
            { 'station': station, 'date': date}, 
            context_instance=RequestContext(request))

@login_required
def slot(request, date, block_id, index, line):
    block = get_object_or_404(Block, pk=block_id)
    try:
        end = block.start_times[int(index)]
    except IndexError:
        end = block.end
    timeslot = block.start_times[int(index)-1].strftime("%H:%M") + " - " + end.strftime("%H:%M")
    slot, created = Slot.objects.get_or_create(date=date, index=index, line=line, block=block, 
                    defaults={'company': request.user.userprofile})

    # Process request
    if request.method == 'POST':
        formset = JobFormSet(request.POST, instance=slot)
        if formset.is_valid():
            slot.save()
            formset.save()
            return HttpResponseRedirect('/timeslots/station/%s/date/%s' % (block.dock.station, date))

    formset = JobFormSet(instance=slot)
    return render_to_response('timeslots/slot_detail.html', 
            {'date': date, 'curr_block': block, 'timeslot': timeslot, 'station': block.dock.station, 'slot': slot, 'form': formset}, 
            context_instance=RequestContext(request))
