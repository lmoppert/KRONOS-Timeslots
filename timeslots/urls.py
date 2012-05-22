from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from timeslots.models import Station

urlpatterns = patterns('timeslots.views',
    url(r'^$', 'index'),
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(model=Station)),
)
