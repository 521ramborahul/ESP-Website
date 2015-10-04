
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
  Email: web-team@learningu.org
"""
import time

from esp.dbmail.models import MessageRequest, send_mail, TextOfEmail
from datetime import datetime, timedelta
from django.db.models.query import Q
from django.db import transaction
from django.template.loader import render_to_string

from django.conf import settings


_ONE_WEEK = timedelta(weeks=1)


@transaction.autocommit
def process_messages(debug=False):
    """Go through all unprocessed messages and process them.
    
    Callers (e.g. dbmail_cron.py) should ensure that this function is not
    called in more than one thread simultaneously."""
    
    now = datetime.now()
    one_week_ago = now - _ONE_WEEK

    # Choose a set of messages to process.  Anything which arrives later will
    # not be processed by this run of the script. Any outstanding requests
    # which were created over one week ago are assumed to be out-of-date, and
    # are ignored.
    messages = MessageRequest.objects.filter(Q(processed_by__lte=now) |
                                             Q(processed_by__isnull=True),
                                             created_at__gte=one_week_ago,
                                             processed=False,
    )
    messages = list(messages)

    #   Process message requests
    for message in messages:
        # If we raise an error here, transaction management will make sure that
        # things with the MessageRequest get backed out properly.  We let the
        # whole script just exit in this case -- this way we get an error
        # message via cron, and the next run of the script can just try again.
        message.process(debug=debug)
    return messages

@transaction.autocommit
def send_email_requests(debug=False):
    """Go through all email requests that aren't sent and send them.
    
    Callers (e.g. dbmail_cron.py) should ensure that this function is not
    called in more than one thread simultaneously."""

    now = datetime.now()
    one_week_ago = now - _ONE_WEEK

    retries = getattr(settings, 'EMAILRETRIES', None)
    if retries is None:
        # previous code thought that settings.EMAILRETRIES might be set to None
        # to be the default, rather than being undefined, so we keep that
        # behavior.
        retries = 2 # i.e. 3 tries total

    # Choose a set of emails to process.  Anything which arrives later will
    # not be processed by this run of the script. Any outstanding requests
    # which were created over one week ago are assumed to be out-of-date, and
    # are ignored.
    mailtxts = TextOfEmail.objects.filter(Q(sent_by__lte=now) |
                                          Q(sent_by__isnull=True),
                                          created_at__gte=one_week_ago,
                                          sent__isnull=True,
                                          tries__lte=retries)
    mailtxts_list = list(mailtxts)

    wait = getattr(settings, 'EMAILTIMEOUT', None)
    if wait is None:
        wait = 1.5
    
    num_sent = 0
    errors = [] # if any messages failed to deliver

    for mailtxt in mailtxts_list:
        exception = mailtxt.send(debug=debug)
        if exception is not None:
            errors.append({'email': mailtxt, 'exception': str(exception)})
            if debug: print "Encountered error while sending to " + str(mailtxt.send_to) + ": " + str(e)
        else:
            num_sent += 1

        time.sleep(wait)

    if debug and num_sent > 0:
        print 'Sent %d messages' % num_sent

    #   Report any errors
    if errors:
        recipients = [mailtxt.send_from]

        if 'bounces' in settings.DEFAULT_EMAIL_ADDRESSES:
            recipients.append(settings.DEFAULT_EMAIL_ADDRESSES['bounces'])

        mail_context = {'errors': errors}
        delivery_failed_string = render_to_string('email/delivery_failed', mail_context)
        if debug:
            print 'Mail delivery failure'
            print delivery_failed_string
        send_mail('Mail delivery failure', delivery_failed_string, settings.SERVER_EMAIL, recipients)
    elif num_sent > 0:
        if debug: print 'No mail delivery failures'
