from django.contrib import admin
from esp.admin import admin_site
from django import forms
from django.db import models
from esp.users.models.userbits import UserBit, UserBitImplication
from esp.users.models.forwarder import UserForwarder
from esp.users.models import UserAvailability, ContactInfo, StudentInfo, TeacherInfo, GuardianInfo, EducatorInfo, ZipCode, ZipCodeSearches, K12School, ESPUser, Record, Permission, GradeChangeRequest
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from esp.utils.admin_user_search import default_search_fields
import datetime

admin_site.register(UserForwarder)

admin_site.register(ZipCode)
admin_site.register(ZipCodeSearches)

#def default_search_fields(user_param='user'):
#    """Returns a list containing all the default ways we like to be able to search a user by."""
#    return [i % user_param for i in ['%s__username', '%s__first_name', '%s__last_name', '=%s__email']]

class UserAvailabilityAdmin(admin.ModelAdmin):
    def parent_program(obj): #because 'event__program' for some reason doesn't want to work...
        return obj.event.program
    list_display = ['id', 'user', 'event', parent_program]
    list_filter = ['event__program', ]
    search_fields = default_search_fields()
    ordering = ['-event__program', 'user__username', 'event__start']
admin_site.register(UserAvailability, UserAvailabilityAdmin)

class ESPUserAdmin(UserAdmin):
    #remove the user_permissions and is_superuser from adminpage
    #(since we don't use either of those)
    #See https://github.com/django/django/blob/stable/1.3.x/django/contrib/auth/admin.py

    from django.utils.translation import ugettext, ugettext_lazy as _
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('User Roles'), {'fields': ('groups',)}),
        )

admin_site.register(ESPUser, ESPUserAdmin)

class RecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'program', 'time',]
    list_filter = ['event', 'program', 'time']
    search_fields = default_search_fields()
    date_hierarchy = 'time'
admin_site.register(Record, RecordAdmin)

class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'permission_type','program','start_date','end_date']
    search_fields = default_search_fields() + ['permission_type', 'program__url']
    list_filter = ['permission_type', 'program']
    actions = [ 'expire', 'renew' ]

    def expire(self, request, queryset):
        rows_updated = queryset.update(end_date=datetime.datetime.now())
        if rows_updated == 1:
            message_bit = "1 permission was"
        else:
            message_bit = "%s permissions were" % rows_updated
        self.message_user(request, "%s successfully expired." % message_bit)
    expire.short_description = "Expire permissions"

    def renew(self, request, queryset):
        rows_updated = queryset.update(end_date=None)
        if rows_updated == 1:
            message_bit = "1 permission was"
        else:
            message_bit = "%s permissions were" % rows_updated
        self.message_user(request, "%s successfully expired." % message_bit)
    renew.short_description = "Renew permissions"

admin_site.register(Permission, PermissionAdmin)

class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'e_mail', 'phone_day', 'address_postal']
    search_fields = default_search_fields() + ['e_mail']
admin_site.register(ContactInfo, ContactInfoAdmin)

class UserInfoAdmin(admin.ModelAdmin):
    search_fields = default_search_fields()

class StudentInfoAdmin(UserInfoAdmin):
    list_display = ['id', 'user', 'graduation_year', 'k12school', 'school']
    list_filter = ['graduation_year']
    search_fields = default_search_fields()
admin_site.register(StudentInfo, StudentInfoAdmin)

class TeacherInfoAdmin(UserInfoAdmin):
    list_display = ['id', 'user', 'graduation_year', 'from_here', 'college']
    search_fields = default_search_fields()
admin_site.register(TeacherInfo, TeacherInfoAdmin)

class GuardianInfoAdmin(UserInfoAdmin):
    list_display = ['id', 'user', 'year_finished', 'num_kids']
    search_fields = default_search_fields()
admin_site.register(GuardianInfo, GuardianInfoAdmin)

class EducatorInfoAdmin(UserInfoAdmin):
    search_fields=default_search_fields()
    list_display = ['id', 'user', 'position', 'k12school', 'school']
admin_site.register(EducatorInfo, EducatorInfoAdmin)


class K12SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'grades', 'contact_title', 'contact_name', 'school_type']
    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput(attrs={'size':'50',}),},
    }

    def contact_name(self, obj):
        return "%s %s" % (obj.contact.first_name, obj.contact.last_name)
    contact_name.short_description = 'Contact name'

admin_site.register(K12School, K12SchoolAdmin)


class GradeChangeRequestAdmin(admin.ModelAdmin):
    list_display = ['requesting_student', 'claimed_grade', 'approved','acknowledged_by','acknowledged_time', 'created']
    readonly_fields = ['requesting_student','acknowledged_by','acknowledged_time','claimed_grade']
    search_fields = default_search_fields('requesting_student')
    list_filter = ('created','approved',)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'acknowledged_by', None) is None:
            obj.acknowledged_by = request.user
        obj.save()

admin_site.register(GradeChangeRequest, GradeChangeRequestAdmin)

#   Include admin pages for Django group
admin_site.register(Group, GroupAdmin)

