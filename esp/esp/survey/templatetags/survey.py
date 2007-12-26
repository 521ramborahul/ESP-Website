__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 MIT ESP

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Contact Us:
ESP Web Group
MIT Educational Studies Program,
84 Massachusetts Ave W20-467, Cambridge, MA 02139
Phone: 617-253-4882
Email: web@esp.mit.edu
"""

from django import template
from django.template import loader
from esp.program.models.class_ import Class

register = template.Library()

@register.filter
def intrange(min_val, max_val):
    return range(int(min_val), int(max_val) + 1)
    
@register.filter
def field_width(min_val, max_val):
    return '%d%%' % (70 / (int(max_val) - int(min_val) + 1))
    
@register.filter
def substitute(input_str, item):
    #   Puts all of the attributes of the given item in the context dictionary
    t = template.Template(input_str)
    c = template.Context(item.__dict__)
    return t.render(c)

@register.filter
def uselist(input_str, lst):
    #   Takes a list of stuff and puts it in context as 'lst'
    t = template.Template(input_str)
    c = template.Context({'lst': lst})
    return t.render(c)

@register.filter
def tally(lst):
    #   Takes a list and returns a dictionary of entry: frequency
    d = {}
    for item in lst:
        if d.has_key(str(item)):
            d[str(item)] += 1
        else:
            d[str(item)] = 1
    return d

@register.filter
def weighted_avg(dct):
    #   Takes a dictionary of number: freq. and returns weighted avg. (float)
    #   Accepts "Yes", "True" as 1 and "No", "False" as 0.
    s = 0.0
    n = 0
    for key in dct.keys():
        try:
            weight = int(key, 10)
        except:
            weight = 0
            if ['yes', 'true'].count(key.lower()) > 0:
                weight = 1
        s += weight * dct[key]
        n += dct[key]
    
    if n == 0:
        return 0
    else:
        return s / n

@register.filter
def stripempty(lst):
    #   Takes a list and deletes empty entries. Whitespace-only is empty.
    return [ item for item in lst if len(str(item).strip()) > 0 ]

@register.filter
def makelist(lst):
    #   Because I can't understand Django's built-in unordered_list -ageng
    if len(lst) == 0:
        return "No responses"
    result = ""
    for item in lst:
        result += "<li>" + item + "</li>" + '\n'
    return result

@register.filter
def numeric_stats(lst, n):
    if len(lst) == 0:
        return "No responses"
    t = tally(lst)
    a = weighted_avg(t)
    result = '<ul><li> mean: ' + ( '%.2f' % a ) + '</li></ul>'
    result += '<ul>'
    for i in range(1, n+1):
        if not t.has_key(str(i)):
            t[str(i)] = 0
        result += '<li>' + str(i) + ': ' + str(t[str(i)]) + '</li>'
    result += '</ul>'
    return result

@register.filter
def boolean_stats(lst):
    if len(lst) == 0:
        return "No responses"
    t = tally(lst)
    a = 100 * weighted_avg(t)
    result = '<ul><li> % "Yes": ' + ( '%.2f' % a ) + '</li></ul>'
    result += '<ul>'
    for i in ['Yes', 'No']:
        if not t.has_key(str(i)):
            t[str(i)] = 0
        result += '<li>' + str(i) + ': ' + str(t[str(i)]) + '</li>'
    result += '</ul>'
    return result

@register.filter
def average(lst):
    if len(lst) == 0:
        return 'N/A'
    try:
        sum = 0.0
        for l in lst:
            sum += float(l)
        return str(round(sum / len(lst), 2))
    except:
        return 'N/A'
    
@register.filter
def stdev(lst):
    if len(lst) == 0:
        return 'N/A'
    try:
        sum = 0.0
        std_sum = 0.0
        for l in lst:
            sum += float(l)
        mean = sum / len(lst)
        for l in lst:
            std_sum += abs(float(l) - mean)
        return str(round(std_sum / len(lst), 2))
    except:
        return 'N/A'
    
@register.filter
def histogram(answer_list, format='html'):
    """ Generate Postscript code for a histogram of the provided results, save it and return a string pointing to it. """
    from esp.settings import MEDIA_ROOT, TEMPLATE_DIRS
    HISTOGRAM_PATH = 'images/histograms/'
    HISTOGRAM_DIR = MEDIA_ROOT + HISTOGRAM_PATH
    from esp.web.util.latex import get_rand_file_base
    import os
    
    template_file = TEMPLATE_DIRS + '/survey/histogram_base.eps'
    file_base = get_rand_file_base()
    file_name = '/tmp/%s.eps' % file_base
    image_width = 2.75
    
    #   Place results in key, value pairs where keys contain values and values contain frequencies.
    context = {}
    context['file_name'] = file_name
    context['title'] = 'Results of survey'
    context['num_responses'] = len(answer_list)
    
    context['results'] = []
    for ans in answer_list:
        try:
            i = [r['value'] for r in context['results']].index(str(ans))
            context['results'][i]['freq'] += 1
        except ValueError:
            context['results'].append({'value': ans, 'freq': 1})
    
    context['results'].sort(key=lambda x: x['value'])
    
    #   Compute simple stats so postscript doesn't have to
    max_freq = 0
    context['num_keys'] = len(context['results'])
    for item in context['results']:
        if item['freq'] > max_freq:
            max_freq = item['freq']
            context['max_freq'] = max_freq
    
    file_contents = loader.render_to_string(template_file, context)
    file_obj = open(file_name, 'w')
    file_obj.write(file_contents)
    file_obj.close()
    
    #   We have the necessary EPS file, now we do any necessary conversions and include
    #   it into the output.
    if format == 'tex':
        return '\includegraphics[width=%fin]{%s}' % (image_width, file_name)
    elif format == 'html':
        os.system('gs -dTextAlphaBits=4 -dDEVICEWIDTHPOINTS=216 -dDEVICEHEIGHTPOINTS=162 -sDEVICE=png16m -R96 -sOutputFile=%s%s.png %s' % (HISTOGRAM_DIR, file_base, file_name))
        return '<img src="%s.png" />' % ('/media/' + HISTOGRAM_PATH + file_base)
    
@register.filter
def favorite_classes(answer_list, limit):
    result_header = '<ol>\n'
    result_footer = '</ol>\n'
    result_body = ''
    
    class_dict = {}
    
    for a in answer_list:
        for i in a:
            ind = int(i)
            if class_dict.has_key(ind):
                class_dict[ind] += 1
            else:
                class_dict[ind] = 1
               
    key_list = class_dict.keys()
    key_list.sort(key=lambda x: -class_dict[x])
   
    max_count = min(limit, len(key_list))
   
    for key in key_list[:max_count]:
        cl = Class.objects.filter(id=key)
        if cl.count() == 1:
            result_body += '<li>%s: %s (%d votes)\n' % (cl[0].emailcode(), cl[0].title(), class_dict[key])

    return result_header + result_body + result_footer
        