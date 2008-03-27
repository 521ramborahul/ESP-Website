
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
from esp.program.modules.base    import ProgramModuleObj, needs_teacher, meets_deadline
from esp.program.modules         import module_ext
from esp.program.models          import Program
from esp.datatree.models         import DataTree, GetNode
from esp.web.util                import render_to_response
from django                      import newforms as forms
from esp.cal.models              import Event
from django.core.cache           import cache
from esp.db.models               import Q
from esp.users.models            import User, ESPUser
from esp.resources.models        import ResourceType, Resource
from datetime                    import timedelta

class AvailabilityModule(ProgramModuleObj):
    """ This program module allows teachers to indicate their availability for the program. """

    def prepare(self, context={}):
        """ prepare returns the context for the main availability page. 
            Everything else can be gotten from hooks in this module. """
        if context is None: context = {}
        
        context['availabilitymodule'] = self 
        return context

    def isCompleted(self):
        """ Make sure that they have indicated sufficient availability for all classes they have signed up to teach. """
        self.user = ESPUser(self.user)
        available_slots = self.user.getAvailableTimes(self.program)
        
        total_time = self.user.getTaughtTime(self.program, include_scheduled=False)
        available_time = timedelta()
        for a in available_slots:
            available_time = available_time + a.duration()
        
        if (total_time > available_time):
            return False
        else:
            return True

    def teachers(self, QObject = False):
        """ Returns a list of teachers who have indicated at least one segment of teaching availability for this program. """
        
        if QObject is True:
            return {'availability': self.getQForUser(Q(resource__event__anchor = self.program_anchor_cached()))}
        
        teacher_list = Resource.objects.filter(event__anchor=self.program_anchor_cached()).values('user').distinct()
        
        return {'availability': [t['user'] for t in teacher_list]}

    def teacherDesc(self):
        return {'availability': """Teachers who have indicated their scheduled availability for the program."""}

    def deadline_met(self):
        if self.user.isAdmin(self.program):
            return True
        
        tmpModule = ProgramModuleObj()
        tmpModule.__dict__ = self.__dict__
        return tmpModule.deadline_met()
    
    def getTimes(self):
        #   Get a list of tuples with the id and name of each of the program's timeslots
        times = self.program.getTimeSlots()
        return [(str(t.id), t.short_description) for t in times]

    def availability(self, request, tl, one, two, module, extra, prog):
        #   Renders the teacher availability page and handles submissions of said page.
        
        teacher = ESPUser(request.user)
        time_options = self.program.getTimeSlots()
        #   Group contiguous blocks
        time_groups = Event.group_contiguous(list(time_options))
                
        if request.method == 'POST':
            #   Process form
            post_vars = request.POST
            
            #   Reset teacher's availability
            teacher.clearAvailableTimes(self.program)
            
            #   Add in resources for the checked available times.
            for ts_id in post_vars.getlist('timeslots'):
                    ts = Event.objects.filter(id=int(ts_id))
                    if len(ts) != 1:
                        raise ESPError('Found %d matching events for input %s' % (len(ts), key))
                    
                    teacher.addAvailableTime(self.program, ts[0])
                    
            return self.goToCore(tl)
                
        else:
            #   Show new form
            available_slots = teacher.getAvailableTimes(self.program)
            if len(available_slots) == 0:
                #   If they didn't enter anything, make everything checked by default.
                available_slots = self.program.getTimeSlots()
                
            context = {'groups': [{'selections': [{'checked': (t in available_slots), 'slot': t} for t in group]} for group in time_groups]}
            context['prog'] = self.program
            
            return render_to_response(self.baseDir()+'availability_form.html', request, (prog, tl), context)
