from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from timeslots.models import Station

urlpatterns = patterns('',
    url(r'^$', 
        ListView.as_view(
            queryset=Station.objects,
            context_object_name='Station',
            template_name='index.html')),
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(model=Station)),
)
