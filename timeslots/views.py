from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
#from django.http import HttpResponseRedirect, HttpResponse
#from django.core.urlresolvers import reverse
from django.template import RequestContext
from timeslots.models import Station, Dock, Line

@login_required
def index(request):
    station_list = get_list_or_404(Station)
    return render_to_response('index.html', {'station_list': station_list}, context_instance=RequestContext(request))
