from django.shortcuts import render_to_response
from esp.miniblog.models import Entry
from django.contrib.auth.models import User, AnonymousUser
from esp.datatree.models import GetNode
from esp.users.models import UserBit
from esp.dbmail.models import MessageRequest, EmailRequest
from esp.dbmail.controllers import EmailController
from esp.web.navBar import makeNavBar
from datetime import datetime

def show_miniblog(request, url, subsection = None, section_redirect_keys = {}, extramsg=''):
    """ Shows a miniblog based on the specified node """
    user = request.user
	
    if subsection == None:
        tree_branch = 'Web'
    else:
        tree_branch = section_redirect_keys[subsection]

    node = 'Q/' + tree_branch + '/' + str(url)
    qsc = GetNode(node)
        
    entries = Entry.find_posts_by_perms(user, GetNode('V/Subscribe'), qsc=qsc)

    return render_to_response('miniblog.html', { 'request': request,
                                                 'entries': entries,
                                                 'canpost': UserBit.UserHasPerms(user, qsc, GetNode('V/Administer/Edit/Use')),
												 'navbar_list': makeNavBar(request.user, qsc),
                                                 'webnode': str(url),
												 'logged_in': request.user.is_authenticated(),
                                                 'extramsg': extramsg })

def show_miniblog_entry(request, url, extramsg=''):
    """ Shows a miniblog based on the specified id """
    user = request.user
    entries = Entry.objects.filter(pk=int(url))

    # Assert permissions
    verb = GetNode( 'V/Subscribe' )
    for e in entries:
	    branch = e.anchor
	    if not UserBit.UserHasPerms( user, branch, verb ): assert False, "Insufficient permissions to view record"

    return render_to_response('miniblog.html', { 'request': request,
                                                 'entries': entries,
                                                 'canpost': UserBit.UserHasPerms(user, branch, GetNode('V/Administer/Edit/Use')),
												 'navbar_list': makeNavBar(request.user, branch),
                                                 'webnode': str(url),
												 'logged_in': request.user.is_authenticated(),
                                                 'extramsg': extramsg })


def create_miniblog(request, url, tree_prefix = ''):
	user = request.user
	qsc = GetNode('Q/' + tree_prefix + str(url))
	
	has_perms = UserBit.UserHasPerms(user, qsc, GetNode('V/Administer/Edit/Use'))
	
	if has_perms:
		initial_title = ''
		if (request.POST and request.POST.has_key('anntext')):
			initial_title = request.POST['anntext']
		create_form_block = {'action': '/blog/' + url + '/post/',
							'title': 'Create Announcement: ' + initial_title,
							'headers': ['Announcement Details'],
							'lineitems': [{'label': 'Announcement Title', 'variable': 'title', 'default': initial_title}],
							'textboxes': [{'label': 'Announcement Content', 'variable': 'content', 'default': ''}]
							}
		return render_to_response('battlescreens/editor', {'request': request,
															'navbar_list': makeNavBar(request.user, qsc),
															'blocks': [create_form_block]})
	else:
		assert False, 'Blog post failed.'

def post_miniblog(request, url, tree_prefix = ''):
    """ Add a post to a miniblog, then re-render the miniblog """
    for thing in ['title', 'content']:
        if not request.POST.has_key(thing):
            return show_miniblog(request, url, extramsg='Error: Failed post.  Please contact the server administrators.')

    user = request.user

    qsc = GetNode('Q/' + tree_prefix + str(url))

    has_perms = UserBit.UserHasPerms(user, qsc, GetNode('V/Administer/Edit/Use'))

    if has_perms:
        e = Entry()
        e.anchor = GetNode('Q/' + str(url))
        e.timestamp = datetime.now()
        e.title = request.POST['title']
        e.content = request.POST['content']
        e.save()
    else:
        return show_miniblog(request, '/blog/' + str(e.id) + '/', extramsg='Error: You don\'t have permission to post to this page.')

    return show_miniblog(request, '/blog/' + str(e.id) + '/')


#	Function for previewing announcements  - Michael P
#	Generates the block structure used by battle screens
def preview_miniblog(request, section):
	curUser = request.user
	sub = GetNode('V/Subscribe')
	ann_posts = Entry.find_posts_by_perms(curUser, sub)
	ann_posts.sort(key=lambda obj:obj.timestamp)
	
	ann_items = []
	
	if ann_posts:
		#	Show only the 5 [or whatever] most recent announcements
		max_announcements = 5;
		if (len(ann_posts) < max_announcements):
			max_announcements = len(ann_posts)
		
		for i in range(len(ann_posts) - max_announcements - 1, len(ann_posts) - 1):
			x = ann_posts[i]
			ann_items.append(['<a href="/blog/' + str(x.id) + '/">' + x.title + '</a>', None, '']);
			
		#	I've put a link in here to an all-announcements page that I didn't make yet.  Hold tight.
		if len(ann_posts) > 5:
			ann_items.append(['<b>' + str(len(ann_posts)) + ' total... </b><a href="/blog/announcements">see all</a>', None, ''])
	else:
		ann_items = [['No current announcements', None, '']]
	
	block_ann = 	{	'title' : 'Your Announcements',
						'headers' : None,
						'sections' : [{	'header': 'Recent Announcements',
										'items': ann_items}]}
	
	return block_ann
