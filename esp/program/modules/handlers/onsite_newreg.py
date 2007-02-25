from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl, needs_onsite
from esp.program.modules import module_ext
from esp.web.util        import render_to_response
from django.contrib.auth.decorators import login_required
from esp.users.models    import ESPUser, UserBit, User, ContactInfo, StudentInfo
from esp.datatree.models import GetNode
from django              import forms
from django.http import HttpResponseRedirect
from esp.program.models import RegistrationProfile
from esp.program.modules.manipulators import OnSiteNormalRegManipulator



class OnSiteRegister(ProgramModuleObj):


    def createBit(self, extension):
        verb = GetNode('V/Flags/Registration/'+extension)
        ub = UserBit.objects.filter(user = self.student,
                                    verb = verb,
                                    qsc  = self.program.anchor)
        if len(ub) > 0:
            return False

        ub = UserBit()
        ub.verb = verb
        ub.qsc  = self.program.anchor
        ub.user = self.student
        ub.recursive = False
        ub.save()
        return True
    
    @needs_onsite()
    def onsite_create(self, request, tl, one, two, module, extra, prog):
        manipulator = OnSiteNormalRegManipulator()
	new_data = {}
	if request.method == 'POST':
            new_data = request.POST.copy()
            
            errors = manipulator.get_validation_errors(new_data)
            
            if not errors:
                manipulator.do_html2python(new_data)
                username = base_uname = (new_data['first_name'][0]+ \
                                         new_data['last_name']).lower()
                if ESPUser.objects.filter(username = username).count() > 0:
                    i = 2
                    username = base_uname + str(i)
                    while ESPUser.objects.filter(username = username).count() > 0:
                        i += 1
                        username = base_uname + str(i)
                new_user = User(username = username,
                                first_name = new_data['first_name'],
                                last_name  = new_data['last_name'],
                                email      = new_data['email'],
                                is_staff   = False,
                                is_superuser = False)
                new_user.save()

                self.student = new_user

                new_user.save()

                regProf = RegistrationProfile.getLastForProgram(new_user,
                                                                self.program)
                contact_user = ContactInfo(first_name = new_user.first_name,
                                           last_name  = new_user.last_name,
                                           e_mail     = new_user.email)
                contact_user.save()
                regProf.contact_user = contact_user

                student_info = StudentInfo(graduation_year = ESPUser.YOGFromGrade(new_data['grade']))
                student_info.save()
                regProf.student_info = student_info

                regProf.save()

                new_user = ESPUser(new_user)
                
                new_user.recoverPassword()

                if new_data['paid']:
                    self.createBit('Paid')

                self.createBit('Attended')

                if new_data['medical']:
                    self.createBit('MedicalFiled')

                if new_data['liability']:
                    self.createBit('LiabilityFiled')

                self.createBit('OnSite')

		v = GetNode( 'V/Flags/UserRole/Student')
		ub = UserBit()
		ub.user = new_user
		ub.recursive = False
		ub.qsc = GetNode('Q')
		ub.verb = v
		ub.save()
                
                new_user = ESPUser(new_user)

                return render_to_response(self.baseDir()+'reg_success.html', request, (prog, tl), {'student': new_user, 'retUrl': '/onsite/%s/schedule_students?extra=115&op=usersearch&userid=%s' % \
                                                                                                   (self.program.getUrlBase(), new_user.id)})



                            

        
        else:
            new_data = {}
            errors = {}

	form = forms.FormWrapper(manipulator, new_data, errors)
	return render_to_response(self.baseDir()+'reg_info.html', request, (prog, tl), {'form':form})
        
 

