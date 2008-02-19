from django import template
from esp.web.util.template import cache_inclusion_tag
    
register = template.Library()

def cache_key_func(cls, user=None, prereg_url=None, filter=False, request=None):
   if not user or not prereg_url:
        return 'CLASS_DISPLAY__%s' % cls.id

   return None

def core_cache_key_func(cls):
    return 'CLASS_CORE_DISPLAY__%s' % cls.id

def minimal_cache_key_func(cls, user=None, prereg_url=None, filter=False, request=None):
    if not user or not prereg_url:
        return 'CLASS_MINDISPLAY__%s' % cls.id

    return None

def current_cache_key_func(cls, user=None, prereg_url=None, filter=False, request=None):
    if not user or not prereg_url:
        return 'CLASS_CURRENT__%s' % cls.id

    return None

@cache_inclusion_tag(register, 'inclusion/program/class_catalog_core.html', cache_key_func=core_cache_key_func)
def render_class_core(cls):
    return {'class': cls,
            'isfull': cls.num_students() >= cls.class_size_max}

@cache_inclusion_tag(register, 'inclusion/program/class_catalog.html', cache_key_func=cache_key_func)
def render_class(cls, user=None, prereg_url=None, filter=False, request=None):
    errormsg = None

    if user and prereg_url:
        errormsg = cls.cannotAdd(user, True, request=request)

    show_class =  (not filter) or (not errormsg)
    
    
    return {'class':      cls,
            'user':       user,
            'prereg_url': prereg_url,
            'errormsg':   errormsg,
            'show_class': show_class}

# We're not caching this yet because I doubt people will hit this function the same way repeatedly--same user and all.
# The lambda is there because cache_inclusion_tag doesn't like receiving cache_key_func=None. -ageng 2008-02-18
@cache_inclusion_tag(register, 'inclusion/program/class_catalog_swap.html', cache_key_func=lambda a, b, c, d, e, f: None)
def render_class_swap(cls, swap_class, user=None, prereg_url=None, filter=False, request=None):
    errormsg = None

    if user and prereg_url:
        errormsg = cls.cannotAdd(user, True, request=request)
        if errormsg == 'Conflicts with your schedule!':
            errormsg = None
            for currentclass in user.getEnrolledClasses(cls.parent_program, request).exclude(id=swap_class.id):
                for time in currentclass.meeting_times.all():
                    if cls.meeting_times.filter(id = time.id).count() > 0:
                        errormsg = 'Conflicts with your schedule!'
    
    if cls.id == swap_class.id:
        errormsg = '(You are currently registered for this class.)'
    
    show_class =  (not filter) or (not errormsg)
    
    
    return {'class':      cls,
            'user':       user,
            'prereg_url': prereg_url,
            'errormsg':   errormsg,
            'show_class': show_class}

@cache_inclusion_tag(register, 'inclusion/program/class_catalog_minimal.html', cache_key_func=minimal_cache_key_func)
def render_class_minimal(cls, user=None, prereg_url=None, filter=False, request=None):
    errormsg = None

    if user and prereg_url:
        errormsg = cls.cannotAdd(user, True, request=request)

    show_class =  (not filter) or (not errormsg)
    
    
    return {'class':      cls,
            'user':       user,
            'prereg_url': prereg_url,
            'errormsg':   errormsg,
            'show_class': show_class}
            
@cache_inclusion_tag(register, 'inclusion/program/class_catalog_current.html', cache_key_func=current_cache_key_func)
def render_class_current(cls, user=None, prereg_url=None, filter=False, request=None):
    errormsg = None

    if user and prereg_url:
        errormsg = cls.cannotAdd(user, True, request=request)

    show_class =  (not filter) or (not errormsg)

    return {'class':      cls,
            'show_class': show_class}
                        
            
@cache_inclusion_tag(register, 'inclusion/program/class_catalog_preview.html', cache_key_func=minimal_cache_key_func)
def render_class_preview(cls, user=None, prereg_url=None, filter=False, request=None):
    errormsg = None

    if user and prereg_url:
        errormsg = cls.cannotAdd(user, True, request=request)

    show_class =  (not filter) or (not errormsg)
    
    
    return {'class':      cls,
            'user':       user,
            'prereg_url': prereg_url,
            'errormsg':   errormsg,
            'show_class': show_class}

@cache_inclusion_tag(register, 'inclusion/program/class_catalog_row.html', cache_key_func=minimal_cache_key_func)
def render_class_row(cls, user=None, prereg_url=None, filter=False, request=None):
    errormsg = None

    if user and prereg_url:
        errormsg = cls.cannotAdd(user, True, request=request)

    show_class =  (not filter) or (not errormsg)
    
    
    return {'class':      cls,
            'user':       user,
            'prereg_url': prereg_url,
            'errormsg':   errormsg,
            'show_class': show_class}
           
