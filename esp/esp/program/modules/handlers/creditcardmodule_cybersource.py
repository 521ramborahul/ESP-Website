
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
from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl, meets_deadline
from esp.program.modules import module_ext
from esp.web.util        import render_to_response
from esp.money.models    import PaymentType, Transaction
from datetime            import datetime        
from esp.db.models       import Q
from esp.users.models    import User, ESPUser
#from esp.money.models    import RegisterLineItem, UnRegisterLineItem, PayForLineItems, LineItem, LineItemType
from esp.accounting_core.models import LineItemType, EmptyTransactionException
from esp.accounting_docs.models import Document

class CreditCardModule_Cybersource(ProgramModuleObj):
    def extensions(self):
        return [('creditCardInfo', module_ext.CreditCardModuleInfo)]

    def cost(self, espuser, anchor):
        return '%s.00' % str(self.creditCardInfo.base_cost)

    def isCompleted(self):
        return Transaction.objects.filter(anchor = self.program_anchor_cached(),
                                          fbo = self.user).count() > 0

    def students(self, QObject = False):
        # this should be fixed...this is the best I can do for now - Axiak
        # I think this is substantially better; it's the same thing, but in one query. - Adam
        #transactions = Transaction.objects.filter(anchor = self.program_anchor_cached())
        #userids = [ x.fbo_id for x in transactions ]
        QObj = Q(fbo__anchor=self.program_anchor_cached())

        if QObject:
            return {'creditcard': QObj}
        else:
            from esp.users.models import ESPUser
            
            return {'creditcard':User.objects.filter(QObj).distinct()}



    def studentDesc(self):
        return {'creditcard': """Students who have filled out the credit card form."""}
     
    @meets_deadline('/Payment')
    @usercheck_usetl
    def startpay_cybersource(self, request, tl, one, two, module, extra, prog):
        # Force users to pay for non-optional stuffs
        user = ESPUser(request.user)
        invoice = Document.get_invoice(user, prog.anchor, LineItemType.objects.filter(anchor=prog.anchor), dont_duplicate=True)

        context = {}
        context['module'] = self
        context['one'] = one
        context['two'] = two
        context['tl']  = tl
        context['user'] = user
        context['itemizedcosts'] = invoice.get_items()

        try:
            context['itemizedcosttotal'] = invoice.cost()
        except EmptyTransactionException:
            context['itemizedcosttotal'] = 0
            
        context['financial_aid'] = user.hasFinancialAid(prog.anchor)
        context['invoice'] = invoice
        
        return render_to_response(self.baseDir() + 'cardstart.html', request, (prog, tl), context)
