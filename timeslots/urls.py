from datetime import datetime
from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from timeslots.models import Station, Dock, Slot, UserProfile

urlpatterns = patterns('timeslots.views',
    url(r'^$', 'index'),
    url(r'^logout$', 'logout_then_login'),
    url(r'^keco/$', 'keco'),
    url(r'^station/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/$', 'station'),
    url(r'^station/(?P<station_id>\d+)/$', 'station', {'date': datetime.now().strftime("%Y-%m-%d")}, name='timeslots_station_detail'),
    url(r'^station/$', 'station_redirect'),
    url(r'^jobs/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/$', 'jobs'),
    url(r'^date/(?P<date>\d{4}-\d{2}-\d{2})/slot/(?P<block_id>\d+)\.(?P<timeslot>\d+)\.(?P<line>\d+)/$',
        'slot', name='timeslots_slot_detail'),
    url(r'^dock/(?P<pk>\d+)/$', DetailView.as_view(model=Dock)),
    url(r'^user/(?P<pk>\d+)/$', DetailView.as_view(model=UserProfile, template_name='timeslots/user_detail.html')),
)
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'timeslots/user_login.html'}, name='user_login'),
)
