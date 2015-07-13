from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
import settings

urlpatterns = patterns('',
    # Example:
    # (r'^polls/', include('polls.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^djpoll/(?P<djpoll_id>[^/]+)/$', 'djpoll.views.inicio'),
    (r'^djpoll/guardar/1/$', 'djpoll.views.guardar'),
    (r'^djpoll/reportes/1/$', 'djpoll.views.reportes'),
    (r'^djpoll/simular/1/$', 'djpoll.views.simular'),
    (r'^djpoll/proyecto/1/$', 'djpoll.views.crearProyecto'),
    (r'^djpoll/subirArchivo$', 'djpoll.views.subirArchivo'),
    (r'^login/$', 'djpoll.views.login'),
    (r'^logout/$', 'djpoll.views.logout'),
    (r'^inicio/$', 'djpoll.views.index'),
    (r'^$', 'djpoll.views.redirec'),
)

urlpatterns += patterns('',
        (r'%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'), 'django.views.static.serve',{'document_root' : settings.MEDIA_ROOT }),)

handler404 = 'djpoll.views.error_404'
handler500 = 'djpoll.views.error_404'