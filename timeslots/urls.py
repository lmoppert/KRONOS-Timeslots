"""URLs for the Timeslots application."""

# pylint:disable=C0301
from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from timeslots.views import (JobListView, JobTableView, SlotView, UserProfile,
                             BlockingForm, DayLoggingArchive,
                             MonthLoggingArchive)

urlpatterns = patterns(
    'timeslots.views',
    url(r'^$', 'index', name='timeslots_home'),
    url(r'^logout/$', 'logout_then_login', name='user_logout'),
    url(r'^station/(?P<station_id>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/slotstatus/(?P<slot_id>\d+)/$', 'slotstatus', name='timeslots_slot_progress'),  # NOQA
    url(r'^station/(?P<pk>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/slots/$',
        SlotView.as_view()),
    url(r'^station/(?P<pk>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/joblist/$',
        JobListView.as_view()),
    url(r'^station/(?P<pk>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/jobtable/$',
        JobTableView.as_view()),
    url(r'^station/(?P<pk>\d+)/$', SlotView.as_view(),
        name='timeslots_station_detail'),
    url(r'^station/$', 'station_redirect', name='timeslots_station'),
    url(r'^logging/$', 'logging_redirect', name='timeslots_logging'),
    url(r'^logging/export/(?P<year>\d{4})-(?P<month>\d{2})/$',
        'logging_export', name='timeslots_logging_export'),
    url(r'^date/(?P<date>\d{4}-\d{2}-\d{2})/slot/(?P<block_id>\d+)\.(?P<timeslot>\d+)\.(?P<line>\d+)/$', 'slot', name='timeslots_slot_detail'),  # NOQA
    #url(r'^blocking/$', 'blocking', name='timeslots_blocking'),
    url(r'^blocking/$', BlockingForm.as_view(), name='timeslots_blocking'),
    url(r'^profile/$', 'profile', name='timeslots_userprofile_detail'),
    url(r'^password_changed/$', 'password_change_done'),
    url(r'^users/$', 'users', name='timeslots_user_list'),
    url(r'^imprint/$',
        TemplateView.as_view(template_name='timeslots/imprint.html'),
        name='timeslots_imprint'),

)
urlpatterns += patterns(
    'django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'timeslots/user_login.html'},
        name='user_login'),
    url(r'^password/$', 'password_change', {
        'post_change_redirect': '/timeslots/password_changed/',
        'template_name': 'timeslots/password_change_form.html'},
        name='timeslots_change_password'),
)
urlpatterns += patterns(
    '',
    url(r'^userprofile/$', UserProfile.as_view(),
        name='timeslots_userprofile_form'),
    url(r'^logging/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/$',
        DayLoggingArchive.as_view(), name='timeslots_logging_day'),
    url(r'^logging/(?P<year>\d{4})-(?P<month>\d{2})/$',
        MonthLoggingArchive.as_view(), name='timeslots_logging_month'),
)
