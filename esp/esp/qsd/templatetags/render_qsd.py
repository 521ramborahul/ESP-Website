from django import template
from django.shortcuts import render_to_response
from django.core.cache import cache
from esp.web.util.template import cache_inclusion_tag, DISABLED
from esp.qsd.models import QuasiStaticData
from esp.qsd.models import qsd_cache_key, qsd_edit_id
from urllib import quote

register = template.Library()

@cache_inclusion_tag(register,'inclusion/qsd/render_qsd.html')
def render_qsd(qsd):
    return {'qsdrec': qsd}
render_qsd.cached_function.depend_on_row(QuasiStaticData, lambda qsd: {'qsd': qsd})

@cache_inclusion_tag(register,'inclusion/qsd/render_qsd_inline.html')
def render_inline_qsd(url):
    qsd_obj = QuasiStaticData.objects.get_by_url(url)
    if qsd_obj is None:
        return {'url': url, 'edit_id': qsd_edit_id(url)}
    
    return {'qsdrec': qsd_obj}
render_inline_qsd.cached_function.depend_on_row(QuasiStaticData, lambda qsd: {'url':qsd.url})

@cache_inclusion_tag(register,'inclusion/qsd/render_qsd_inline.html')
def render_inline_program_qsd(program, name):
    #unlike the above method, we don't know the url, just a program object
    #we could attempt to construct the url in the template
    #or just do this
    url = QuasiStaticData.prog_qsd_url(program, name)
    qsd_obj = QuasiStaticData.objects.get_by_url(url)
    if qsd_obj is None:
        return {'url': url, 'edit_id': qsd_edit_id(url)}

    return {'qsdrec': qsd_obj}
render_inline_program_qsd.cached_function.depend_on_row(QuasiStaticData, lambda qsd: {'url':qsd.url})
    

class InlineQSDNode(template.Node):
    def __init__(self, nodelist, url, program_variable):
        self.nodelist = nodelist
        self.url = url
        self.program_variable = template.Variable(program_variable) if program_variable is not None else None
        
    def render(self, context):
        try:
            program = self.program_variable.resolve(context) if self.program_variable is not None else None
        except template.VariableDoesNotExist:
            program = None
        #   Accept literal string url argument if it is quoted; otherwise expect a template variable.
        #   template.Variable resolves string literals to themselves automatically
        url_resolved = template.Variable(self.url).resolve(context)
        if program is not None:
            url = QuasiStaticData.prog_qsd_url(program,url_resolved)
        else:
            url = url_resolved
        #probably should have an error message if variable was not None and prog was

        qsd_obj = QuasiStaticData.objects.get_by_url(url)
        if qsd_obj is None:
            title = self.url
            if program is not None:
                title += ' - ' + unicode(program)
            qsd_obj = QuasiStaticData(url=url,
                                      name='',
                                      title=title,
                                      content=self.nodelist.render(context))

        return render_to_response("inclusion/qsd/render_qsd_inline.html", {'qsdrec': qsd_obj}, context_instance=context).content

@register.tag
def inline_qsd_block(parser, token):
    tokens = token.split_contents()
    if len(tokens) == 2:
        iqb, url = tokens
    else:
        raise Exception("Wrong number of inputs for %s, 1 expected" % (tokens))
    
    nodelist = parser.parse(("end_inline_qsd_block",))
    parser.delete_first_token()
    
    return InlineQSDNode(nodelist, url, None)


@register.tag
def inline_program_qsd_block(parser, token):
    tokens = token.split_contents()
    if len(tokens) == 3:
        iqb, program, url = tokens
    else:
        raise Exception("Wrong number of inputs for %s, 2 expected" % (tokens))
    
    nodelist = parser.parse(("end_inline_program_qsd_block",))
    parser.delete_first_token()
    
    return InlineQSDNode(nodelist, url, program)

