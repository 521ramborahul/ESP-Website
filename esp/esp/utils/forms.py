
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
import re

from django import forms
from django.core.validators import EMPTY_VALUES
from django.forms.forms import Form, Field, BoundField
from django.forms import ValidationError
from django.forms.util import ErrorList
from django.utils.html import escape, mark_safe
from django.utils.encoding import smart_text
from django.template import loader
from django.core.mail import send_mail

from esp.tagdict.models import Tag
from esp.utils.widgets import DummyWidget

class UKPhoneNumberField(forms.CharField):
    """
    A form field that validates input as a U.S. phone number.
    """
    phone_digits_re = re.compile(r'^0(\d{10})$')
    default_error_messages = {
        'invalid': 'Phone numbers must be in valid format.',
    }
    def clean(self, value):
        super(UKPhoneNumberField, self).clean(value)
        if value in EMPTY_VALUES:
            return ''
        number = re.sub('([^0-9]+)', '', smart_text(value))
        m = self.phone_digits_re.search(number)
        if m:
            return value
        raise ValidationError(self.error_messages['invalid'])

class EmailModelForm(forms.ModelForm):
    """ An extension of Django's ModelForms that e-mails when
        an instance of the model is saved using the form.
        Requires from_addr (string) and destination_addrs (list of strings)
        to be provided as arguments to save().
    """
    def __init__(self, *args, **kwargs):
        super(EmailModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.itervalues():
            if field.required:
                field.widget.attrs['class'] = 'required'
    
    def save(self, from_addr='', destination_addrs=[]):
        result = super(EmailModelForm, self).save()
        self.email(from_addr, destination_addrs)
        return result
        
    def email(self, from_addr, destination_addrs):
        context = {}
        context['instance_name'] = self.instance.__class__.__name__
        context['fields'] = []
        for field in self.fields:
            context['fields'].append({'name': field, 'data': self.data[field]})
        msg_text = loader.render_to_string("email/autoform.txt", context)
        send_mail('Automatic E-mail Form Submission (type: %s)' % context['instance_name'], msg_text, from_addr, destination_addrs)


class SizedCharField(forms.CharField):
    """ Just like CharField, but you can set the width of the text widget. """
    def __init__(self, length=None, *args, **kwargs):
        forms.CharField.__init__(self, *args, **kwargs)
        self.widget.attrs['size'] = length

class StrippedCharField(SizedCharField):
    def clean(self, value):
        return super(StrippedCharField, self).clean(self.to_python(value).strip())

#### NOTE: Python super() does weird things (it's the next in the MRO, not a superclass).
#### DO NOT OMIT IT if overriding __init__() when subclassing these forms

class FormWithRequiredCss(forms.Form):
    """ Form that adds the "required" class to every required widget, to restore oldforms behavior. """
    def __init__(self, *args, **kwargs):
        super(FormWithRequiredCss, self).__init__(*args, **kwargs)
        for field in self.fields.itervalues():
            if field.required:
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' required'
                else:
                    field.widget.attrs['class'] = 'required'

class FormWithTagInitialValues(forms.Form):
    def __init__(self, *args, **kwargs):

        #   Get tag data in the form of a dictionary:
        #     field name -> tag to look up for initial value
        if 'tag_map' in kwargs:
            tag_map = kwargs['tag_map']
            tag_defaults = {}
            for field_name in tag_map:
                #   Check for existence of tag
                tag_data = Tag.getTag(tag_map[field_name])
                #   Use tag data as initial value if the tag was found
                if tag_data:
                    tag_defaults[field_name] = tag_data
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            #   Apply defaults to form quietly (don't override provided values)
            for key in tag_defaults:
                if key not in kwargs['initial']:
                    kwargs['initial'][key] = tag_defaults[key]
            #   Remove the tag_map so as not to confuse other functions
            del kwargs['tag_map']

        super(FormWithTagInitialValues, self).__init__(*args, **kwargs)

class FormUnrestrictedOtherUser(FormWithRequiredCss):
    """ Form that implements makeRequired for the old form --- disables required fields at in some cases. """

    def __init__(self, user=None, *args, **kwargs):
        super(FormUnrestrictedOtherUser, self).__init__(*args, **kwargs)
        self.user = user
        if user is None or not (hasattr(user, 'other_user') and user.other_user):
            pass
        else:
            for field in self.fields.itervalues():
                if field.required:
                    field.required = False
                    field.widget.attrs['class'] = None # GAH!

class DummyField(forms.Field):
    widget = DummyWidget
    def __init__(self, *args, **kwargs):
        super(DummyField, self).__init__(*args, **kwargs)
        #   Set a flag that can be checked in Python code or template rendering
        #   to alter behavior
        #   self.is_dummy_field = True

    def is_dummy_field(self):
        return True
