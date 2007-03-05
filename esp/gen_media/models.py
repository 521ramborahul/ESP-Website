from django.db   import models
from django.conf import settings
from esp.users.models import User
from esp.middleware   import ESPError
import os

TEXIMAGE_BASE = settings.MEDIA_ROOT+'/latex'
TEXIMAGE_URL  = '/media/uploaded/latex'
IMAGE_TYPE    = 'png'
LATEX_DPI     = 150
LATEX_BG      = 'Transparent' #'white'

mimes         = {'gif': 'image/gif',
                 'png': 'image/png'}

commands = {'latex'  : 'openin_any=p /usr/bin/latex',
            'dvips'  : '/usr/bin/dvips',
            'convert': '/usr/bin/convert',
            'dvipng' : '/usr/bin/dvipng'}

TMP      = '/tmp'

class LatexImage(models.Model):

    content  = models.TextField()
    filename = models.TextField()
    filetype = models.CharField(maxlength=10)

    def getImage(self):
        if not self.file_exists():
            raise ESPError(False), 'Youre wrong'
            self.genImage()
            self.save()
        return str(self)

    def genImage(self):
        if not self.filename:
            self.filename = get_rand_file_base()
            self.filetype = IMAGE_TYPE
            
        tex = r"""\documentclass[fleqn]{article} \usepackage{amssymb,amsmath} """ +\
              r"""\usepackage[latin1]{inputenc} \begin{document} \\""" + \
              r""" \thispagestyle{empty} \mathindent0cm \parindent0cm $%s$ \end{document}""" % self.content

        fullpath = TMP+'/'+self.filename

        tex_file = open(fullpath + '.tex', 'w')
        tex_file.write(tex)
        tex_file.close()

        os.system('cd %s; %s -interaction=nonstopmode %s &>/dev/null' % \
                  (TMP, commands['latex'], self.filename))

        os.system( '%s -q -T tight -bg %s -D %s -o %s.png %s.dvi &&  %s %s.png %s/%s.%s &> /dev/null' % \
                  (commands['dvipng'], LATEX_BG, LATEX_DPI, fullpath, fullpath, commands['convert'], fullpath,
                   TEXIMAGE_BASE, self.filename, self.filetype))

        os.system('rm -f %s/%s*' % (TMP, self.filename))
        
        return True
        

    def __str__(self):
        return '<img src="%s/%s.%s" alt="%s" title="%s" border="0" class="LaTeX" align="absmiddle" />' % \
               (TEXIMAGE_URL, self.filename, self.filetype, self.content, self.content)
        

    def file_exists(self):
        if not self.filename:
            return False
        return os.path.exists('%s/%s' % (TEXIMAGE_BASE, self.filename))
    
def get_rand_file_base():
    import sha
    from random import random

    rand = sha.new(str(random())).hexdigest()

    while os.path.exists('%s/%s.%s' % (TEXIMAGE_BASE, rand, IMAGE_TYPE)):
        rand = sha.new(str(random())).hexdigest()

   
    return rand




    
