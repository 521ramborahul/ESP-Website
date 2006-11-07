from django.conf.urls.defaults import *
from esp.program.models import Class

#	This is a lookup for the redirector, to insert a certain string for the tree node 
section_redirect_keys = {'teach': 'Programs',
						'learn': 'Programs',
						'program': 'Programs',
						'help': 'ESP/Committees',
						None: 'Web'}

urlpatterns = patterns('',
    # Example:
    # (r'^esp/', include('esp.apps.foo.urls.foo')),

    (r'^beta/satprep.csv$', 'esp.satprep.views.satprep_csv'),

    # The default
    (r'^$', 'esp.web.views.index'),

    # Generic view for starting a class
    (r'^startaclass/', 'django.views.generic.create_update.create_object', { 'model': Class } ),

    # aseering - Features that are decidedly not done, but are still useable, will end up under "beta/"
    (r'^beta/calendar.ics$', 'esp.web.views.iCalFeed'),

    # Mini-Blog pages
	(r'^(?P<subsection>teach|learn|help)/(?P<url>.*)/blog/$', 'esp.miniblog.views.show_miniblog', {'section_redirect_keys': section_redirect_keys}),
	(r'^blog/post/$', 'esp.miniblog.views.post_miniblog'),
    (r'^blog/(?P<url>.*)/post/$', 'esp.miniblog.views.post_miniblog'),
    (r'^blog/(?P<url>.*)/$', 'esp.miniblog.views.show_miniblog_entry'),

    # aseering - Is it worth consolidating these?  Two entries for the single "contact us! widget
    # Contact Us! pages
    (r'^contact/contact.html$', 'esp.web.views.contact'),
    (r'^contact/submit.html$', 'esp.web.views.contact_submit'),

    (r'^(teach|learn)/teachers/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/bio.html$', 'esp.web.views.bio'),
    (r'^(teach|learn)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/?$', 'esp.web.views.program'),
    (r'^(teach|learn)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/([-A-Za-z0-9_ ]+)/?$', 'esp.web.views.program'),
    #(r'^(learn|teach)/([-A-Za-z0-9/_ ]+)/([-A-Za-z0-9_ ]+).html$', 'esp.web.views.redirect'),
    (r'^program/Template/$', 'esp.program.views.programTemplateEditor'),
    (r'^program/(?P<program>[-A-Za-z0-9_ ]+)/(?P<session>[-A-Za-z0-9_ ]+)/Classes/Template/$', 'esp.program.views.classTemplateEditor'),
	
    (r'^(?P<subsection>(learn|teach|program|help))/(?P<url>.*).html$', 'esp.web.views.redirect', { 'section_redirect_keys': section_redirect_keys } ),
	
	#	This same URL pattern also handles the battlescreen  -Michael
    (r'^myesp/([-A-Za-z0-9_ ]+)/?$', 'esp.web.views.myesp'),

    # Event-generation
    (r'^events/create/$', 'esp.calendar.views.createevent'),
    (r'^events/edit/$', 'esp.calendar.views.updateevent'),
    (r'^events/edit/(?P<id>\d+)/$', 'esp.calendar.views.updateevent'),

    # DB-generated QSD pages: HTML or plaintext
    (r'^(?P<url>.*)\.html$', 'esp.web.views.redirect', { 'section_redirect_keys': section_redirect_keys } ),
    #(r'^(?P<url>.*)\.text$', 'esp.qsd.views.qsd_raw'),

    # Possibly overspecific, possibly too general.
    (r'^(?P<url>.*)/media/(?P<filename>[^/]+\.[^/]{1,4})$', 'esp.qsdmedia.views.qsdmedia'),

    # Update navbar
    (r'^navbar/edit.scm', 'esp.web.navBar.updateNavBar'),

    # Reimbursement requests
    (r'^money/reimbursement/$', 'esp.money.views.create_reimbursement'),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),

    # Uncomment this for @login_required:
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
	
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'C:\Documents and Settings\Michael P\Desktop\work\esp_website\esp\media'}),

    # Class-edit interface
    (r'^classes/edit/(?P<id>[0-9]*)/$', 'esp.program.views.updateClass')
	

)
