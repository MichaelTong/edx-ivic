from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'djangoapp.views.home', name='home'),
    url(r'^profile/$','djangoapp.views.profile'),
    url(r'^template/(?P<tp>.*)/$','djangoapp.views.template'), #use 32 code
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(r'^signup/$','djangoapp.views.signup'),
    url(r'^login/$','djangoapp.vmtemplates.verification.signin'),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),
    )
