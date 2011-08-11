from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^js/', include('test_jsmvc.urls')),
    url(r'^blogs/', include('blogs.urls')),
    url(r'^comments/', include('blogs.comments.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^ratings/', include('ratings.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^', include('blogs.urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
