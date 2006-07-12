from django.conf.urls.defaults import *
from esp.program.models import Class

urlpatterns = patterns('',
    (r'^startaclass/', 'django.views.generic.create_update.create_object', { 'model': Class } ),
    # Example:
    # (r'^esp/', include('esp.apps.foo.urls.foo')),

    # The default
    (r'^$', 'esp.web.views.index'),
    (r'^contact.html$', 'esp.web.views.contact'),
    (r'^Learn/teachers/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/bio.html$', 'esp.web.views.bio'),
    (r'^(teach|learn)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/?$', 'esp.web.views.program'),
    (r'^(teach|learn)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/?$', 'esp.web.views.program'),
    (r'^(learn|teach)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+).html$', 'esp.web.views.redirect')
    (r'^myesp/([-A-Za-z0-9_ ]+)/?$', 'esp.web.views.myesp'),                       
    (r'^(?P<url>.*)\.html$', 'esp.web.views.qsd'),
    (r'^(?P<url>.*)\.text$', 'esp.web.views.qsd_raw'),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
)
