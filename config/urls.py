from django.conf.urls.static import static
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from timeslots import views

# admin.autodiscover()

urlpatterns = [
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
    # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
