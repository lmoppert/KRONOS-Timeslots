from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from timeslots.models import Station, Dock, Slot

urlpatterns = patterns('timeslots.views',
    url(r'^$', 'index'),
    url(r'^station/(?P<pk>\d+)/$', DetailView.as_view(model=Station)),
    url(r'^dock/(?P<pk>\d+)/$', DetailView.as_view(model=Dock)),
)
