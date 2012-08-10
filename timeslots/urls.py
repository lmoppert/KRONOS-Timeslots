from datetime import datetime
from django.conf.urls import patterns, url
from timeslots.views import UserProfile
from timeslots.models import Station

urlpatterns = patterns('timeslots.views',
    url(r'^$', 'index', name='timeslots_home'),
    url(r'^logout/$', 'logout_then_login', name='user_logout'),
    url(r'^station/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/slotstatus/(?P<slot_id>\d+)/$', 'slotstatus', name='timeslots_slot_progress'),
    url(r'^station/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/slots/$', 'station', {'view_mode': 'slots'}),
    url(r'^station/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/joblist/$', 'station', {'view_mode': 'joblist'}),
    url(r'^station/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/jobtable/$', 'station', {'view_mode': 'jobtable'}),
    url(r'^station/(?P<station_id>\d+)/$', 'station', {'date': datetime.now().strftime("%Y-%m-%d"), 'view_mode': 'slots'}, name='timeslots_station_detail'),
    url(r'^station/$', 'station_redirect'),
    url(r'^date/(?P<date>\d{4}-\d{2}-\d{2})/slot/(?P<block_id>\d+)\.(?P<timeslot>\d+)\.(?P<line>\d+)/$', 'slot', name='timeslots_slot_detail'),
    url(r'^profile/$', 'profile', name='timeslots_userprofile_detail'),
    url(r'^blocking/$', 'blocking', name='timeslots_blocking'),
)
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'timeslots/user_login.html'}, name='user_login'),
    url(r'^password/$', 'password_change', {'template_name': 'timeslots/password_change_form.html'}, name='timeslots_change_password'),
    url(r'^password/changed/$', 'password_change_done', name='timeslots_change_password'),
)
from django.views.generic import DetailView
urlpatterns += patterns('',
    url(r'^userprofile/$', UserProfile.as_view(), name='timeslots_userprofile_form'),
)
