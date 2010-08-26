from django.contrib import admin
from django import forms
from django.db import models
from esp.users.models.userbits import UserBit, UserBitImplication
from esp.users.models import UserAvailability, ContactInfo, StudentInfo, TeacherInfo, GuardianInfo, EducatorInfo, ZipCode, ZipCodeSearches, K12School


class UserBitAdmin(admin.ModelAdmin):
    search_fields = ['user__last_name','user__first_name',
                     'qsc__uri','verb__uri']
admin.site.register(UserBit, UserBitAdmin)


class UserBitImplicationAdmin(admin.ModelAdmin):
    exclude = ('created_bits',)

admin.site.register(UserBitImplication, UserBitImplicationAdmin)

admin.site.register(TeacherInfo)
admin.site.register(GuardianInfo)
admin.site.register(EducatorInfo)
admin.site.register(ZipCode)
admin.site.register(ZipCodeSearches)
admin.site.register(UserAvailability)

class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'e_mail', 'phone_day', 'address_postal']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'e_mail']
admin.site.register(ContactInfo, ContactInfoAdmin)

class StudentInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'graduation_year', 'k12school', 'school']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
admin.site.register(StudentInfo, StudentInfoAdmin)

class K12SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'grades', 'contact_title', 'contact_name', 'school_type']
    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput(attrs={'size':'50',}),},
    }

    def contact_name(self, obj):
        return "%s %s" % (obj.contact.first_name, obj.contact.last_name)
    contact_name.short_description = 'Contact name'

admin.site.register(K12School, K12SchoolAdmin)
