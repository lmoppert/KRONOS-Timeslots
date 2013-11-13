"""URL definitions."""

from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'timeslots.views.index', name='home'),
    url(r'^urls/$', 'timeslots.tests.urls.show_url_patterns', name='urls'),
    url(r'^timeslots/', include('timeslots.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
