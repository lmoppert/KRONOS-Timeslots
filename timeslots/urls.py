from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from timeslots.models import Ladestelle

urlpatterns = patterns('',
    url(r'^$', 
        ListView.as_view(
            queryset=Ladestelle.objects,
            context_object_name='Ladesellen')),
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(model=Ladestelle)),
)
