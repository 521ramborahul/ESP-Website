
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
from esp.users.models import ContactInfo, UserBit, ESPUser
from esp.datatree.models import GetNode, DataTree
from esp.program.models import ArchiveClass, ClassCategories
from esp.web.util.main import navbar_data, preload_images, render_to_response
from django.db.models.query import QuerySet
from django.http import HttpResponse, Http404, HttpResponseNotAllowed, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime

#	Two inputs to each function:
#	-	category: what you sort or view by
#		(such as: year, program, subject category, title)
#	-	options: the particular filter for that data
#		(eg. 2004, Splash, ComputerScience)

class ArchiveFilter(object):
	category = ""
	options = ""
	def __init__(self, category = "", options = ""):
		self.category = category
		self.options  = options
	
	def __str__(self):
		return '%s, %s' % \
		        (self.category, self.options)

def compute_range(postvars, num_records):
	default_num_records = 25
	results_start = 0
	results_end = None
	if postvars.has_key('results_start'):
		results_start = int(postvars['results_start'])
	if postvars.has_key('results_end'):
		results_end = int(postvars['results_end'])
	if (num_records > default_num_records) and results_end == None:
		if postvars.has_key('max_num_results') and postvars['max_num_results'] != "":
			results_end = results_start + int(postvars['max_num_results'])
		else:
			results_end = results_start + default_num_records
			
	return {'start': results_start, 'end': results_end}
		
def extract_criteria(postvars):
	#	Use filters
	criteria = []
	for key in postvars.keys():
		if key.find("filter_") != -1 and len(key) > 7: criteria.append(ArchiveFilter(category = key[7:], options = postvars[key]))
	
	return criteria

def filter_archive(records, criteria):
	result = records
	for c in criteria:
		if c.category == 'year':
			result = result.filter(year__icontains = c.options)
		elif c.category == 'program':
			result = result.filter(program__icontains = c.options)
		elif c.category == 'title':
			result = result.filter(title__istartswith = c.options)
		elif c.category == 'category':
			result = result.filter(category__icontains = c.options)
		elif c.category == 'teacher':
			result = result.filter(teacher__icontains = c.options)
		elif c.category == 'description':
			result = result.filter(description__icontains = c.options)
			
	return result

def archive_classes(request, category, options, sortorder = None):
	context = {'selection': 'Classes'}
	context['category'] = category
	context['options'] = options
	
	
	
	url_criterion = ArchiveFilter(category = category, options = options)

	criteria_list = [url_criterion]
	criteria_list += extract_criteria(request.POST)
	#	assert False, [c.__str__() for c in criteria_list ]
	
	category_list = [n['category'] for n in ArchiveClass.objects.all().values('category').distinct()]
	program_list = [p['program'] for p in ArchiveClass.objects.all().values('program').distinct()]
	
	category_dict = {}
	classcatList = ClassCategories.objects.all()
	for letter in map(chr, range(65, 91)):
		category_dict[letter] = 'Unknown Category'
		
	for category in classcatList:
		category_dict[category.category[0].upper()] = category.category
	
	
	filter_keys = {	'category': [{'name': category_dict[c.upper()], 'value': c} for c in category_list],
			'year': [{'name': y, 'value': y} for y in range(1998, datetime.now().year + 1)],
			'title': [{'name': 'Starts with ' + letter, 'value': letter} for letter in map(chr, range(65,91))],
 			'program': [{'name': p, 'value': p.upper()} for p in program_list],
			'teacher': [{}],
			'description': [{}]
			}
	if request.POST.has_key('filter_teacher'): filter_keys['teacher'][0]['default_value'] = request.POST['filter_teacher']
	if request.POST.has_key('filter_description'): filter_keys['description'][0]['default_value'] = request.POST['filter_description']
	
	results = filter_archive(ArchiveClass.objects.all(), criteria_list)
	
	
	#	Sort the results by the specified order
	context['old_sortparams'] = sortorder
	if type(sortorder) is not list or len(sortorder) < 1:
		sortorder = ['year', 'category', 'program', 'title', 'teacher', 'description']
		
	ordered_results = results
	
	sortorder.reverse()
	for parameter in sortorder:
		ordered_results = ordered_results.order_by(parameter)
	sortorder.reverse()

	context['sortparams'] = [{'name': n, 'options': filter_keys[n]} for n in sortorder]

	for c in criteria_list:
		for s in context['sortparams']:
			for o in s['options']: 
				if o.has_key('value') and o.has_key('name'):
					if c.category == s['name'] and c.options == o['value']: o['selected'] = True

	#	Display the appropriate range of results
	res_range = compute_range(request.POST, ordered_results.count())
	context['results_range'] = res_range
		
	#	Deal with the Django bug preventing you from using no "end"
	if res_range['end'] is None:
		res_range['end'] = ordered_results.count()

	#	Rename all of the class categories and uppercase the programs
	for entry in ordered_results[res_range['start']:res_range['end']]:
		entry.category = category_dict[entry.category.upper()]	
		entry.program = entry.program.upper()
		#	entry.title = entry.title.capitalize()
	
	#	Compute the headings for the 'jump to category' part
	if sortorder[0] == 'title':
		headings = [item.__dict__['title'][0] for item in ordered_results[res_range['start']:res_range['end']]]
	else:
		headings = [item.__dict__[sortorder[0]] for item in ordered_results[res_range['start']:res_range['end']]]
	
	headings.sort()
	context['headings'] = set(headings)
	
	#	Fill in context some more
	context['results'] = list(ordered_results[res_range['start']:res_range['end']])
	context['results_range']['start'] = context['results_range']['start'] + 1
	if request.POST.has_key('max_num_results'):
		context['max_num_results'] = request.POST['max_num_results']
	context['num_results_list'] = [10, 25, 50, 100, 250]
	context['num_results'] = ordered_results.count()
	context['num_results_shown'] = len(context['results'])
	
	return render_to_response('program/archives.html', request, GetNode('Q/Web/archives'), context) 

def archive_teachers(request, category, options):
	context = {'selection': 'Teachers'}
	context['category'] = category
	context['options'] = options
	
	return render_to_response('program/archives.html', request, None, context) 
	
def archive_programs(request, category, options):
	context = {'selection': 'Programs'}
	context['category'] = category
	context['options'] = options
	
	return render_to_response('program/archives.html', request, None, context) 

archive_handlers = {	'classes': archive_classes,
			'teachers': archive_teachers,
			'programs': archive_programs,
		}

