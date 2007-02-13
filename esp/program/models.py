from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from esp.cal.models import Event
from esp.datatree.models import DataTree, GetNode
from esp.users.models import UserBit, ContactInfo, StudentInfo, TeacherInfo, EducatorInfo, GuardianInfo
from esp.lib.markdown import markdown
from esp.qsd.models import QuasiStaticData
from esp.lib.EmptyQuerySet import EMPTY_QUERYSET
from datetime import datetime
from django.core.cache import cache
from esp.miniblog.models import Entry

# Create your models here.
class ProgramModule(models.Model):
	""" Program Modules for a Program """
	link_title = models.CharField(maxlength=64, blank=True, null=True)
	admin_title = models.CharField(maxlength=128)
	main_call  = models.CharField(maxlength=32)
	check_call = models.CharField(maxlength=32, blank=True, null=True)
	module_type = models.CharField(maxlength=32)
	handler    = models.CharField(maxlength=32)
	seq = models.IntegerField()
	aux_calls = models.CharField(maxlength=512, blank=True, null=True)
	required = models.BooleanField()
	
	def __str__(self):
		return 'Program Module "%s"' % self.admin_title

	class Admin:
		pass
	
class ArchiveClass(models.Model):
	""" Old classes throughout the years """
	program = models.CharField(maxlength=256)
	year = models.IntegerField()
	date = models.CharField(maxlength=128)
	category = models.CharField(maxlength=16)
	teacher = models.CharField(maxlength=1024)
	title = models.CharField(maxlength=1024)
	description = models.TextField()

	def __str__(self):
		return '"%s" taught by "%s"' % (self.title, self.teacher)
	
	def heading(self):
		return ({'label': 'Teacher', 'value': self.teacher},
			{'label': 'Year', 'value': self.year},
			{'label': 'Program', 'value': self.program},
			{'label': 'Category', 'value': self.category})
	
	def content(self):
		return self.description

	
class Program(models.Model):
	""" An ESP Program, such as HSSP Summer 2006, Splash Fall 2006, Delve 2005, etc. """
	anchor = models.ForeignKey(DataTree) # Series containing all events in the program, probably including an event that spans the full duration of the program, to represent this program
	grade_min = models.IntegerField()
	grade_max = models.IntegerField()
	director_email = models.CharField(maxlength=64)
	class_size_min = models.IntegerField()
	class_size_max = models.IntegerField()
	program_modules = models.ManyToManyField(ProgramModule)


	def url(self):
		str_array = self.anchor.tree_encode()
		return '/'.join(str_array[2:])
	
	def __str__(self):
		return str(self.anchor.parent.friendly_name) + ' ' + str(self.anchor.friendly_name)

	def parent(self):
		return anchor.parent

	def niceName(self):
		return str(self).replace("_", " ")

	def getUrlBase(self):
		""" gets the base url of this class """
		tmpnode = self.anchor
		urllist = []
		while tmpnode.name != 'Programs':
			urllist.insert(0,tmpnode.name)
			tmpnode = tmpnode.parent
		return "/".join(urllist)
					  

	def teacherSubscribe(self, user):
		v = GetNode('V/Subscribe')
		qsc = self.anchor.tree_create(['Announcements',
					       'Teachers'])
		
		if UserBit.objects.filter(user = user,
					  qsc = qsc,
					  verb = v).count() > 0:
			return False

		ub, created = UserBit.objects.get_or_create(user = user,
							    qsc = qsc,
							    verb = v)
		return True

	
	def teachers(self, QObjects = False):
		modules = self.getModules(None, 'teach')
		teachers = {}
		for module in modules:
			tmpteachers = module.teachers(QObjects)
			if tmpteachers is not None:
				teachers.update(tmpteachers)
		return teachers

	def students(self, QObjects=False):
		modules = self.getModules(None, 'learn')
		students = {}
		for module in modules:
			tmpstudents = module.students(QObjects)
			if tmpstudents is not None:
				students.update(tmpstudents)
		return students

	def getLists(self, QObjects=False):
		lists = self.students(QObjects)
		lists.update(self.teachers(QObjects))
		learnmodules = self.getModules(None, 'learn')
		teachmodules = self.getModules(None, 'teach')

		
		for k, v in lists.items():
			lists[k] = {'list': v}

		desc  = {}
		for module in learnmodules:
			tmpdict = module.studentDesc()
			if tmpdict is not None:
				desc.update(tmpdict)
		for module in teachmodules:
			tmpdict = module.teacherDesc()
			if tmpdict is not None:
				desc.update(tmpdict)

		for k, v in desc.items():
			lists[k]['description'] = v
		from esp.users.models import ESPUser
		usertypes = ['Student', 'Teacher', 'Guardian', 'Educator']

		for usertype in usertypes:
			lists['all_'+usertype.lower()+'s'] = {'description':
							       usertype+'s in all of ESP',
							       'list' : ESPUser.getAllOfType(usertype)}
			
		return lists

	def students_union(self, QObject = False):
		import operator
		if len(self.students().values()) == 0:
			return []
		
		union = reduce(operator.or_, [x for x in self.students(True).values() ])
		if QObject:
			return union
		else:
			return User.objects.filter(union).distinct()


	def teachers_union(self, QObject = False):
		import operator
		if len(self.teachers().values()) == 0:
			return []
		union = reduce(operator.or_, [x for x in self.teachers(True).values() ])
		if QObject:
			return union
		else:
			return User.objects.filter(union).distinct()	

	def num_students(self):
		modules = self.getModules(None, 'learn')
		students = {}
		for module in modules:
			tmpstudents = module.students()
			if tmpstudents is not None:
				for k, v in tmpstudents.items():
					if type(v) == list:
						students[k] = len(v)
					else:
						students[k] = v.count()
		return students

	def classes_node(self):
		return DataTree.objects.filter(parent = self.anchor, name = 'Classes')[0]

	def getTimeSlots(self):
		return list(self.anchor.tree_create(['Templates','TimeSlots']).children().order_by('id'))

	def isConfirmed(self, espuser):
		v = GetNode('V/Flags/Public')
		userbits = UserBit.objects.filter(verb = v, user = espuser,
						 qsc = self.anchor.tree_create(['Confirmation']))
		if len(userbits) < 1:
			return False

		return True
	
	def getClassRooms(self):
		return list(self.anchor.tree_create(['Templates','Classrooms']).children().order_by('name'))

	def addClassRoom(self, roomname, shortname):
		room = DataTree()
		room.parent = self.anchor.tree_create(['Templates','Classrooms'])
		room.name = shortname
		room.friendly_name = roomname
		room.save()

	def classes(self):
		return Class.objects.filter(parent_program = self)		

	def getResources(self):
		return list(self.anchor.tree_create(['Templates','Resources']).children())

	def getModules(self, user = None, tl = None):
		""" Gets a list of modules for this program. """
		from esp.program.modules import base

		def cmpModules(mod1, mod2):
			""" comparator function for two modules """
			return mod1.seq - mod2.seq
		if tl:
			modules =  [ base.ProgramModuleObj.getFromProgModule(self, module)
				     for module in self.program_modules.all()
				     if module.module_type == tl]
		else:
			modules =  [ base.ProgramModuleObj.getFromProgModule(self, module)
				     for module in self.program_modules.all()]
			
		modules.sort(cmpModules)
		
		if user:
			for module in modules:
				module.setUser(user)
		return modules
		
	class Admin:
		pass
	
	@staticmethod
	def find_by_perms(user, verb):
		""" Fetch a list of relevant programs for a given user and verb """
		return UserBit.find_by_anchor_perms(Program,user,verb)



class ClassCategories(models.Model):
	""" A list of all possible categories for an ESP class

	Categories include 'Mathematics', 'Science', 'Zocial Zciences', etc.
	"""
	category = models.TextField()

	def __str__(self):
		return str(self.category)
		
		
	@staticmethod
	def category_string(letter):
		
		results = ClassCategories.objects.filter(category__startswith = letter)
		
		if results.count() == 1:
			return results[0].category
		else:
			return None

	class Admin:
		pass


# FIXME: The Class object should use the permissions system to control
# which grades (Q/Community/6_12/*) are permitted to join the class, though
# the UI should make it as clean as two numbers, at least initially.
class Class(models.Model):
	""" A Class, as taught as part of an ESP program """
	anchor = models.ForeignKey(DataTree)
	parent_program = models.ForeignKey(Program)
	# title drawn from anchor.friendly_name
	# class number drawn from anchor.name
	category = models.ForeignKey(ClassCategories)
	# teachers are drawn from permissions table
	class_info = models.TextField(blank=True)
	message_for_directors = models.TextField(blank=True)
	grade_min = models.IntegerField()
	grade_max = models.IntegerField()
	class_size_min = models.IntegerField()
	class_size_max = models.IntegerField()
	schedule = models.TextField(blank=True)
	directors_notes = models.TextField(blank=True, null=True)
	duration = models.FloatField(blank=True, null=True, max_digits=5, decimal_places=2)
	event_template = models.ForeignKey(DataTree, related_name='class_event_template_set', null=True)
	meeting_times = models.ManyToManyField(DataTree, related_name='meeting_times', null=True)
	viable_times = models.ManyToManyField(DataTree, related_name='class_viable_set', blank=True)
	resources = models.ManyToManyField(DataTree, related_name='class_resources', blank=True)
	#	We think this is useless because the sign-up is completely based on userbits.
	enrollment = models.IntegerField()

	def classroomassignments(self):
		return ClassRoomAssignment.objects.filter(cls = self)

	def classrooms(self):
		assignments = ClassRoomAssignment.objects.filter(cls = self)
		rooms = {}
		if assignments.count() == 0:
			return []
		
		for assignment in assignments:
			rooms[assignment.room.id] = assignment.room

		return rooms.values()

	def prettyrooms(self):
		return [ x.friendly_name  for x in self.classrooms() ]

	def clearRooms(self):
		for x in ClassRoomAssignment.objects.filter(cls = self):
			x.delete()		

	def assignClassRoom(self, classroom):
		self.clearRooms()

		for time in self.meeting_times.all():
			roomassignment = ClassRoomAssignment()
			roomassignment.cls = self
			roomassignment.timeslot = time
			roomassignment.room = classroom
			roomassignment.save()
		return True
		

	def emailcode(self):
		return self.category.category[0].upper()+str(self.id)

	def url(self):
		str_array = self.anchor.tree_encode()
		return '/'.join(str_array[2:])

	def got_qsd(self):
				return (QuasiStaticData.objects.filter(path = self.anchor).count() > 0)

	def PopulateEvents(self):
		""" Given this instance's event_template, generate a series of events that define this class's schedule """
		for e in self.event_template.event_set.all():
			newevent = Event()
			newevent.start = e.start
			newevent.end = e.end
			newevent.short_description = e.short_description
			newevent.description = e.description.replace('[event]', e.anchor.friendly_name) # Allow for the insertion of event names, so that the templates are less generic/nonspecific
			newevent.event_type = e.event_type
			newevent.anchor = self.anchor
			newevent.save()
		
	def __str__(self):
		if self.title() is not None:
			return self.title()
		else:
			return ""

	def delete(self, adminoverride = False):
		if self.num_students() > 0 and not adminoverride:
			return False

		teachers = self.teachers()
		for teacher in self.teachers():
			self.removeTeacher(teacher)
			self.removeAdmin(teacher)


		if self.anchor.id:
			self.anchor.delete()
		
		self.viable_times.clear()
		self.meeting_times.clear()
		super(Class, self).delete()
		
		
	def title(self):
		cache_id = 'ClassTitle:'+str(self.id)
		retVal = cache.get(cache_id)
		if retVal is not None:
			return retVal
		retVal = self.anchor.friendly_name
		cache.set(cache_id, retVal, 99999)
		return retVal
	
	def teachers(self):
		from esp.users.models import ESPUser
		v = GetNode( 'V/Flags/Registration/Teacher' )
		userbits = [ x.user.id for x in UserBit.bits_get_users( self.anchor, v) ]
		if len(userbits) > 0:
			teachers = list(User.objects.filter(id__in=userbits).distinct())
			return map(ESPUser, teachers)
		else:
			return EMPTY_QUERYSET.distinct()
		#return [ x.user for x in UserBit.bits_get_users( self.anchor, v ) ]



	def cannotAdd(self, user):
		""" Go through and give an error message if this user cannot add this class to their schedule. """
		if not user.isStudent():
			return 'You are not a student!'
		
		if not self.isAccepted():
			return 'This class is not accepted.'

		if self.isFull():
			return 'Class is full!'

		# student has no classes...no conflict there.
		if user.getEnrolledClasses().count() == 0:
			return False

		if user.isEnrolledInClass(self):
			return 'You are already signed up for this class!'
		
		# check to see if there's a conflict:
		for cls in user.getEnrolledClasses().filter(parent_program = self.parent_program):
			for time in cls.meeting_times.all():
				if self.meeting_times.filter(id = time.id).count() > 0:
					return 'Conflicts with your schedule!'

		# this use *can* add this class!
		return False

		
	def makeTeacher(self, user):
		v = GetNode('V/Flags/Registration/Teacher')
		if UserBit.objects.filter(user = user,
					  qsc = self.anchor,
					  verb = v).count() > 0:
			return True
		
		ub, created = UserBit.objects.get_or_create(user = user,
							    qsc = self.anchor,
							    verb = v)
		ub.save()
		return True

	def removeTeacher(self, user):
		v = GetNode('V/Flags/Registration/Teacher')
		for userbit in UserBit.objects.filter(user = user,
						      qsc = self.anchor,
						      verb = v):
			userbit.delete()


		return True

	def subscribe(self, user):
		v = GetNode('V/Subscribe')
		if UserBit.objects.filter(user = user,
					  qsc = self.anchor,
					  verb = v).count() > 0:
			return False

		ub, created = UserBit.objects.get_or_create(user = user,
							    qsc = self.anchor,
							    verb = v)


		return True
	
	def makeAdmin(self, user, endtime = None):
		v = GetNode('V/Administer/Edit')
		if UserBit.objects.filter(user = user,
					  qsc = self.anchor,
					  verb = v).count() > 0:
			return True

		ub, created = UserBit.objects.get_or_create(user = user,
							    qsc = self.anchor,
							    verb = v)


		return True		


	def removeAdmin(self, user):
		v = GetNode('V/Administer/Edit')
		for userbit in UserBit.objects.filter(user = user,
						      qsc = self.anchor,
						      verb = v):
			userbit.delete()

		return True

	def conflicts(self, teacher):
		from esp.users.models import ESPUser
		user = ESPUser(teacher)
		if user.getTaughtClasses().count() == 0:
			return False
		
		for cls in user.getTaughtClasses().filter(parent_program = self.parent_program):
			for time in cls.meeting_times.all():
				if self.meeting_times.filter(id = time.id).count() > 0:
					return True

	def students(self):
		from esp.users.models import ESPUser
		v = GetNode( 'V/Flags/Registration/Preliminary' )
		return [ ESPUser(x.user) for x in UserBit.bits_get_users( self.anchor, v ) ]

	@staticmethod
	def idcmp(one, other):
		return cmp(one.id, other.id)
	
	def __cmp__(self, other):
		selfevent = self.firstBlockEvent()
		otherevent = other.firstBlockEvent()

		if selfevent is not None and otherevent is None:
			return 1
		if selfevent is None and otherevent is not None:
			return -1

		if selfevent is not None and otherevent is not None:
			cmpresult = selfevent.__cmp__(otherevent)
			if cmpresult != 0:
				return cmpresult

		return cmp(self.title(), other.title())

		


	def firstBlockEvent(self):
		eventList = []
		for timeanchor in self.meeting_times.all():
			events = Event.objects.filter(anchor=timeanchor)
			if len(events) == 1:
				eventList.append(events[0])
		if len(eventList) == 0:
			return None
		eventList.sort()
		return eventList[0]


	def num_students(self):
		v = GetNode( 'V/Flags/Registration/Preliminary' )
		if not self.anchor.id:
			return 0
		return UserBit.bits_get_users(self.anchor, v).count()

	def isFull(self):
		if self.num_students() >= self.class_size_max:
			return True
		else:
			return False
	
	def getTeacherNames(self):
		return [ usr.first_name + ' ' + usr.last_name
			for usr in self.teachers() ]

	def friendly_times(self):
		""" will return friendly times for the class """
		txtTimes = []
		eventList = []
		for timeanchor in self.meeting_times.all():
			events = Event.objects.filter(anchor=timeanchor)
			if len(events) != 1:
				txtTimes.append(timeanchor.friendly_name)
			else:
				eventList.append(events[0])

		txtTimes += [ event.pretty_time() for event
			      in Event.collapse(eventList) ]

		return txtTimes
			



	def preregister_student(self, user):
		prereg_verb = GetNode( 'V/Flags/Registration/Preliminary' )
		
		#	First, delete preregistration bits for other classes at the same time.
		other_bits = UserBit.objects.filter(user=user, verb=prereg_verb)
		for b in other_bits:
			class_qset = Class.objects.filter(anchor=b.qsc, event_template = self.event_template)
			if class_qset.count() > 0:
				b.delete()
				
		if not self.isFull():
			#	Then, create the userbit denoting preregistration for this class.
			prereg = UserBit()
			prereg.user = user
			prereg.qsc = self.anchor
			prereg.verb = prereg_verb
			prereg.save()
			return True
		else:
			#	Pre-registration failed because the class is full.
			return False

	def pageExists(self):
		from esp.qsd.models import QuasiStaticData
		return self.anchor.quasistaticdata_set.filter(name='learn:index').count() > 0

	def isAccepted(self):
		return UserBit.UserHasPerms(None, self.anchor, GetNode('V/Flags/Class/Approved'))

	def isReviewed(self):
		return not UserBit.UserHasPerms(None, self.anchor, GetNode('V/Flags/Class/Proposed'))

	
	def prettyDuration(self):
		if self.duration is None:
			return 'N/A'

		return '%s:%02d' % \
		       (int(self.duration),
			int((self.duration - int(self.duration)) * 60))

	def accept(self, user=None):
		""" mark this class as accepted """
		self.review()
		if self.isAccepted():
			return False # already accepted
			
		u = UserBit()
		u.user = None
		u.qsc = self.anchor
		u.verb = GetNode('V/Flags/Class/Approved')
		u.save()

		subject = 'Your %s class was approved!' % (self.parent_program.niceName())
		
		content =  """Congratulations, your class,
%s,
was approved! Please go to http://esp.mit.edu/teach/%s/class_status/%s to view your class' status.

-esp.mit.edu Autogenerated Message""" % \
				  (self.title(), self.parent_program.getUrlBase(), self.id)
		if user is None:
			user = AnonymousUser()
		Entry.post(user, self.anchor.tree_create(['TeacherEmail']), subject, content, True)
		
		return True

	def review(self):
		"""Mark this class as no-longer just `proposed' """
		userbitList = UserBit.objects.filter(user = None,
						     qsc = self.anchor,
						     verb = GetNode('V/Flags/Class/Proposed'))

		for userbit in userbitList:
			userbit.delete()

		return True
	
		

	def propose(self):
		""" Mark this class as just `proposed' """

		self.reject()
		
		proposeVerb = GetNode('V/Flags/Class/Proposed')
		
		userbitList = UserBit.objects.filter(user = None,
						     qsc = self.anchor,
						     verb = proposeVerb)
		if len(userbitList) > 0:
			return False

		u = UserBit()
		u.user = None
		u.qsc = self.anchor
		u.verb = proposeVerb
		u.save()

	def reject(self):
		""" Mark this class as rejected """
		
		self.review()
		userbitlst = UserBit.objects.filter(user = None,
						    qsc  = self.anchor,
						    verb = GetNode('V/Flags/Class/Approved'))
		if len(userbitlst) > 0:
			for userbit in userbitlst:
				userbit.delete()
			return True
		return False

			
	def getUrlBase(self):
		""" gets the base url of this class """
		tmpnode = self.anchor
		urllist = []
		while tmpnode.name != 'Programs':
			urllist.insert(0,tmpnode.name)
			tmpnode = tmpnode.parent
		return "/".join(urllist)
							   
	class Admin:
		pass
	
class ResourceRequest(models.Model):
	""" An indication of resources requested for a particular class """
	requestor = models.OneToOneField(Class)
	wants_projector = models.BooleanField()
	wants_computer_lab = models.BooleanField()
	wants_open_space = models.BooleanField()

	def __str__(self):
		return 'Resource request for ' + str(self.requestor)

	class Admin:
		pass



class ClassRoomAssignment(models.Model):
	""" This associates a class, with a room, with a timeblock
	    This will prevent problems with classes that have to move """
	room     = models.ForeignKey(DataTree, related_name="room")
	timeslot = models.ForeignKey(DataTree, related_name="timeslot")
	unique_together = (('room','timeslot'),)
	
	cls      = models.ForeignKey(Class)
	


class BusSchedule(models.Model):
	""" A scheduled bus journey associated with a program """
	program = models.ForeignKey(Program)
	src_dst = models.CharField(maxlength=128)
	departs = models.DateTimeField()
	arrives = models.DateTimeField()

	class Admin:
		pass


	
class TeacherParticipationProfile(models.Model):
	""" Profile properties associated with a teacher in a program """
	teacher = models.ForeignKey(User)
	program = models.ForeignKey(Program)
	unique_together = (('teacher', 'program'),)
	bus_schedule = models.ManyToManyField(BusSchedule)
	can_help = models.BooleanField()

	def __str__(self):
		return 'Profile for ' + str(self.teacher) + ' in ' + str(self.program)

	class Admin:
		pass
	

class SATPrepRegInfo(models.Model):
	""" SATPrep Registration Info """
	old_math_score = models.IntegerField(blank=True, null=True)
	old_verb_score = models.IntegerField(blank=True, null=True)
	old_writ_score = models.IntegerField(blank=True, null=True)
	diag_math_score = models.IntegerField(blank=True, null=True)
	diag_verb_score = models.IntegerField(blank=True, null=True)
	diag_writ_score = models.IntegerField(blank=True, null=True)	
	heard_by = models.CharField(maxlength=128, blank=True, null=True)
	user = models.ForeignKey(User)
	program = models.ForeignKey(Program)

	def __str__(self):
		return 'SATPrep regisration info for ' +str(self.user) + ' in '+str(self.program)
	def updateForm(self, new_data):
		for i in self.__dict__.keys():
			if i != 'user_id' and i != 'id' and i != 'program_id':
				new_data[i] = self.__dict__[i]
		return new_data

	
        def addOrUpdate(self, new_data, curUser, program):
		for i in self.__dict__.keys():
			if i != 'user_id' and i != 'id' and i != 'program_id' and new_data.has_key(i):
				self.__dict__[i] = new_data[i]
#		self.user = curUser
#		self.program = program
		self.save()

	@staticmethod
	def getLastForProgram(user, program):
		satPrepList = SATPrepRegInfo.objects.filter(user=user,program=program).order_by('-id')
		if len(satPrepList) < 1:
			satPrep = SATPrepRegInfo()
			satPrep.user = user
			satPrep.program = program
		else:
			satPrep = satPrepList[0]
		return satPrep
	class Admin:
		pass

class TeacherBio(models.Model):
	""" A biography of an ESP teacher """
	user = models.ForeignKey(User)
	content = models.TextField()

	def __str__(self):
		return self.user.first_name + ' ' + self.user.last_name + ', a Biography'
	
	def html(self):
		return markdown(self.content)
	
	class Admin:
		pass

class RegistrationProfile(models.Model):
	""" A student registration form """
	user = models.ForeignKey(User)
	program = models.ForeignKey(Program)
	contact_user = models.ForeignKey(ContactInfo, blank=True, null=True, related_name='as_user')
	contact_guardian = models.ForeignKey(ContactInfo, blank=True, null=True, related_name='as_guardian')
	contact_emergency = models.ForeignKey(ContactInfo, blank=True, null=True, related_name='as_emergency')
	student_info = models.ForeignKey(StudentInfo, blank=True, null=True, related_name='as_student')
	teacher_info = models.ForeignKey(TeacherInfo, blank=True, null=True, related_name='as_teacher')
	guardian_info = models.ForeignKey(GuardianInfo, blank=True, null=True, related_name='as_guardian')
	educator_info = models.ForeignKey(EducatorInfo, blank=True, null=True, related_name='as_educator')
	last_ts = models.DateTimeField(default=datetime.now())	

	@staticmethod
	def getLastProfile(user):
		regProfList = RegistrationProfile.objects.filter(user__exact=user).order_by('-last_ts','-id')
		if len(regProfList) < 1:
			regProf = RegistrationProfile()
			regProf.user = user
		else:
			regProf = regProfList[0]
		return regProf

	def save(self):
		""" update the timestamp """
		self.last_ts = datetime.now()
		super(RegistrationProfile, self).save()
		
	@staticmethod
	def getLastForProgram(user, program):
		regProfList = RegistrationProfile.objects.filter(user__exact=user,program__exact=program).order_by('-last_ts','-id')
		if len(regProfList) < 1:
			regProf = RegistrationProfile()
			regProf.user = user
			regProf.program = program
		else:
			regProf = regProfList[0]
		return regProf
			
	def __str__(self):
		if self.program is None:
			return '<Registration for '+str(self.user)+'>'
		if self.user is not None:
			return '<Registration for ' + str(self.user) + ' in ' + str(self.program) + '>'


	def updateForm(self, form_data, specificInfo = None):
		if self.student_info is not None and (specificInfo is None or specificInfo == 'student'):
			form_data = self.student_info.updateForm(form_data)
		if self.teacher_info is not None and (specificInfo is None or specificInfo == 'teacher'):
			form_data = self.teacher_info.updateForm(form_data)
		if self.guardian_info is not None and (specificInfo is None or specificInfo == 'guardian'):
			form_data = self.guardian_info.updateForm(form_data)
		if self.educator_info is not None and (specificInfo is None or specificInfo == 'educator'):
			form_data = self.educator_info.updateForm(form_data)
		if self.contact_user is not None:
			form_data = self.contact_user.updateForm(form_data)
		if self.contact_guardian is not None:
			form_data = self.contact_guardian.updateForm(form_data, 'guard_')
		if self.contact_emergency is not None:
			form_data = self.contact_emergency.updateForm(form_data, 'emerg_')
		return form_data
	
	def preregistered_classes(self):
		v = GetNode( 'V/Flags/Registration/Preliminary' )
		return UserBit.find_by_anchor_perms(Class, self.user, v, self.program.anchor.tree_decode(['Classes']))
	
	def registered_classes(self):
		v = GetNode( 'V/Flags/Registration/Confirmed' )
		return UserBit.find_by_anchor_perms(Class, self.user, v, self.program.anchor.tree_decode(['Classes']))

	class Admin:
		pass

