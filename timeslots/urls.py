from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from timeslots.models import Station, Dock, Slot, UserProfile

urlpatterns = patterns('timeslots.views',
    url(r'^$', 'index'),
    url(r'^logout$', 'logout_then_login'),
    url(r'^station/(?P<pk>\d+)/$', DetailView.as_view(model=Station)),
    url(r'^dock/(?P<pk>\d+)/$', DetailView.as_view(model=Dock)),
    url(r'^user/(?P<pk>\d+)/$', DetailView.as_view(model=UserProfile)),
)
