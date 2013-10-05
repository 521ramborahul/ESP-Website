__author__    = "Individual contributors (see AUTHORS file)"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "AGPL v.3"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2011 by the individual contributors
  (see AUTHORS file)

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

Contact information:
MIT Educational Studies Program
  84 Massachusetts Ave W20-467, Cambridge, MA 02139
  Phone: 617-253-4882
  Email: esp-webmasters@mit.edu
Learning Unlimited, Inc.
  527 Franklin St, Cambridge, MA 02139
  Phone: 617-379-0178
  Email: web-team@lists.learningu.org
"""

from esp.program.tests import ProgramFrameworkTest
from django.utils import simplejson as json
import time

class AJAXSchedulingModuleTestBase(ProgramFrameworkTest):
    def setUp(self, *args, **kwargs):
        from esp.program.modules.base import ProgramModule, ProgramModuleObj
        # Set up the program -- we want to be sure of these parameters
        kwargs.update({
            'num_rooms': 4,
            'num_timeslots': 4, 'timeslot_length': 50, 'timeslot_gap': 10,
            'num_teachers': 3, 'classes_per_teacher': 2, 'sections_per_class': 1
            })
        super(AJAXSchedulingModuleTestBase, self).setUp(*args, **kwargs)

        # Set the section durations to 1:50
        for sec in self.program.sections():
            sec.duration = '1.83'
            sec.save()

    def loginAdmin(self):
        """Log in an admin user."""
        self.failUnless(self.client.login(username=self.admins[0].username, password='password'), "Failed to log in admin user.")

    def emptySchedule(self):
        """Empty the schedule and teacher availability."""
        for s in self.program.sections():
            s.clearRooms()
            s.clear_meeting_times()
        for t in self.teachers:
            t.clearAvailableTimes(self.program)

    #schedule class, 
    #NO guarantee that it's a class that hasn't been scheduled yet
    #return a tuple (section, time, room)
    def scheduleClass(self, section=None, teacher=None, timeslots=None, rooms=None):
        if section == None:
            if teacher == None:
                teacher = self.teachers[0]
            section = teacher.getTaughtSections(self.program)[0]

        if rooms == None:
            rooms = self.rooms[0].identical_resources().filter(event__in=self.timeslots).order_by('event__start')

        if timeslots == None:
            timeslots = self.program.getTimeSlots().order_by('start')       

        ajax_url = '/manage/%s/' % self.program.getUrlBase() + 'ajax_schedule_class'     
        a1 = '\n'.join(['%s,%s' % (r.event.id, r.name) for r in rooms[0:2]])
        response = self.client.post(ajax_url, {'action': 'assignreg', 'cls': section.id, 'block_room_assignments': a1})
        self.failUnless(response.status_code == 200, "Class not successfully scheduled.")        
        return (section, timeslots, rooms)


class AJAXSchedulingModuleTest(AJAXSchedulingModuleTestBase):
    def testModelAPI(self):
        """Schedule classes using the on-model methods."""

        self.emptySchedule()

        # Fetch three consecutive vacancies in one room.
        rooms = self.rooms[0].identical_resources().filter(event__in=self.timeslots).order_by('event__start')
        self.failUnless(rooms.count() >= 3, "Not enough timeslots to run this test.")

        # Now we attempt to schedule the sections overlapping.
        s1, s2 = [t.getTaughtSections(self.program)[0] for t in self.teachers[:2]]

        # First, meeting times should be assigned without trouble.
        m1 = [rooms[0].event, rooms[1].event]
        m2 = [rooms[1].event, rooms[2].event]
        s1.assign_meeting_times(m1)
        s2.assign_meeting_times(m2)
        self.failUnless(set(s1.get_meeting_times()) == set(m1), "Failed to assign meeting times.")
        self.failUnless(set(s2.get_meeting_times()) == set(m2), "Failed to assign meeting times.")

        # Return values should be success on the first one and failure on the second.
        self.failUnless(s1.assign_room(rooms[0])[0] == True, "Received negative response when scheduling first class.")
        self.failUnless(set(s1.classrooms()) == set(rooms[:2]), "Failed to schedule first class.")
        self.failUnless(s2.assign_room(rooms[0])[0] == False, "Failed to detect conflict with first class.")

        # Check that the second attempt did not take.
        self.failUnless(set(s1.classrooms()) == set(rooms[:2]), "First class's schedule modified.")
        self.failUnless(not s2.classrooms().exists(), "Second class should not have any classrooms assigned.")

    def testForceAvailability(self):
        """Test the 'force_availability' view."""

        # force_availability is really a schedulingmodule view.
        # Either we should move this test to the scheduling module's tests,
        # or we should move this page to the AJAX scheduling module.
        # It was just too easy to include the test here meanwhile.

        self.emptySchedule()
        self.loginAdmin()

        # The setup:
        # Teacher 0 is teaching in the first two timeslots.
        # Teacher 1 is available the first two timeslots and has no classes scheduled.
        # Teacher 2 hasn't filled out their availability.

        # Set availability.
        timeslots = self.program.getTimeSlots().order_by('start')
        teachers = list(self.teachers)
        for t in teachers[:2]:
            t.addAvailableTime(self.program, timeslots[0])
            t.addAvailableTime(self.program, timeslots[1])
        # Schedule one class
        teachers[0].getTaughtSections(self.program)[0].assign_meeting_times(timeslots[:2])
        # Check the current state of availability.
        self.failUnless(all([
                set(teachers[0].getAvailableTimes(self.program, ignore_classes=True)) == set(timeslots[:2]),
                set(teachers[1].getAvailableTimes(self.program)) == set(timeslots[:2]),
                set(teachers[2].getAvailableTimes(self.program)) == set(),
                set(teachers[0].getAvailableTimes(self.program)) == set(),
            ]), "Unexpected availability state.")

        # Force availability
        self.client.post('/manage/%s/force_availability' % self.program.getUrlBase(), {'sure': 'True'})
        # Check the state of availability again
        self.failUnless(all([
                set(teachers[0].getAvailableTimes(self.program, ignore_classes=True)) == set(timeslots[:2]),
                set(teachers[1].getAvailableTimes(self.program)) == set(timeslots[:2]),
                set(teachers[2].getAvailableTimes(self.program)) == set(timeslots),
                set(teachers[0].getAvailableTimes(self.program)) == set(),
            ]), "Unexpected availability state.")

    def testWebAPI(self):
        """Schedule classes using the ajax_schedule_class view."""

        self.emptySchedule()
        self.loginAdmin()

        # Force teacher availability.
        self.client.post('/manage/%s/force_availability' % self.program.getUrlBase(), {'sure': 'True'})

        # Attempt to give a teacher a schedule conflict.
        t = self.teachers[0]

        # Fetch two consecutive vacancies in two different rooms
        rooms = self.rooms[0].identical_resources().filter(event__in=self.timeslots).order_by('event__start')
        self.failUnless(rooms.count() >= 2, "Not enough timeslots to run this test.")
        a1 = '\n'.join(['%s,%s' % (r.event.id, r.name) for r in rooms[0:2]])
        rooms = self.rooms.exclude(name=rooms[0].name)[0].identical_resources().filter(event__in=self.timeslots).order_by('event__start')
        self.failUnless(rooms.count() >= 2, "Not enough timeslots to run this test.")
        a2 = '\n'.join(['%s,%s' % (r.event.id, r.name) for r in rooms[0:2]])

        # Schedule one class.
        ajax_url = '/manage/%s/ajax_schedule_class' % self.program.getUrlBase()
        s1, s2 = t.getTaughtSections(self.program)[:2]
        timeslots = self.program.getTimeSlots().order_by('start')
        self.client.post(ajax_url, {'action': 'deletereg', 'cls': s1.id})
        self.client.post(ajax_url, {'action': 'assignreg', 'cls': s1.id, 'block_room_assignments': a1})
        self.failUnless(set(s1.get_meeting_times()) == set(timeslots[0:2]), "Failed to assign meeting times.")
        # Try to schedule the other class.
        self.client.post(ajax_url, {'action': 'deletereg', 'cls': s2.id})
        self.client.post(ajax_url, {'action': 'assignreg', 'cls': s2.id, 'block_room_assignments': a2})
        self.failUnless(set(s1.get_meeting_times()) == set(timeslots[0:2]), "Existing meeting times clobbered.")
        self.failUnless(set(s2.get_meeting_times()) == set(), "Failed to prevent teacher conflict.")
    
    def testChangeLog(self):
        self.emptySchedule()
        self.loginAdmin()
        self.client.post('/manage/%s/force_availability' % self.program.getUrlBase(), {'sure': 'True'})

        ajax_url_base = '/manage/%s/' % self.program.getUrlBase()
        changelog_url = ajax_url_base + 'ajax_change_log'
        
        beforeSchedule = time.time()

        # Schedule one class.
        self.scheduleClass()

        #fetch the changelog
        changelog_response = self.client.get(changelog_url, {'last_fetched_time': beforeSchedule })
        self.failUnless(changelog_response.status_code == 200, "Changelog not successfully retreieved")
        changelog = json.loads(changelog_response.content)["changelog"]
        self.failUnless(len(changelog) == 1, "Change log does not contain exactly one class.")
        
        #change log should truncate at last requested time
        afterSchedule = time.time()
        changelog_response = self.client.get(changelog_url, {'last_fetched_time': afterSchedule })
        changelog = json.loads(changelog_response.content)["changelog"]
        self.failUnless(len(changelog) == 0, "Change log contained content from before last_fetched_time")

        #unschedule a class
        self.client.post(ajax_url, {'action': 'deletereg', 'cls': s1.id})
        #change log should include unscheduled classes 
        changelog_response = self.client.get(changelog_url, {'last_fetched_time': afterSchedule })
        changelog = json.loads(changelog_response.content)["changelog"]
        self.failUnless(len(changelog) == 1, "Change log did not contain the unscheduled class.")
        
        #change log should not include failed scheduling of classes
