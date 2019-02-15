from django.views.generic.base import TemplateView, RedirectView
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from timeslots import views

# admin.autodiscover()

urlpatterns = [
    url(r'^migration/', TemplateView.as_view(template_name="migration.html")),
    url(r'^timeslots/', RedirectView.as_view(url="/")),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^app/', include('timeslots.urls')),
    url(r'^$', views.index, name='home'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'', include('django.contrib.staticfiles.urls')),
    ]
