

from django import newforms as forms
from django.contrib.auth.models import User

__all__ = ['PasswordResetForm','NewPasswordSetForm']

class PasswordResetForm(forms.Form):

    email     = forms.EmailField(max_length=64, required=False,
                                 help_text="(e.g. johndoe@example.org)")

    username  = forms.CharField(max_length=64, required=False,
                                help_text = '(Case sensitive)')


    def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
        "Helper function for outputting HTML. Used by as_table(), as_ul(), as_p()."
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []
        first = True
        for name, field in self.fields.items():
            if not first:
                output.append(error_row % '<span class="or">- or -</span>')
            else:
                first = False
            bf = forms.forms.BoundField(self, field, name)
            bf_errors = forms.forms.ErrorList([forms.forms.escape(error) for error in bf.errors]) # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend(['(Hidden field %s) %s' % (name, e) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                if errors_on_separate_row and bf_errors:
                    output.append(error_row % bf_errors)
                if bf.label:
                    label = forms.forms.escape(bf.label)
                    # Only add a colon if the label does not end in punctuation.
                    if label[-1] not in ':?.!':
                        label += ':'
                    label = bf.label_tag(label) or ''
                else:
                    label = ''
                if field.help_text:
                    help_text = help_text_html % field.help_text
                else:
                    help_text = u''
                output.append(normal_row % {'errors': bf_errors, 'label': label, 'field': unicode(bf), 'help_text': help_text})
        if top_errors:
            output.insert(0, error_row % top_errors)
        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and insert the hidden fields.
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else: # If there aren't any rows in the output, just append the hidden fields.
                output.append(str_hidden)
        return u'\n'.join(output)


    def clean_username(self):

        if self.clean_data.get('username','').strip() == '' and \
           self.clean_data.get('email','').strip() == '':
            raise forms.ValidationError("You need to specify something.")

        if self.clean_data['username'].strip() == '': return ''

        try:
            user = User.objects.get(username=self.clean_data['username'])
        except User.DoesNotExist:
            raise forms.ValidationError, "User '%s' does not exist." % self.clean_data['username']

        return self.clean_data['username'].strip()

    def clean_email(self):
        if self.clean_data['email'].strip() == '':
            return ''

        if len(User.objects.filter(email__iexact=self.clean_data['email']).values('id')[:1])>0:
            return self.clean_data['email'].strip()

        raise forms.ValidationError('No user has email %s' % self.clean_data['email'])


class NewPasswordSetForm(forms.Form):

    code     = forms.CharField(widget = forms.HiddenInput())
    username = forms.CharField(max_length=128,
                               help_text='(The one you used to receive the email.)')
    password = forms.CharField(max_length=128, min_length=5,widget=forms.PasswordInput())
    password_confirm = forms.CharField(max_length = 128,widget=forms.PasswordInput(),
                                       label='Password Confirmation')

    def clean_username(self):
        try:
            user = User.objects.get(username = self.clean_data['username'].strip(),
                                    password = self.clean_data['code'])
        except User.DoesNotExist:
            raise forms.ValidationError('Invalid username.')

        return self.clean_data['username'].strip()
    

    def clean_password_confirm(self):
        new_passwd= self.clean_data['password_confirm'].strip()

        if self.clean_data['password'] != new_passwd:
            raise forms.ValidationError('Password and confirmation are not equal.')
        return new_passwd
