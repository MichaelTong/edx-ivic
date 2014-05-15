from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'djangoapp.views.home', name='home'),
    url(r'^profile/$','djangoapp.views.profile'),
    url(r'^profile/(?P<username>.+)/template/(?P<tp>[A-Za-z0-9]{8}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{12})/$','djangoapp.views.template'),
    url(r'^profile/(?P<username>.+)/template/(?P<tp>[A-Za-z0-9]{8}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{12})/delete/$','djangoapp.views.delete'),
    url(r'^profile/(?P<username>.+)/template/(?P<tp>[A-Za-z0-9]{8}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{12})/request/$','djangoapp.views.tpreq'),
    url(r'^profile/(?P<username>.+)/template/(?P<tp>[A-Za-z0-9]{8}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{4}\-[A-Za-z0-9]{12})/howtoadd/$','djangoapp.views.tphowto'),
    url(r'^add/$','djangoapp.views.add'),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(r'^signup/$','djangoapp.views.signup'),
    url(r'^check/$','djangoapp.vmtemplates.verification.check_username'),
    url(r'^logout/$','djangoapp.vmtemplates.verification.signout'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'home.html'}),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT }),
    )
