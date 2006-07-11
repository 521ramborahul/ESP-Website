from django.db import models
from django.contrib.auth.models import User
from esp.calendar.models import Event
from esp.datatree.models import DataTree, GetNode
from esp.users.models import UserBit

# Create your models here.

class Program(models.Model):
    """ An ESP Program, such as HSSP Summer 2006, Splash Fall 2006, Delve 2005, etc. """
    anchor = models.ForeignKey(DataTree) # Series containing all events in the program, probably including an event that spans the full duration of the program, to represent this program

    def __str__(self):
        return str(self.anchor.parent.friendly_name) + ' ' + str(self.anchor.friendly_name)

    def parent(self):
	    return anchor.parent

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

    class Admin:
        pass

class EquipmentType(models.Model):
    """ A type of equipment that is available for classes to use

    Equipment types include projectors, classrooms with desks, Athena labs, and the like """
    equipment = models.TextField() # Human-readable name of the element of equipment
    numAvailable = models.IntegerField() # Number of this item of equipment owned by ESP

    def __str__(self):
        return str(equipment)

    class Admin:
        pass

# FIXME: The Class object should use the permissions system to control
# which grades (Q/Community/6_12/*) are permitted to join the class, though
# the UI should make it as clean as two numbers, at least initially.
class Claus(models.Model):
	""" A Class, as taught as part of an ESP program """
	anchor = models.ForeignKey(DataTree)
	parent_program = models.ForeignKey(Program)
	# title drawn from anchor.friendly_name
	title = models.TextField()
	# class number drawn from anchor.name
	category = models.ForeignKey(ClassCategories)
	# teachers are drawn from permissions table
	class_info = models.TextField()
	equipment_needed = models.ManyToManyField(EquipmentType, blank=True, null=True)
	message_for_directors = models.TextField()
	grade_min = models.IntegerField()
	grade_max = models.IntegerField()
	class_size_min = models.IntegerField()
	class_size_max = models.IntegerField()
	schedule = models.TextField()
	enrollment = models.IntegerField()

	def __str__(self):
		return str(self.title)

	def teachers(self):
		v = GetNode( 'V/Administer/Program/Class' )
		return [ x.user for x in UserBit.bits_get_users( self.anchor, v ) ]

	class Admin:
		pass
	
	class InvalidClassProposal(Exception):
		cause = ""
		def __init__(self, new_cause):
			cause = new_cause
	
	@staticmethod
	def create_via_proposal(proposal):

class TeacherBio(models.Model):
	""" A biography of an ESP teacher """
	pass
