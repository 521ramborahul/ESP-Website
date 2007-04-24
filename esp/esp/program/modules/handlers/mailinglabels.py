
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

from esp.web.util.main import render_to_response
from esp.users.models import ESPUser
from esp.users.models import PersistentQueryFilter, K12School, ContactInfo, ESPUser, User, ESPError, ZipCode
from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl, meets_deadline, meets_grade
from esp.program.modules import module_ext
from django.http import HttpResponse
from django.db.models import Q
from esp.program.modules.forms.mailinglabels_schools import SchoolSelectForm
import operator


class MailingLabels(ProgramModuleObj):
    """ This allows one to generate Mailing Labels for both schools and users. You have the option of either creating a file which can be sent to MIT mailing services or actually create printable files.
    """

    @needs_admin
    def mailinglabel(self, request, tl, one, two, module, extra, prog):
        """ This function will allow someone to morph into a user for testing purposes. """
        from esp.users.views     import get_user_list
        if extra is None or extra.strip() == '':
            return render_to_response(self.baseDir()+'mailinglabel_index.html',request, (prog, tl), {})

        if 'schools' in extra.strip():                  
            if request.method == 'POST':

                if request.POST.has_key('filter_id'):
                    """
                    A filter was passed.
                    """
                    f = PersistentQueryFilter.objects.get(id = request.POST['filter_id'])
                    infos = f.getList(ContactInfo).distinct()
                else:

                    form = SchoolSelectForm(request.POST)
                    if form.is_valid():
                        try:
                            zipc = ZipCode.objects.get(zip_code = form.clean_data['zip_code'])
                        except:
                            raise ESPError(False), 'Please enter a valid US zipcode. "%s" is not valid.' % form.clean_data['zip_code']

                        zipcodes = zipc.close_zipcodes(form.clean_data['proximity'])

                        Q_infos = Q(k12school__id__isnull = False,
                                    address_zip__in = zipcodes)

                        grades = form.clean_data['grades'].split(',')

                        if len(grades) > 0:
                            Q_grade = reduce(operator.or_, [Q(k12school__grades__contains = grade) for grade in grades])
                            Q_infos &= Q_grade

                        f = PersistentQueryFilter.create_from_Q(ContactInfo, Q_infos, description="All ContactInfos for K12 schools with grades %s and %s miles from zipcode %s." % (form.clean_data['grades'], form.clean_data['proximity'], form.clean_data['zip_code']))

                        num_schools = ContactInfo.objects.filter(Q_infos).distinct().count()

                        return render_to_response(self.baseDir()+'schools_confirm.html', request, (prog, tl), {'filter':f,'num': num_schools})

                    else:
                        return render_to_response(self.baseDir()+'selectschools.html', request, (prog, tl), {'form': form})

            else:
                form = SchoolSelectForm(initial = {'zip_code': '02139'})

                return render_to_response(self.baseDir()+'selectschools.html', request, (prog, tl), {'form': form})

        else:
            filterObj, found = get_user_list(request, self.program.getLists(True))

            if not found:
                return filterObj

            infos = [ESPUser(user).getLastProfile().contact_user for user in ESPUser.objects.filter(filterObj.get_Q()).distinct() ]

        output = MailingLabels.gen_addresses(infos)

        if 'csv' in extra.strip():
            response = HttpResponse('\n'.join(output), mimetype = 'text/plain')
            return response

        
    @staticmethod
    def gen_addresses(infos):
        """ Takes a iterable list of infos and returns a lits of addresses. """

        import pycurl
        from django.template.defaultfilters import urlencode
        import re
        import time


        regex = re.compile(r""""background:url\(images\/table_gray.gif\); padding\:5px 10px;">\s*(.*?)<br \/>\s*(.*?)&nbsp;(.{2})&nbsp;&nbsp;(\d{5}\-\d{4})""")


        addresses = {}
        ids_zipped = []

        if infos[0].k12school_set.all().count() > 0:
            use_title = True
        else:
            use_title = False
        
        for info in infos:
            if info == None:
                continue

            schools = info.k12school_set.all()

            if len(schools) > 0:
                if schools[0].contact_title == 'SCHOOL':
                    title = None
                else:
                    title = schools[0].contact_title
            else:
                title = None

            if use_title:
                name = "'%s %s','%s'" % (info.first_name.strip(), info.last_name.strip(), title)
            else:
                name = '%s %s' % (info.first_name.strip(), info.last_name.strip())
            
            if info.address_postal != None:
                key = info.address_postal
            else:

                ids_zipped.append(info.id)

                #print info.__dict__

                post_data =  {'visited' : 1,
                              'pagenumber': 0,
                              'firmname': '',
                              'address1': '',
                              'urbanization': '',
                              'submit_x' : '',
                              'submit_y' : '',
                              'submit':    'Find ZIP Code'}


                post_data.update({'address2': info.address_street,
                                  'state'   : info.address_state,
                                  'city'    : info.address_city,
                                  'zip5'    : info.address_zip,
                                  })

                post_string = '&'.join(['%s=%s' % (key, urlencode(value)) for key, value in post_data.iteritems()])

                c = pycurl.Curl()

                c.setopt(pycurl.URL, 'http://zip4.usps.com/zip4/zcl_0_results.jsp')
                c.setopt(pycurl.POSTFIELDS, post_string)
                c.setopt(pycurl.POST, 1)
                c.setopt(pycurl.REFERER, 'http://zip4.usps.com/zip4/welcome.jsp')
                #c.setopt(pycurl.RETURNTRANSFER, True)



                import StringIO
                b = StringIO.StringIO()
                c.setopt(pycurl.WRITEFUNCTION, b.write)

                c.perform()

                retdata = b.getvalue().replace('\n','').replace('\r','')

                ma = regex.search(retdata)
                try:
                    key = "'%s','%s','%s','%s'" % (ma.group(1),
                                                   ma.group(2),
                                                   ma.group(3),
                                                   ma.group(4))
                    info.address_postal = key
                except:
                    key = False
                    info.address_postal = 'FAILED'

                info.save()

            if key != 'FAILED':

                if addresses.has_key(key):
                    if name.upper() not in [n.upper() for n in addresses[key]]:
                        addresses[key].append(name)
                else:
                    addresses[key] = [name]
            


                #time.sleep(1)
        if use_title:
            output = ["'Num','Name','Title','Street','City','State','Zip'"]
        else:
            output = ["'Num','Name','Street','City','State','Zip'"]
        #output.append(','.join(ids_zipped))
        i = 1
        for key, value in addresses.iteritems():
            if key != False:
                if use_title:
                    output.append("'%s',%s,%s" % (i, ' and '.join(value), key))
                else:
                    output.append("'%s','%s',%s" % (i,' and '.join(value), key))
                i+= 1
            
        return output


        
