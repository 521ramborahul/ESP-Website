
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
from django.http     import HttpResponseRedirect
from esp.users.views import search_for_user
from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl, needs_onsite
from esp.program.modules.handlers.programprintables import ProgramPrintables
from esp.users.models import ESPUser, UserBit
from esp.datatree.models import GetNode
from datetime         import datetime, timedelta
class OnsiteClassSchedule(ProgramModuleObj):


    @needs_student
    def printschedule(self, request, *args, **kwargs):
        verb  = request.get_node('V/Publish/Print')
        qsc   = self.program.anchor.tree_create(['Schedule'])

        if len(UserBit.objects.filter(user=self.user,
                                  verb=verb,
                                  qsc=qsc).exclude(enddate__lte=datetime.now())[:1]) == 0:

            newbit = UserBit.objects.create(user=self.user, verb=verb,
                             qsc=qsc, recursive=False, enddate=datetime.now() + timedelta(days=1))

        return HttpResponseRedirect('/learn/%s/studentreg' % self.program.getUrlBase())

    @needs_student
    def studentschedule(self, request, *args, **kwargs):
        #   tl, one, two, module, extra, prog
        request.GET = {'op':'usersearch',
                       'userid': str(self.user.id) }

        module = [module for module in self.program.getModules('manage')
                  if type(module) == ProgramPrintables        ][0]

        module.user = self.user
        module.program = self.program
        
        kwargs = {'tl': args[0], 'one': args[1], 'two': args[2], 'module': args[3], 'extra': 'onsite', 'prog': args[5]}
        return module.studentschedules(request, **kwargs)

        
    @needs_onsite
    def schedule_students(self, request, tl, one, two, module, extra, prog):
        """ Display a teacher eg page """

        user, found = search_for_user(request, ESPUser.getAllOfType('Student', False))
        if not found:
            return user
        
        self.user.switch_to_user(request,
                                 user,
                                 self.getCoreURL(tl),
                                 'OnSite Registration!',
                                 True)

        return HttpResponseRedirect('/learn/%s/studentreg' % self.program.getUrlBase())

