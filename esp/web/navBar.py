from esp.web.models import NavBarEntry
from esp.users.models import UserBit
from esp.datatree.models import GetNode
from django.http import HttpResponseRedirect, Http404
from esp.datatree.models import DataTree

def makeNavBar(user, node):
	""" Query the navbar-entry table for all navbar entries associated with this tree node """
	qsdTree = NavBarEntry.objects.filter(path=node).order_by('sort_rank')
	#navbar_data = []
	#for entry in qsdTree:
	#	qd = {}
	#	qd['link'] = entry.link
	#	qd['text'] = entry.text
	#	qd['indent'] = entry.indent
	#	navbar_data.append(qd)
	#return navbar_data
	return { 'node': node,
		 'has_edit_bits': UserBit.UserHasPerms(user, node, GetNode('V/Administer')),
		 'qsdTree': qsdTree }



def updateNavBar(request):
	""" Update a NavBar entry with the specified data """

	for i in [ 'navbar_id', 'action', 'new_url', 'node_id' ]:
		# Info can come by way of GET or POST, so we're using REQUEST
		# Could trusting GET be a problem?; I'm assuming Django
		# sessions are still maintained properly, so I can do security that way
		if not request.REQUEST.has_key(i):
			#raise Http404
			assert False, "Need " + str(i)

	action = request.REQUEST['action']

	try:
		if request.REQUEST['node_id'] == '':
			node = None
		else:
			node = DataTree.objects.filter(pk=request.REQUEST['node_id'])[0]
	except Exception:
		# raise Http404
		raise

	try:
		if request.REQUEST['navbar_id'] == '':
			navbar = None
		else:
			navbar = NavBarEntry.objects.filter(pk=request.REQUEST['navbar_id'])[0]
	except Exception:
		#raise Http404
		raise

	if not actions.has_key(request.REQUEST['action']):
		#raise Http404
		assert False, "Need action"

	actions[action](request, navbar, node)

	return HttpResponseRedirect(request.REQUEST['new_url'])

def navBarUp(request, navbar, node):
	""" Swap the sort_rank of the specified NavBarEntry and the NavBarEntry immediately before it in the list of NavBarEntrys associated with this tree node, so that this NavBarEntry appears to move up one unit on the page

	Fail silently if this is not possible
	"""
	navbarList = NavBarEntry.objects.filter(path=navbar.path).order_by('sort_rank')

	last_n = None

	for n in navbarList:
		if navbar == n and last_n != None:
			temp_sort_rank = n.sort_rank
			n.sort_rank = last_n.sort_rank
			last_n.sort_rank = temp_sort_rank

			n.save()
			last_n.save()

		last_n = n
		
	
def navBarDown(request, navbar, node):
	""" Swap the sort_rank of the specified NavBarEntry and the NavBarEntry immediately after it in the list of NavBarEntrys associated with this tree node, so that this NavBarEntry appears to move down one unit on the page

	Fail silently if this is not possible
	"""
	navbarList = NavBarEntry.objects.filter(path=navbar.path).order_by('sort_rank')

	last_n = None

	for n in navbarList:
		if last_n != None and navbar == last_n:
			temp_sort_rank = n.sort_rank
			n.sort_rank = last_n.sort_rank
			last_n.sort_rank = temp_sort_rank

			n.save()
			last_n.save()

		last_n = n
		

def navBarNew(request, navbar, node):
	""" Create a new NavBarEntry.  Put it at the bottom of the current sort_rank. """
	try:
		max_sort_rank = NavBarEntry.objects.filter(path=node).order_by('-sort_rank')[0].sort_rank
	except Exception:
		raise
	#	max_sort_rank = -100

	new_sort_rank = max_sort_rank + 100

	try:
		entry = NavBarEntry()
		entry.path = node
		entry.sort_rank = new_sort_rank
		entry.link = request.POST['url']
		entry.text = request.POST['text']
		entry.indent = request.POST['indent']

		entry.save()
		
	except Exception:
		raise

	
def navBarDelete(request, navbar, node):
	navbar.delete()


actions = { 'up': navBarUp,
	    'down': navBarDown,
	    'new': navBarNew,
	    'delete': navBarDelete }

