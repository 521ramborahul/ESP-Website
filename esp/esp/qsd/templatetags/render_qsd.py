from django import template
from esp.datatree.models import *
from esp.users.models import UserBit
from esp.web.util.template import cache_inclusion_tag, DISABLED
from esp.qsd.models import QuasiStaticData
from esp.qsd.models import qsd_cache_key
from urllib import quote

register = template.Library()

def cache_key(qsd, user=None):
    return qsd_cache_key(qsd.path, qsd.name, user,)

def inline_cache_key(input_anchor, path, user=None):
    if user and hasattr(user, 'id') and user.id is not None:
        return '%s_%s_%d_inline' % (input_anchor.id, path, user.id)
    else:
        return '%s_%s_anon_inline' % (input_anchor.id, path)

@cache_inclusion_tag(register,'inclusion/qsd/render_qsd.html', cache_key_func=cache_key, cache_time=300)
def render_qsd(qsd, user=None):
    edit_bits = False
    if user:
        edit_bits = UserBit.UserHasPerms(user, qsd.path, DataTree.get_by_uri('V/Administer/Edit'))
    return {'qsdrec': qsd, 'edit_bits': edit_bits}

@cache_inclusion_tag(register,'inclusion/qsd/render_qsd_inline.html', cache_key_func=inline_cache_key, cache_time=300)
def render_inline_qsd(input_anchor, qsd, user=None):
    if isinstance(input_anchor, basestring):
        try:
            anchor = DataTree.get_by_uri(input_anchor)
        except DataTree.NoSuchNodeException:
            return {}
                
    elif isinstance(input_anchor, DataTree):
        anchor = input_anchor
    else:
        return {}

    edit_bits = False
    if user:
        edit_bits = UserBit.UserHasPerms(user, anchor, DataTree.get_by_uri('V/Administer/Edit'))
    qsd_obj = anchor.quasistaticdata_set.filter(name=qsd).order_by('-id')
    if len(qsd_obj) == 0:
        return {'edit_bits': edit_bits, 'qsdname': qsd, 'anchor_id': anchor.id}
    qsd_obj = qsd_obj[0]
    
    return {'qsdrec': qsd_obj, 'edit_bits': edit_bits}
