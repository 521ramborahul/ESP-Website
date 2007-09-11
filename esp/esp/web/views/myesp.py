
__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 MIT ESP

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Contact Us:
ESP Web Group
MIT Educational Studies Program,
84 Massachusetts Ave W20-467, Cambridge, MA 02139
Phone: 617-253-4882
Email: web@esp.mit.edu
"""
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from esp.cal.models import Event
from esp.qsd.models import QuasiStaticData
from esp.users.models import ContactInfo, UserBit, ESPUser, TeacherInfo, StudentInfo, EducatorInfo, GuardianInfo
from esp.program.models import RegistrationProfile
from esp.datatree.models import GetNode
from esp.miniblog.models import Entry
from esp.miniblog.views import preview_miniblog, create_miniblog
from esp.program.models import Program, RegistrationProfile, Class, ClassCategories
from esp.web.views.program import program_teacherreg2
from esp.dbmail.models import MessageRequest
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse, Http404, HttpResponseNotAllowed, HttpResponseRedirect
from django.template import loader, Context
from icalendar import Calendar, Event as CalEvent, UTC
import datetime
from django.contrib.auth.models import User
from esp.middleware import ESPError
from esp.web.models import NavBarEntry
from esp.users.manipulators import UserRegManipulator, UserPasswdManipulator, UserRecoverForm, SetPasswordForm
from esp.web.util.main import render_to_response
from django import forms
from esp.program.manipulators import StudentProfileManipulator, TeacherProfileManipulator, GuardianProfileManipulator, EducatorProfileManipulator, UserContactManipulator



@login_required
def myesp_passwd(request, module):
	""" Change password """
	if request.user.username == 'onsite':
		raise ESPError(), "Sorry, you're not allowed to change the password of this user. It's special."
	new_data = request.POST.copy()
	manipulator = UserPasswdManipulator(request.user)
	if request.method == "POST":
		errors = manipulator.get_validation_errors(new_data)
		if not errors:
			manipulator.do_html2python(new_data)
			user = authenticate(username=new_data['username'].lower(),
					    password=new_data['password'])
			
			user.set_password(new_data['newpasswd'])
			user.save()
			login(request, user)
			return render_to_response('users/passwd.html', request, GetNode('Q/Web/myesp'), {'Success': True})
	else:
		errors = {}
		
	return render_to_response('users/passwd.html', request, GetNode('Q/Web/myesp'), {'Problem': False,
						    'form':           forms.FormWrapper(manipulator, new_data, errors),
											 'Success': False})


def myesp_passrecover(request, module):
	""" Recover the password for a user """
	from esp.users.models import PersistentQueryFilter
	from django.template import loader
	from esp.db.models import Q
	
	new_data = request.POST.copy()
	manipulator = UserRecoverForm()
	
	
	if request.method == 'POST' and request.POST.has_key('prelim'):
		errors = manipulator.get_validation_errors(new_data)
		if not errors:
			try:
				user = User.objects.get(username = new_data['username'])
			except:
				raise ESPError(), 'Could not find user %s.' % new_data['username']

			user = ESPUser(user)
			user.recoverPassword()

			return render_to_response('users/requestrecover.html', request, GetNode('Q/Web/myesp'),{'Success': True})

	else:
		errors = {}

	return render_to_response('users/requestrecover.html', request, GetNode('Q/Web/myesp'),
				  {'form': forms.FormWrapper(manipulator, new_data, errors)})

def myesp_passemailrecover(request, module):
	new_data = request.POST.copy()
	manipulator = SetPasswordForm()

	success = False
	code = ''

	if request.GET.has_key('code'):
		code = request.GET['code']
	if request.POST.has_key('code'):
		code = request.POST['code']
	
	numusers = User.objects.filter(password = code).count()
	if numusers == 0:
		code = False
	
      	
	
	if request.method == 'POST':
		errors = manipulator.get_validation_errors(new_data)
		if not errors:
			user = User.objects.get(username = new_data['username'].lower())
			user.set_password(new_data['newpasswd'])
			user.save()
			auth_user = authenticate(username = new_data['username'].lower(), password = new_data['newpasswd'])
			login(request, auth_user)
			success = True
			
	else:
		errors = {}
		
	return render_to_response('users/emailrecover.html', request, GetNode('Q/Web/myesp'),
				  {'form': forms.FormWrapper(manipulator, new_data, errors),
				   'code': code,
				   'Success': success})
	

def myesp_home(request, module):
	""" Draw the ESP home page """
	curUser = request.user
	sub = GetNode('V/Subscribe')
	ann = Entry.find_posts_by_perms(curUser, sub)
	ann = [x.html() for x in ann]
	return render_to_response('display/battlescreen', request, GetNode('Q/Web/myesp'), {'announcements': ann})

#	Format for battlescreens 			Michael P
#	----------------------------------------------
#	The battle screen template is good for drawing individual blocks of helpful stuff.
#	So, it passes the template an array called blocks.

#	Each variable in the blocks array has:
#	-	title
#	-	array of 'header' html strings 
#		(in case you don't want to use separate sections)
#	-	array of sections

#	Each variable in the sections array has
#	-	header text including links
#	-	array of list items
#	-	list of input items
#	-	footer text including links / form items

#	The list item is displayed with a wide cell on the left followed by a narrow cell on the right.
#	The wide cell is like the name of some object to deal with,
#	and the narrow cell is like the administrative actions that can be applied to the object.
#	For example, the wide cell might have "Michael Price: Audio and Speakerbuilding" and the narrow cell
#	might be "Approve / Reject". 

#	An input item is a plain array of 4 containing
#	-	label text
#	-	text value (request.POST[value] = input_text)
#	-	button label (value)
#	-	form action (what URL the data is submitted to)

#	A list item is a plain array of 3 to 5 containing
#	-	left-hand (wide) cell text 
#	-	left-hand (wide) cell url
#	-	right-hand (narrow) cell html
#	-	OPTIONAL: command string
#	-	OPTIONAL: form post URL

#	That hopefully completes the array structure needed for this thing.


def myesp_battlescreen(request, module, admin_details = False, student_version = False):
	"""This function is the main battlescreen for the teachers. It will go through and show the classes
	that they can edit and display. """

	# request.user just got 1-up'd
	currentUser = ESPUser(request.user)

	if request.POST:
		#	If you clicked a button to approve or reject, first clear the "proposed" bit
		#	by setting the end date to now.
		if request.POST.has_key('command'):
			try:
				# not general yet...but started as 'edit','class','classid'...
				command, objtype, objid = request.POST['command'].split('_')
			except ValueError:
				command = None

			if command == 'edit' and objtype == 'class':
				clsid = int(objid) # we have a class
				clslist = list(Class.objects.filter(id = clsid))
				if len(clslist) != 1:
					assert False, 'Zero (or more than 1) classes match selected ID.'
				clsobj = clslist[0]
				prog = clsobj.parent_program
				two  = prog.anchor.name
				one  = prog.anchor.parent.name
				return program_teacherreg2(request, 'teach', one, two, 'teacherreg', '', prog, clsobj)
	
	# I have no idea what structure this is, but at its simplest level,
	# it's a dictionary
	announcements = preview_miniblog(request)

	usrPrograms = currentUser.getVisible(Program)

	# get a list of editable classes
	if student_version:
		clslist = currentUser.getEnrolledClasses()
	else:
		clslist = currentUser.getEditable(Class)

	fullclslist = {}
	
	# not the most direct way of doing it,
	# but hey, it's O(n) in class #, which
	# is nice.
	for cls in clslist:
		if fullclslist.has_key(cls.parent_program.id):
			fullclslist[cls.parent_program.id].append(cls)
		else:
			fullclslist[cls.parent_program.id] = [cls]
	
	# I don't like adding this second structure...
	# but django templates made me do it!
	responseProgs = []

	if admin_details:
		admPrograms = currentUser.getEditable(Program).order_by('-id')
	else:
		admPrograms = []
	
	for prog in usrPrograms:
		if not fullclslist.has_key(prog.id):
			curclslist = []
		else:
			curclslist = fullclslist[prog.id]
		responseProgs.append({'prog':        prog,
				      'clslist':     curclslist,
				      'shortened':   False,#len(curclslist) > 5,
				      'totalclsnum': len(curclslist)})

	return render_to_response('battlescreens/general.html', request, GetNode('Q/Web/myesp'), {'page_title':    'MyESP: Teacher Home Page',
								 'progList':      responseProgs,
								 'admin_details': admin_details,
								 'admPrograms'  : admPrograms,
								 'student_version': student_version,
								 'announcements': {'announcementList': announcements[:5],
										   'overflowed':       len(announcements) > 5,
										   'total':            len(announcements)}})


@login_required
def myesp_battlescreen_admin(request, module):
	curUser = ESPUser(request.user)
	if curUser.isAdministrator():
		return myesp_battlescreen(request, module, admin_details = True)
	else:
		raise Http404

@login_required
def myesp_battlescreen_student(request, module):
	curUser = ESPUser(request.user)
	if curUser.isStudent():
		return myesp_battlescreen(request, module, student_version = True)
	else:
		raise Http404


@login_required
def myesp_switchback(request, module):
	user = request.user
	user = ESPUser(user)
	user.updateOnsite(request)

	if not user.other_user:
		raise ESPError(), 'You were not another user!'

	return HttpResponseRedirect(user.switch_back(request))

@login_required
def edit_profile(request, module):


	curUser = ESPUser(request.user)

	dummyProgram = Program.objects.get(anchor = GetNode('Q/Programs/Dummy_Programs/Profile_Storage'))
	
	if curUser.isStudent():
		return profile_editor(request, None, True, 'Student')
	
	elif curUser.isTeacher():
		return profile_editor(request, None, True, 'Teacher')
	
	elif curUser.isGuardian():
		return profile_editor(request, None, True, 'Guardian')
	
	elif curUser.isEducator():
		return profile_editor(request, None, True, 'Educator')	

	else:
		return profile_editor(request, None, True, '')

@login_required
def profile_editor(request, prog_input=None, responseuponCompletion = True, role=''):
	""" Display the registration profile page, the page that contains the contact information for a student, as attached to a particular program """

	STUDREP_VERB = GetNode('V/Flags/UserRole/StudentRep')
	STUDREP_QSC  = GetNode('Q')

	
	if prog_input is None:
		prog = Program.objects.get(anchor = GetNode('Q/Programs/Dummy_Programs/Profile_Storage'))
		navnode = GetNode('Q/Web/myesp')
	else:
		prog = prog_input
		navnode = prog
		
	curUser = request.user
	role = role.lower();
	context = {'logged_in': request.user.is_authenticated() }
	context['user'] = request.user
	
	curUser = ESPUser(curUser)
	curUser.updateOnsite(request)
	
	manipulator = {'': UserContactManipulator(curUser),
		       'student': StudentProfileManipulator(curUser),
		       'teacher': TeacherProfileManipulator(curUser),
		       'guardian': GuardianProfileManipulator(curUser),
		       'educator': EducatorProfileManipulator(curUser)}[role]
	context['profiletype'] = role

	if request.method == 'POST' and request.POST.has_key('profile_page'):
		new_data = request.POST.copy()
		manipulator.prepare(new_data)
		errors = manipulator.get_validation_errors(new_data)
		if not errors:
			manipulator.do_html2python(new_data)

			regProf = RegistrationProfile.getLastForProgram(curUser, prog)

			if regProf.id is None:
				old_regProf = RegistrationProfile.getLastProfile(curUser)
			else:
				old_regProf = regProf

			for field_name in ['address_zip','address_city','address_street','address_state']:
				if new_data[field_name] != getattr(old_regProf.contact_user,field_name,False):
					new_data['address_postal'] = ''

			if new_data['address_postal'] == '':
				new_data['address_postal'] = False

			regProf.contact_user = ContactInfo.addOrUpdate(regProf, new_data, regProf.contact_user, '', curUser)
			regProf.contact_emergency = ContactInfo.addOrUpdate(regProf, new_data, regProf.contact_emergency, 'emerg_')

			if new_data.has_key('dietary_restrictions') and new_data['dietary_restrictions']:
				regProf.dietary_restrictions = new_data['dietary_restrictions']

			if role == 'student':
				regProf.student_info = StudentInfo.addOrUpdate(curUser, regProf, new_data)
				regProf.contact_guardian = ContactInfo.addOrUpdate(regProf, new_data, regProf.contact_guardian, 'guard_')
			elif role == 'teacher':
				regProf.teacher_info = TeacherInfo.addOrUpdate(curUser, regProf, new_data)
			elif role == 'guardian':
				regProf.teacher_info = GuardianInfo.addOrUpdate(curUser, regProf, new_data)
			elif role == 'educator':
				regProf.educator_info = EducatorInfo.addOrUpdate(curUser, regProf, new_data)
			blah = regProf.__dict__
			regProf.save()

			curUser.first_name = new_data['first_name']
			curUser.last_name  = new_data['last_name']
			curUser.email     = new_data['e_mail']
			curUser.save()
			if responseuponCompletion == True:
				return render_to_response('users/profile_complete.html', request, navnode, {})
			else:
				return True

	else:
		errors = {}
		if prog_input is None:
			regProf = RegistrationProfile.getLastProfile(curUser)
		else:
			regProf = RegistrationProfile.getLastForProgram(curUser, prog)
		if regProf.id is None:
			regProf = RegistrationProfile.getLastProfile(curUser)
		new_data = {}
		if curUser.isStudent():
			new_data['studentrep'] = (UserBit.objects.filter(user = curUser,
									 verb = STUDREP_VERB,
									 qsc  = STUDREP_QSC).count() > 0)
		new_data['first_name'] = curUser.first_name
		new_data['last_name']  = curUser.last_name
		new_data['e_mail']     = curUser.email
		new_data = regProf.updateForm(new_data, role)

	context['request'] = request
	context['form'] = forms.FormWrapper(manipulator, new_data, errors)
	return render_to_response('users/profile.html', request, navnode, context)

@login_required
def myesp_onsite(request, module):
	
	user = ESPUser(request.user)
	if not user.isOnsite():
		raise ESPError(False), 'You are not a valid on-site user, please go away.'
	verb = GetNode('V/Registration/OnSite')
	
	progs = UserBit.find_by_anchor_perms(Program, user = user, verb = verb)

	if len(progs) == 1:
		return HttpResponseRedirect('/onsite/%s/main' % progs[0].getUrlBase())
	else:
		navnode = GetNode('Q/Web/myesp')
		return render_to_response('program/pickonsite.html', request, navnode, {'progs': progs})

@login_required
def myesp_battlescreen_teacher(request, module):
	qscs = UserBit.bits_get_qsc(user=request.user, verb=GetNode("V/Flags/UserRole/Teacher"))
	if qscs.count() > 0:
		return myesp_battlescreen(request, module)
	else:
		raise Http404	


myesp_handlers = {
		   'home': myesp_home,
		   'switchback': myesp_switchback,
		   'onsite': myesp_onsite,
		   'passwd': myesp_passwd,
		   'passwdrecover': myesp_passrecover,
		   'recoveremail': myesp_passemailrecover,
		   'student': myesp_battlescreen_student,
		   'teacher': myesp_battlescreen_teacher,
		   'admin': myesp_battlescreen_admin,
		   'profile': edit_profile
		   }

