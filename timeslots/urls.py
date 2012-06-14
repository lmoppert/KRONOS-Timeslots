from datetime import datetime
from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from timeslots.models import Station, Dock, Slot, UserProfile

urlpatterns = patterns('timeslots.views',
    url(r'^$', 'index'),
    url(r'^logout$', 'logout_then_login'),
    url(r'^user/(?P<pk>\d+)/$', DetailView.as_view(model=UserProfile)),
    url(r'^station/(?P<pk>\d+)/date/(?P<date>\d{4}-\d{2}-\d{2})/$', 'station'),
    url(r'^station/(?P<pk>\d+)/$', 'station', {'date': datetime.now().strftime("%Y-%m-%d")}),
    url(r'^station/$', 'station_redirect'),
    url(r'^date/(?P<date>\d{4}-\d{2}-\d{2})/slot/(?P<block_id>\d+)\.(?P<index>\d+)\.(?P<line>\d+)/$', 'slot'),
    url(r'^dock/(?P<pk>\d+)/$', DetailView.as_view(model=Dock)),
)
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'timeslots/login.html'}, name='user_login'),
)
