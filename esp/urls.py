from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^esp/', include('esp.apps.foo.urls.foo')),

    # The default
    (r'^$', 'esp.web.views.index'),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
)
