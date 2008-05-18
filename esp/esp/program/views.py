
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
from esp.web.util import render_to_response
from esp.cal.models import Event
from esp.qsd.models import QuasiStaticData
from esp.datatree.models import GetNode, DataTree
from esp.miniblog.models import Entry
from django.http import HttpResponseRedirect, HttpResponse, Http404
from esp.users.models import ESPUser, UserBit, GetNodeOrNoBits
from esp.program.models import ClassSubject
from django import forms

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.decorators import login_required
from esp.web.models import NavBarEntry

from esp.utils.forms import save_instance
from esp.program.models import Program
from esp.program.modules.base import needs_admin
from esp.program.forms import ProgramCreationForm
from esp.program.setup import prepare_program, commit_program
from esp.accounting_docs.models import Document
from esp.middleware import ESPError
from esp.accounting_core.models import LineItemType

@login_required
def updateClass(request, id):
    """ An update-class form """
    try:
        manipulator = Class.ChangeManipulator(id)
    except Class.DoesNotExist:
	raise Http404

    curUser = ESPUser(request.user)
    if not curUser.canEdit(Class.objects.get(id=id)):
        raise Http404
	
    orig_class = manipulator.original_object

    #errors = None

    if request.POST:
        new_data = request.POST.copy()
        # We're not letting users change these.  Admins only, and only via the Admin interface.
        assert False, (new_data['anchor'], str(orig_class.anchor.id))
        
        new_data['anchor'] = str(orig_class.anchor.id)
        new_data['parent_program'] = str(orig_class.parent_program.id)


        errors = manipulator.get_validation_errors(new_data)

        if not errors:
            manipulator.do_html2python(new_data)

            manipulator.save(new_data)

            return HttpResponseRedirect(".")
    else:
        errors = {}
        new_data = orig_class.__dict__

    form = forms.FormWrapper(manipulator, new_data, errors)
    return render_to_response('program/class_form.html', request, orig_class.parent_program, {'form': form, 'class': orig_class, 'edit': True, 'orig_class': orig_class })


#def courseCatalogue(request, one, two):
#    """ aseering 9-1-2006 : This function appears to not be used by anything; esp.web.program contains its equivalent.
#        If nothing breaks by commenting this out, it should probably be deleted. """
#    treeItem = "Q/Programs/" + one + "/" + two 
#    prog = GetNode(treeItem).program_set.all()
#    if len(prog) < 1:
#        return render_to_response('users/construction', request, None, {})
#    prog = prog[0]
#    clas = list(prog.class_set.all().order_by('category'))
#    p = one + " " + two
#    return render_to_response('program/catalogue', request, prog,{'courses': clas })


def programTemplateEditor(request):
    """ Generate and display a listing of all QSD pages in the Programs template
    (QSD pages that are created automatically when a new program is created) """
    qsd_pages = []

    template_node = GetNode('Q/Programs/Template')

    for qsd in template_node.quasistaticdata_set.all():
        qsd_pages.append( { 'edit_url': qsd.name + ".edit.html",
                            'view_url': qsd.name + ".html",
                            'page': qsd } )

    have_create = UserBit.UserHasPerms(request.user, template_node, GetNode('V/Administer/Edit'))

    return render_to_response('display/qsd_listing.html', request, GetNode('Q/Web'), {'qsd_pages': qsd_pages, 'have_create': have_create })

def classTemplateEditor(request, program, session):
    """ Generate and display a listing of all QSD pages in the Class template within the specified program
    (QSD pages that are created automatically when a new class is created) """
    qsd_pages = []

    try:
        template_node = GetNodeOrNoBits('Q/Programs/' + program + '/' + session + '/Template', request.user)
    except DataTree.NoSuchNodeException:
        raise Http404

    for qsd in template_node.quasistaticdata_set.all():
        qsd_pages.append( { 'edit_url': qsd.name + ".edit.html",
                            'view_url': qsd.name + ".html",
                            'page': qsd } )

    have_create = UserBit.UserHasPerms(request.user, template_node, GetNode('V/Administer/Edit'))

    return render_to_response('display/qsd_listing.html', request, program, {'qsd_pages': qsd_pages,
                                                            'have_create': have_create })

@login_required
def managepage(request, page):
    if page == 'newprogram':

        template_prog = None

	if 'template_prog' in request.GET:
            #try:
            tprogram = Program.objects.get(id=int(request.GET["template_prog"]))

            template_prog = {}
            template_prog.update(tprogram.__dict__)
            del template_prog["id"]
            
            template_prog["program_modules"] = [ x["id"] for x in tprogram.program_modules.all().values("id") ]
            template_prog["term"] = tprogram.anchor.name
            template_prog["term_friendly"] = tprogram.anchor.friendly_name
            template_prog["anchor"] = tprogram.anchor.parent.id
            
            # aseering 5/18/2008 -- List everyone who was granted V/Administer on the specified program
            template_prog["admins"] = [ x["id"] for x in User.objects.filter(userbit__verb=GetNode("V/Administer"), userbit__qsc=tprogram.anchor).values("id") ]

            # aseering 5/18/2008 -- More aggressively list everyone who was an Admin
            #template_prog["admins"] = [ x.id for x in UserBit.objects.bits_get_users(verb=GetNode("V/Administer"), qsc=tprogram.anchor, user_objs=True) ]
            
            program_visible_bits = list(UserBit.objects.bits_get_users(verb=GetNode("V/Flags/Public"), qsc=tprogram.anchor).filter(user__isnull=True).order_by("-startdate"))
            if len(program_visible_bits) > 0:
                newest_bit = program_visible_bits[0]
                oldest_bit = program_visible_bits[-1]
    
                template_prog["publish_start"] = oldest_bit.startdate
                template_prog["publish_end"] = newest_bit.enddate

            student_reg_bits = list(UserBit.objects.bits_get_users(verb=GetNode("V/Deadline/Registration/Student"), qsc=tprogram.anchor).filter(user__isnull=True).order_by("-startdate"))
            if len(student_reg_bits) > 0:
                newest_bit = student_reg_bits[0]
                oldest_bit = student_reg_bits[-1]
    
                template_prog["student_reg_start"] = oldest_bit.startdate
                template_prog["student_reg_end"] = newest_bit.enddate

            teacher_reg_bits = list(UserBit.objects.bits_get_users(verb=GetNode("V/Deadline/Registration/Teacher"), qsc=tprogram.anchor).filter(user__isnull=True).order_by("-startdate"))
            if len(teacher_reg_bits) > 0:
                newest_bit = teacher_reg_bits[0]
                oldest_bit = teacher_reg_bits[-1]
    
                template_prog["teacher_reg_start"] = oldest_bit.startdate
                template_prog["teacher_reg_end"] = newest_bit.enddate

            
            line_items = LineItemType.objects.filter(anchor__name="Required", anchor__parent__parent=tprogram.anchor).values("amount", "finaid_amount")

            template_prog["base_cost"] = int(-sum([ x["amount"] for x in line_items]))
            template_prog["finaid_cost"] = int(-sum([ x["finaid_amount"] for x in line_items ]))

        if 'checked' in request.GET:
            # Our form's anchor is wrong, because the form asks for the parent of the anchor that we really want.
            # Don't bother trying to fix the form; just re-set the anchor when we're done.
            new_prog = Program(anchor=GetNode(request.session['prog_form'].clean_data['anchor'].uri + "/" + request.session['prog_form'].clean_data["term"]))
            new_prog = save_instance(request.session['prog_form'], new_prog)
            new_prog.anchor = GetNode(request.session['prog_form'].clean_data['anchor'].uri + "/" + request.session['prog_form'].clean_data["term"])
            
            commit_program(new_prog, request.session['datatrees'], request.session['userbits'], request.session['modules'], request.session['costs'])
            
            manage_url = '/manage/' + new_prog.url() + '/resources'
            return HttpResponseRedirect(manage_url)
    
        #   If the form has been submitted, process it.
        if request.method == 'POST':
            data = request.POST.copy()
            form = ProgramCreationForm(data)
    
            if form.is_valid():
                temp_prog = Program(anchor=form.clean_data['anchor'])
                temp_prog = save_instance(form, temp_prog, commit=False)
                datatrees, userbits, modules = prepare_program(temp_prog, form)
                request.session['prog_form'] = form
                request.session['datatrees'] = datatrees
                request.session['userbits'] = userbits
                request.session['modules'] = modules
                request.session['costs'] = ( form.clean_data['base_cost'], form.clean_data['finaid_cost'] )
              
                return render_to_response('program/newprogram_review.html', request, request.get_node('Q/Programs/'), {'prog': temp_prog, 'datatrees': datatrees, 'userbits': userbits, 'modules': modules})
            
                
        else:
            #   Otherwise, the default view is a blank form.
            if template_prog:
                form = ProgramCreationForm(template_prog)
            else:
                form = ProgramCreationForm()

        return render_to_response('program/newprogram.html', request, request.get_node('Q/Programs/'), {'form': form, 'programs': Program.objects.all().order_by('-id')})
        
    if page == 'submit_transaction':
        #   We might also need to forward post variables to http://shopmitprd.mit.edu/controller/index.php?action=log_transaction
        
        if request.POST.has_key("decision") and request.POST["decision"] != "REJECT":

            try:
                from decimal import Decimal
                post_locator = request.POST['merchantDefinedData1']
                post_amount = Decimal(request.POST['orderAmount'])
                post_id = request.POST['requestID']
                
                document = Document.receive_creditcard(request.user, post_locator, post_amount, post_id)
                
            except:
                from esp.middleware import ESPError
                raise ESPError(), "Your credit card transaction was successful, but a server error occurred while logging it.  The transaction has not been lost (please do not try to pay again!); this just means that the green Credit Card checkbox on the registration page may not be checked off.  Please <a href=\"mailto:esp-webmasters@mit.edu\">e-mail us</a> and ask us to correct this manually.  We apologize for the inconvenience."

            one = document.anchor.parent.name
            two = document.anchor.name

            return HttpResponseRedirect("http://%s/learn/%s/%s/confirmreg" % (request.META['HTTP_HOST'], one, two))
            
        return render_to_response( 'accounting_docs/credit_rejected.html', request, GetNode('Q/Accounting/'), {} )

    raise Http404
