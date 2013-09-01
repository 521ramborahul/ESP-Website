
__author__    = "Individual contributors (see AUTHORS file)"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "AGPL v.3"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 by the individual contributors
  (see AUTHORS file)

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

Contact information:
MIT Educational Studies Program
  84 Massachusetts Ave W20-467, Cambridge, MA 02139
  Phone: 617-253-4882
  Email: esp-webmasters@mit.edu
Learning Unlimited, Inc.
  527 Franklin St, Cambridge, MA 02139
  Phone: 617-379-0178
  Email: web-team@lists.learningu.org
"""
# Create your views here.

from django.forms.models import modelformset_factory
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

from .models import NewResourceType, AbstractResource, NewResource
from .forms import NewResourceFormSet, NewResourceTypeForm, AbstractResourceForm, NewResourceForm
from esp.web.util import render_to_response

def manageResources(request):
    context = {}
    if request.method == 'POST':
        if 'new-resource-type' in request.POST:
            #we've updated a NewResourceType
            if request.POST['new-resource-type']=='None':
                newResourceTypeForm = NewResourceTypeForm(request.POST)
                if newResourceTypeForm.is_valid():
                    newResourceType = newResourceTypeForm.save()
                    newResourceType.html_id = 'new-resource-type-%s' % newResourceType.id
                    newResourceType.extra = NewResourceType()
                    newResourceType.extra.html_id = 'new-resource-type-add'
                    newResourceType.extra.form = NewResourceTypeForm()
                    newResourceType.extra.show = False
                else:
                    newResourceType = NewResourceType()
                    newResourceType.html_id = 'new-resource-type-add'
            else:
                newResourceTypeId = int(request.POST['new-resource-type'])
                newResourceType = NewResourceType.objects.get(id=newResourceTypeId)
                newResourceTypeForm = NewResourceTypeForm(request.POST, instance=newResourceType)
            if newResourceTypeForm.is_valid():
                newResourceType = newResourceTypeForm.save()
                newResourceType.html_id = 'new-resource-type-%s' % newResourceType.id
            newResourceType.form = newResourceTypeForm
            newResourceType.show = True
            context['newResourceType']=newResourceType
            return render_to_response('resources/new_resource_type_form.html',request, context)
        elif 'abstract-resource' in request.POST:
            #we've updated an AbstractResource (or its associated Resources)
            if request.POST['abstract-resource']=='None':
                abstractResourceForm = AbstractResourceForm(request.POST)
                newResourceFormSet = NewResourceFormSet(request.POST, request.FILES, prefix='abstract-resource-add', queryset = NewResource.objects.none())
                if abstractResourceForm.is_valid():
                    if newResourceFormSet.is_valid():
                        abstractResource = abstractResourceForm.save()
                        for newResource in newResourceFormSet.save(commit=False):
                            newResource.abstraction=abstractResource
                            newResource.save()
                        newResourceFormSet.save_m2m()
                        abstractResource.html_id = 'abstract-resource-%s' % abstractResource.id
                        abstractResource.extra = AbstractResource()
                        abstractResource.extra.html_id = 'abstract-resource-add'
                        abstractResource.extra.form = AbstractResourceForm()
                        abstractResource.extra.newResourceFormSet = NewResourceFormSet(queryset=AbstractResource.objects.none(), prefix="abstract-resource-add")
                        abstractResource.extra.show = False
                    else:
                        abstractResource = AbstractResource()
                        abstractResource.html_id='abstract-resource-add'
                else:
                    abstractResource = AbstractResource()
                    abstractResource.html_id='abstract-resource-add'
            else:
                abstractResourceId = int(request.POST['abstract-resource'])
                abstractResource = AbstractResource.objects.get(id=abstractResourceId)
                abstractResourceForm = AbstractResourceForm(request.POST, instance=abstractResource)
                if abstractResourceForm.is_valid():
                    newResourceFormSet = NewResourceFormSet(request.POST, request.FILES, prefix='abstract-resource-%s' % abstractResourceId, queryset = abstractResource.newresource_set.all())
                    if newResourceFormSet.is_valid():
                        abstractResourceForm.save()
                        for newResource in newResourceFormSet.save(commit=False):
                            newResource.abstraction=abstractResource
                            newResource.save()
                        newResourceFormSet.save_m2m()
                        abstractResource.html_id = 'abstract-resource-type-%s' % abstractResource.id
            abstractResource.form = abstractResourceForm
            abstractResource.newResourceFormSet = newResourceFormSet
            abstractResource.show = True
            context['abstractResource'] = abstractResource
            return render_to_response('resources/abstract_resource_form.html', request, context)
        else:
            return HttpResponseBadRequest('')
    else:
        #we aren't submitting a form
        newResourceTypes = list(NewResourceType.objects.filter(is_active=True)) #listify these so we can index into them
        abstractResources = list(AbstractResource.objects.filter(is_active=True).prefetch_related('newresource_set'))
        newResourceTypeIndices = {}
        rootNewResourceTypes = []
        for i, newResourceType in enumerate(newResourceTypes):
            newResourceType.form = NewResourceTypeForm(instance=newResourceType)
            newResourceType.html_id = 'new-resource-type-%s' % newResourceType.id
            newResourceType.show = False
            newResourceTypeIndices[newResourceType.id]=i
            newResourceType.children=[]
        for newResourceType in newResourceTypes:
            # populate the tree of resource types
            if newResourceType.parent_id is not None:
                newResourceTypes[newResourceTypeIndices[newResourceType.parent_id]].children.append(newResourceType)
            else:
                rootNewResourceTypes.append(newResourceType)
        for abstractResource in abstractResources:
            abstractResource.form = AbstractResourceForm(instance=abstractResource)
            abstractResource.newResourceFormSet = NewResourceFormSet(queryset=abstractResource.newresource_set.all(), prefix="abstract-resource-%s" % abstractResource.id)
            abstractResource.html_id = 'abstract-resource-%s' % abstractResource.id
            newResourceTypes[newResourceTypeIndices[abstractResource.resource_type_id]].children.append(abstractResource) #these will always be leaves of the tree so it's easier
        context['newResourceTypes']=newResourceTypes
        context['abstractResources']=abstractResources
        context['rootNewResourceTypes']=rootNewResourceTypes
        addNewResourceType = NewResourceType()
        addNewResourceType.html_id = 'new-resource-type-add'
        addNewResourceType.form = NewResourceTypeForm()
        addNewResourceType.show = False
        context['addNewResourceType'] = addNewResourceType
        addAbstractResource = AbstractResource()
        addAbstractResource.html_id = 'abstract-resource-add'
        addAbstractResource.form = AbstractResourceForm()
        addAbstractResource.newResourceFormSet = NewResourceFormSet(queryset=AbstractResource.objects.none(), prefix="abstract-resource-add")
        addAbstractResource.show = False
        context['addAbstractResource'] = addAbstractResource
    return render_to_response('resources/manage_resources.html', request, context)
        
        
