
__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2010 MIT ESP

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

from esp.program.modules.base import ProgramModuleObj, CoreModule
from esp.web.util        import render_to_response
from esp.program.modules.forms.volunteer import VolunteerOfferForm
from esp.users.models import ESPUser, AnonymousUser

class VolunteerSignup(ProgramModuleObj, CoreModule):
    @classmethod
    def module_properties(cls):
        return {
            "admin_title": "Volunteer Sign-up Module",
            "link_title": "Sign Up to Volunteer",
            "module_type": "volunteer",
            "seq": 0,
            "main_call": "signup",
            "aux_calls": "view",
            }

    def signup(self, request, tl, one, two, module, extra, prog):
        context = {}
        
        if request.method == 'POST':
            form = VolunteerOfferForm(request.POST, program=prog)
            if form.is_valid():
                offers = form.save()
                context['complete'] = True
                context['complete_name'] = offers[0].name
                context['complete_email'] = offers[0].email
                context['complete_phone'] = offers[0].phone
                form = VolunteerOfferForm(program=prog)
        else:
            form = VolunteerOfferForm(program=prog)
            
        #   Pre-fill information if possible
        if hasattr(self.user, 'email'):
            form.load(self.user)
        
        context['form'] = form
        
        return render_to_response('program/modules/volunteersignup/signup.html', request, (prog, tl), context)