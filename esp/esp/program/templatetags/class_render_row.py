from django import template
from django.conf import settings

from argcache import wildcard
from esp.utils.cache_inclusion_tag import cache_inclusion_tag
from esp.program.models import ClassSubject, ClassSection
from esp.tagdict.models import Tag

register = template.Library()


@cache_inclusion_tag(register, 'inclusion/program/class_teacher_list_row.html')
def render_class_teacher_list_row(klass):
    return {'cls': klass,
            'program': klass.parent_program,
            'crmi': klass.parent_program.getModuleExtension('ClassRegModuleInfo'),
            'friendly_times_with_date': (Tag.getProgramTag(key='friendly_times_with_date', program=klass.parent_program, default=False) == "True"),
            'email_host': settings.EMAIL_HOST
            }
render_class_teacher_list_row.cached_function.depend_on_row(ClassSubject, lambda cls: {'klass': cls})
render_class_teacher_list_row.cached_function.depend_on_row(ClassSection, lambda sec: {'klass': sec.parent_class})
render_class_teacher_list_row.cached_function.depend_on_cache(ClassSubject.get_teachers, lambda self=wildcard, **kwargs: {'klass': self})


@cache_inclusion_tag(register, 'inclusion/program/class_copy_row.html')
def render_class_copy_row(klass):
    return {'cls': klass,
            'program': klass.parent_program,
            'crmi': klass.parent_program.getModuleExtension('ClassRegModuleInfo')}
render_class_teacher_list_row.cached_function.depend_on_row(ClassSubject, lambda cls: {'klass': cls})
render_class_teacher_list_row.cached_function.depend_on_row(ClassSection, lambda sec: {'klass': sec.parent_class})
render_class_copy_row.cached_function.depend_on_cache(ClassSubject.get_teachers, lambda self=wildcard, **kwargs: {'klass': self})
