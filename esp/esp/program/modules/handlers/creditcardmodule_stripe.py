
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
from esp.program.modules import module_ext
from esp.datatree.models import *
from esp.web.util import render_to_response
from esp.dbmail.models import send_mail
from esp.users.models import ESPUser
from esp.accounting.controllers import ProgramAccountingController, IndividualAccountingController
from esp.middleware import ESPError
from esp.middleware.threadlocalrequest import get_current_request

from django.conf import settings
from django.db.models.query import Q
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from decimal import Decimal
from datetime import datetime
import stripe
import re

class CreditCardModule_Stripe(ProgramModuleObj, module_ext.StripeCreditCardSettings):
    @classmethod
    def module_properties(cls):
        return {
            "admin_title": "Credit Card Payment Module (Stripe)",
            "link_title": "Credit Card Payment",
            "module_type": "learn",
            "seq": 10000,
            }

    def isCompleted(self):
        """ Whether the user has paid for this program or its parent program. """
        return IndividualAccountingController(self.program, get_current_request().user).has_paid()
    have_paid = isCompleted

    def students(self, QObject = False):
        #   This query represented students who have a payment transfer from the outside
        pac = ProgramAccountingController(self.program)
        QObj = Q(transfer__source__isnull=True, transfer__line_item=pac.default_payments_lineitemtype())

        if QObject:
            return {'creditcard': QObj}
        else:
            return {'creditcard':ESPUser.objects.filter(QObj).distinct()}

    def studentDesc(self):
        return {'creditcard': """Students who have filled out the credit card form."""}

    def check_setup(self):
        """ Validate the keys specified in the StripeCreditCardSettings object.
            If something is wrong, provide an error message which will hopefully
            only be seen by admins during setup. """

        #   A Stripe account comes with 4 keys, starting with e.g. sk_test_
        #   and followed by a 24 character base64-encoded string.
        valid_pk_re = r'pk_(test|live)_([A-Za-z0-9+/=]){24}'
        valid_sk_re = r'sk_(test|live)_([A-Za-z0-9+/=]){24}'
        config_url = '/admin/modules/stripecreditcardsettings/%d' % self.extension_id
        if not re.match(valid_pk_re, self.publishable_key) or not re.match(valid_sk_re, self.secret_key):
            raise ESPError('The site has not yet been properly set up for credit card payments.  Administrators should <a href="%s">configure payments here</a>.' % config_url, True)

    @main_call
    @usercheck_usetl
    @meets_deadline('/Payment')
    def payonline(self, request, tl, one, two, module, extra, prog):

        #   Check for setup of module.
        self.check_setup()

        user = ESPUser(request.user)

        iac = IndividualAccountingController(self.program, request.user)
        context = {}
        context['module'] = self
        context['program'] = prog
        context['user'] = user
        context['invoice_id'] = iac.get_id()
        context['identifier'] = iac.get_identifier()
        payment_type = iac.default_payments_lineitemtype()
        sibling_type = iac.default_siblingdiscount_lineitemtype()
        grant_type = iac.default_finaid_lineitemtype()
        context['itemizedcosts'] = iac.get_transfers().exclude(line_item__in=[payment_type, sibling_type, grant_type]).order_by('-line_item__required')
        context['itemizedcosttotal'] = iac.amount_due()
        context['totalcost_cents'] = int(context['itemizedcosttotal'] * 100)
        context['subtotal'] = iac.amount_requested()
        context['financial_aid'] = iac.amount_finaid()
        context['sibling_discount'] = iac.amount_siblingdiscount()
        context['amount_paid'] = iac.amount_paid()

        if 'HTTP_HOST' in request.META:
            context['hostname'] = request.META['HTTP_HOST']
        else:
            context['hostname'] = Site.objects.get_current().domain
        context['institution'] = settings.INSTITUTION_NAME
        context['support_email'] = settings.DEFAULT_EMAIL_ADDRESSES['support']
        
        return render_to_response(self.baseDir() + 'cardpay.html', request, context)

    def send_error_email(self, request, context):
        """ Send an e-mail to admins explaining the credit card error.
            (Broken out from charge_payment view for readability.) """

        context['request'] = request
        context['program'] = self.program
        context['postdata'] = request.POST.copy()
        domain_name = Site.objects.get_current().domain
        msg_content = render_to_string(self.baseDir() + 'error_email.txt', context)
        msg_subject = '[ ESP CC ] Credit card error on %s: %d %s' % (domain_name, request.user.id, request.user.name())
        send_mail(msg_subject, msg_content, settings.SERVER_EMAIL, [settings.DEFAULT_EMAIL_ADDRESSES['support'], self.program.getDirectorConfidentialEmail(), ])

    @aux_call
    def charge_payment(self, request, tl, one, two, module, extra, prog):
        context = {'postdata': request.POST.copy()}

        iac = IndividualAccountingController(self.program, request.user)

        #   Set Stripe key based on settings.  Also require the API version
        #   which our code is designed for.
        stripe.api_key = self.secret_key
        stripe.api_version = '2014-03-13'

        if request.POST.get('ponumber', '') != iac.get_id():
            #   If we received a payment for the wrong PO:
            #   This is not a Python exception, but an error nonetheless.
            context['error_type'] = 'inconsistent_po'
            context['error_info'] = {'request_po': request.POST.get('ponumber', ''), 'user_po': iac.get_id()}
        else:
            try:
                #   Create the charge on Stripe's servers - this will charge the user's card
                charge = stripe.Charge.create(
                    amount=int(request.POST['totalcost_cents']),
                    currency="usd",
                    card=request.POST['stripeToken'],
                    description="Payment for %s - %s" % (prog.niceName(), request.user.name()),
                    metadata={
                        'ponumber': request.POST['ponumber'],
                        'donation': request.POST['donation'],
                    },
                )
            except stripe.error.CardError, e:
                context['error_type'] = 'declined'
                context['error_info'] = e.json_body['error']
            except stripe.error.InvalidRequestError, e:
                #   While this is a generic error meaning invalid parameters were supplied
                #   to Stripe's API, we will usually see it because of a duplicate request.
                context['error_type'] = 'invalid'
            except stripe.error.AuthenticationError, e:
                context['error_type'] = 'auth'
            except stripe.error.APIConnectionError, e:
                context['error_type'] = 'api'
            except stripe.error.StripeError, e:
                context['error_type'] = 'generic'

        if 'error_type' in context:
            #   If we got any sort of error, send an e-mail to the admins and render an error page.
            self.send_error_email(request, context)
            return render_to_response(self.baseDir() + 'failure.html', request, context)

        #   We have a successful charge.  Save a record of it if we can uniquely identify the user/program.
        totalcost_dollars = float(request.POST['totalcost_cents']) / 100.0
        iac.submit_payment(totalcost_dollars, request.POST['stripeToken'])

        #   Render the success page, which doesn't do much except direct back to studentreg.
        context['amount_paid'] = totalcost_dollars
        return render_to_response(self.baseDir() + 'success.html', request, context)

    class Meta:
        abstract = True

