from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from timeslots.models import Station, Dock, Line
from django.contrib.auth import logout

def logout_page(request):
    logout_then_login(request)

@login_required
def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

