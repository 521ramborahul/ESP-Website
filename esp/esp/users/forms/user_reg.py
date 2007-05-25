
from django import newforms as forms
from django.contrib.auth.models import User

role_choices = (
    ('Student', 'ESP Student (in K-12th grade)'),
    ('Teacher', 'ESP Teacher (MIT or non-MIT affilated)'),
    ('Guardian', 'Guardian of ESP student'),
    ('Educator', 'K-12 Educator'),
    )

class UserRegForm(forms.Form):
    """
    A form for users to register for the ESP web site.
    """
    first_name = forms.CharField(max_length=30)
    last_name  = forms.CharField(max_length=30)

    username = forms.CharField(help_text="At least 5 characters, must contain only alphanumeric characters.",
                               min_length=5, max_length=30)


    password = forms.CharField(widget = forms.PasswordInput(),
                               min_length=5)

    confirm_password = forms.CharField(widget = forms.PasswordInput(),
                                       min_length=5)

    initial_role = forms.ChoiceField(choices = role_choices)

    email = forms.EmailField(help_text = "Please provide a valid email address. We won't spam you.",max_length=30)


    def clean_username(self):
        errors = []
        bad_list = ':!@#$%^&*(){}[]<>?,./\|~`+=- '

        data = self.clean_data['username']

        if len(set(bad_list) & set(data)) > 0:
            raise forms.ValidationError('Username contains invalid characters.')

        if User.objects.filter(username__iexact = data).count() > 0:
            raise forms.ValidationError('Username already in use.')

        data = data.strip()
        return data

    def clean_confirm_password(self):
        if self.clean_data['confirm_password'] != self.clean_data['password']:
            raise forms.ValidationError('Ensure the password and password confirmation are equal.')
        return self.clean_data['confirm_password']



class EmailUserForm(forms.Form):


    email = forms.EmailField(help_text = '(e.g. johndoe@domain.xyz)')
