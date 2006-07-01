from django.shortcuts import render_to_response
from esp.calendar.models import Event

class navbar:
	navbar_data = [
		{ 'link': '/teach/what-to-teach.html',
		  'text': 'What You Can Teach',
		'indent': False },
		{ 'link': '/teach/prev-classes.html',
		  'text': 'Previous Classes',
		  'indent': False },
		{ 'link': '/teach/teaching-time.html',
		  'text': 'Time Commitments',
		  'indent': False },
		{ 'link': '/teach/training.html',
		  'text': 'Teacher Training',
		  'indent': False },
		{ 'link': '/teach/ta.html',
		  'text': 'Become a TA',
		  'indent': False },
		{ 'link': '/teach/coteach.html',
		  'text': 'Co-Teach',
		  'indent': False },
		{ 'link': '/teach/reimburse.html',
		  'text': 'Reimbursements',
		  'indent': False },
		{ 'link': '/programs/hssp/teach.html',
		  'text': 'HSSP',
		  'indent': False },
		{ 'link': '/teach/teacherinformation.html',
		  'text': 'Teacher Information',
		  'indent': True },
		{ 'link': '/programs/hssp/classreg.html',
		  'text': 'Class Registration',
		  'indent': True },
		{ 'link': '/programs/hssp/summerhssp.html',
		  'text': 'Summer HSSP',
		  'indent': False },
		{ 'link': '/programs/hssp/classreg.html',
		  'text': 'Class Registration',
		  'indent': True },
		{ 'link': '/programs/firehose/teach.html',
		  'text': 'Firehose',
		  'indent': False },
		{ 'link': '/programs/junction/teach.html',
		  'text': 'JUNCTION',
		  'indent': False },
		{ 'link': '/programs/junction/classreg.html',
		  'text': 'Class Registration',
		  'indent': True },
		{ 'link': '/programs/delve/teach.html',
		  'text': 'Delve (AP Program)',
		  'indent': False }
	]

class preloader:
	preload_images = [
		'/media/images/level3/nav/home_ro.gif',
		'/media/images/level3/nav/discoveresp_ro.gif',
		'/media/images/level3/nav/takeaclass_ro.gif',
		'/media/images/level3/nav/volunteertoteach_ro.gif',
		'/media/images/level3/nav/getinvolved_ro.gif',
		'/media/images/level3/nav/archivesresources_ro.gif',
		'/media/images/level3/nav/myesp_ro.gif',
		'/media/images/level3/nav/contactinfo_ro.gif'
	]
	  
class home(navbar,preloader):
	@staticmethod
	def index(request):
		latest_event_list = Event.objects.filter().order_by('-start')
		return render_to_response('index.html', {
				'navbar_list': navbar_data,
				'preload_images': preload_images
			})


def index(request):
	return home.index(request)
