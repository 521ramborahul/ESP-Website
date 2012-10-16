
__author__    = "Individual contributors (see AUTHORS file)"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "AGPL v.3"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 by the individual contributors
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
from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl, meets_deadline, main_call, aux_call
from esp.datatree.models import *
from esp.program.modules import module_ext
from esp.web.util        import render_to_response
from esp.middleware      import ESPError
from esp.users.models    import ESPUser, UserBit, User
from django.db.models.query       import Q
from django.shortcuts import redirect
from esp.middleware.threadlocalrequest import get_current_request

# hackish solution for Splash 2012
class FormstackMedliabModule(ProgramModuleObj):
    """ Module for collecting medical information online via Formstack """

    reg_verb = GetNode('V/Flags/Registration/FormstackMedliabDone')

    @classmethod
    def module_properties(cls):
        return {
            "admin_title": "Formstack Med-liab Module",
            "link_title": "Medical and Emergency Contact Information",
            "module_type": "learn",
            "seq": 3,
            "required": True
            }

    def isCompleted(self):
        return UserBit.valid_objects().filter(user=get_current_request().user,
                                              qsc=self.program.anchor,
                                              verb=self.reg_verb).exists()

    @main_call
    @needs_student
    @meets_deadline('/FormstackMedliab')
    def medliab(self, request, tl, one, two, module, extra, prog):
        """
        Landing page redirecting to med-liab form on Formstack.
        """
        # code for Junction admissions will have better handling of
        # Formstack forms
        # for now, just render a QSD page
        context = {}
        return render_to_response(self.baseDir()+'medliab.html',
                                  request, (prog, tl), context)

    @aux_call
    @needs_student
    def medicalpostback581309742(self, request, tl, one, two, module, extra, prog):
        """
        Marks student off as completed.
        """
        UserBit.objects.create(user=request.user,
                               qsc=self.program.anchor,
                               verb=self.reg_verb)
        return self.goToCore(tl)

    class Meta:
        abstract = True

