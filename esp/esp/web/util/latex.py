""" This module will render latex code and return a rendered display. """

import os.path
import os
from random import random
from md5    import md5
from esp.middleware import ESPError
from django.http import HttpResponse

TEX_TEMP = '/tmp/'
TEX_EXT  = '.tex'

def render_to_latex(filepath, context_dict={}, filetype='pdf'):
    """ Render some tex source to latex. This will run the latex
        interpreter and generate the necessary file type
        (either pdf, tex, ps, dvi, or a log file)   """
    from django.template import Context, Template, loader

    src = loader.find_template_source(filepath)[0]

    src = '{% load latex %}\n' + src

    context = Context(context_dict)

    t = Template(src)

    rendered_source = t.render(context)

    return gen_latex(rendered_source, filetype)
    

def gen_latex(texcode, type='pdf'):
    """ Generate the latex code. """

    file_base = get_rand_file_base()

    if type == 'tex':
        return HttpResponse(texcode, mimetype='text/plain')
    

    # write to the LaTeX file
    texfile   = open(file_base+'.tex', 'w')
    texfile.write(texcode)
    texfile.close()
    

    file_types = ['pdf','dvi','ps','log','tex']

    if type=='pdf':
        mime = 'application/pdf'
        os.system('cd /tmp; pdflatex %s.tex' % file_base)
        
    elif type=='dvi':
        mime = 'application/x-dvi'
        os.system('cd /tmp; latex %s.tex' % file_base)
        
    elif type=='ps':
        mime = 'application/postscript'
        os.system('cd /tmp; latex %s.tex' % file_base)
        os.system('cd /tmp; dvips %s -o %s.ps' % (file_base, file_base))
        os.remove('%s.dvi' % file_base)
        
    elif type=='log':
        mime = 'text/plain'
        os.system('cd /tmp; latex %s.tex' % file_base)
    else:
        raise ESPError(), 'Invalid type received for latex generation: %s should be one of %s' % (type, file_types)
    

    try:
        tex_log_file = open(file_base+'.log')
        tex_log      = tex_log_file.read()
        tex_log_file.close()
        os.remove(file_base+'.log')
    except:
        tex_log      = ''

    if type != 'log':
        try:
            new_file     = open(file_base+'.'+type)
            new_contents = new_file.read()
            new_file.close()
            os.remove(file_base+'.'+type)
            os.remove(file_base+'.tex')
        
        except:
            raise ESPError(), 'Could not read contents of %s. (Hint: try looking at the log file)' % file_base+'.'+type

    if type=='log':
        new_contents = tex_log

    return HttpResponse(new_contents, mimetype=mime)

    
    

def get_rand_file_base():
    rand = md5(str(random())).hexdigest()

    while os.path.exists('%s%s.%s' % (TEX_TEMP, rand, TEX_EXT)):
        rand = md5(str(random())).hexdigest()

   
    return TEX_TEMP + rand



    
