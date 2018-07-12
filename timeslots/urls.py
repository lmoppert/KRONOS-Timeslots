from datetime import datetime
from django.conf.urls import url, include
from timeslots.views import UserProfile, DockProducts, DayLoggingArchive, MonthLoggingArchive
from timeslots import views

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    url(r'^$', views.index, name='timeslots_home'),
    url(r'^station/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/slotstatus/(?P<slot_id>\d+)/$', views.slotstatus, name='timeslots_slot_progress'),
    url(r'^station/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/slots/$', views.station, {'view_mode': 'slots'}, name='timeslots_slot_view'),
    url(r'^station/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/joblist/$', views.station, {'view_mode': 'joblist'}),
    url(r'^station/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/jobtable/$', views.station, {'view_mode': 'jobtable'}),
    url(r'^station/(?P<station_id>\d+)/$', views.station, {'date': datetime.now().strftime("%Y-%m-%d"), 'view_mode': 'slots'}, name='timeslots_station_detail'),
    url(r'^station/$', views.station_redirect, name='timeslots_station'),
    url(r'^logging/$', views.logging_redirect, name='timeslots_logging'),
    url(r'^logging/export/(?P<year>\d{4})-(?P<month>\d{2})/$', views.logging_export, name='timeslots_logging_export'),
    url(r'^date/(?P<date>\d{4}-\d{2}-\d{2})/slot/(?P<block_id>\d+)\.(?P<timeslot>\d+)\.(?P<line>\d+)/$', views.slot, name='timeslots_slot_detail'),
    url(r'^blocking/$', views.blocking, name='timeslots_blocking'),
    url(r'^profile/$', views.profile, name='timeslots_userprofile_detail'),
    url(r'^password_changed/$', views.password_change_done),
    url(r'^users/$', views.users, name='timeslots_user_list'),
    url(r'^imprint/$', views.imprint, name='timeslots_imprint'),
    url(r'^privacy/$', views.privacy, name='timeslots_privacy'),
    url(r'^userprofile/$', UserProfile.as_view(), name='timeslots_userprofile_form'),
    url(r'^dock/(?P<dock_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/products/$', DockProducts.as_view(), name='timeslots_products_form'),
    url(r'^logging/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/$', DayLoggingArchive.as_view(), name='timeslots_logging_day'),
    url(r'^logging/(?P<year>\d{4})-(?P<month>\d{2})/$', MonthLoggingArchive.as_view(), name='timeslots_logging_month'),
]
