from django.db import models
from django.template import loader, Context
from django.core.mail import send_mail

# Create your models here.

class VolunteerRegistration(models.Model):
    your_name = models.CharField(max_length=100)
    email_address = models.EmailField()
    phone_number = models.CharField(max_length=32, help_text='Cell phone numbers are preferred.')
    availability = models.CharField(max_length=255, help_text='What times are you available to help out on October 3rd?')
    notes = models.TextField(blank=True, default='', help_text='What are you interested in helping with?  Have you talked to anyone already?')

class ResponseForm(models.Model):
    contact_name = models.CharField(max_length = 100)
    position = models.CharField(max_length = 100)
    email = models.EmailField()
    school = models.CharField(max_length = 150)
    mailing_address = models.TextField()
    xeroxable_flier_for_summer_hssp = models.BooleanField()
    xeroxable_flier_for_junction = models.BooleanField()
    catalog_of_all_2007_to_2008_esp_courses = models.BooleanField()
    xeroxable_fliers_for_all_2008_to_2009_esp_courses = models.BooleanField()
    splash_on_wheels_application = models.FileField(upload_to="uploaded/sow_apps/%y/", blank=True, null=True)
    bulk_financial_aid_application = models.FileField(upload_to="uploaded/bulk_finaid_form/%y/", blank=True, null=True)

    def __unicode__(self):
        return 'Survey Response: %s (%s)' % (self.school, self.contact_name)

    def send_mail(self):
        text = loader.get_template("shortterm/school_response/email.txt").render(Context({'form': self}))
        send_mail('Survey Response: %s' % self.school,  text, self.email, ["esp@mit.edu"])

    class Admin:
        pass

