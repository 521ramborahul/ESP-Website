from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl
from esp.program.modules import module_ext
from esp.web.util        import render_to_response
from esp.program.manipulators import SATPrepInfoManipulator
from django import forms
from django.core.cache import cache
from esp.program.models import SATPrepRegInfo
from esp.users.models   import ESPUser
from django.db.models.query import Q, QNot
from django.template.defaultfilters import urlencode
from django.template import Context, Template
from esp.miniblog.models import Entry


class CommModule(ProgramModuleObj):


    def students(self,QObject = False):
        if QObject:
            return {'satprepinfo': Q(satprepreginfo__program = self.program)}
        students = ESPUser.objects.filter(satprepreginfo__program = self.program).distinct()
        return {'satprepinfo': students }

    def isCompleted(self):
        
	satPrep = SATPrepRegInfo.getLastForProgram(self.user, self.program)
	return satPrep.id is not None

    @needs_admin
    def commfinal(self, request, tl, one, two, module, extra, prog):
        from django.template import Context, Template
        from esp.users.models import PersistentQueryFilter
        
        announcements = self.program.anchor.tree_create(['Announcements'])
        filterid, subject, body  = [request.POST['filterid'],
                                    request.POST['subject'],
                                    request.POST['body']    ]


        if request.POST.has_key('from') and \
           len(request.POST['from'].strip()) > 0:
            fromemail = request.POST['from']
        else:
            fromemail = None

        QObj = PersistentQueryFilter.getFilterFromID(filterid, User).get_Q()

        users = list(ESPUser.objects.filter(QObj).distinct())
        users.append(self.user)

        bodyTemplate    = Template(body)
        subjectTemplate = Template(subject)

        for user in users:
            
            anchor = announcements.tree_create([user.id])
            context_dict = {'name': ESPUser(user).name() }
            context = Context(context_dict)
            
            newentry = Entry(content   = bodyTemplate.render(context),
                             title     = subjectTemplate.render(context),
                             anchor    = anchor,
                             email     = True,
                             sent      = False,
                             fromuser  = self.user,
                             fromemail = fromemail
                            )

            newentry.save()

            newentry.subscribe_user(user)
        from django.conf import settings
        if hasattr(settings, 'EMAILTIMEOUT') and \
               settings.EMAILTIMEOUT is not None:
            est_time = settings.EMAILTIMEOUT * len(users)
        else:
            est_time = 1.5 * len(users)
            

        #        assert False, self.baseDir()+'finished.html'
        return render_to_response(self.baseDir()+'finished.html', request,
                                  (prog, tl), {'time': est_time})



    @needs_admin
    def commstep2(self, request, tl, one, two, module, extra, prog):
        pass
        

    @needs_admin
    def maincomm(self, request, tl, one, two, module, extra, prog):
        from esp.users.views     import get_user_list
        filterObj, found = get_user_list(request, self.program.getLists(True))

        if not found:
            return filterObj

        listcount = ESPUser.objects.filter(filterObj.get_Q()).distinct().count()

        return render_to_response(self.baseDir()+'step2.html', request,
                                  (prog, tl), {'listcount': listcount,
                                               'filterid' : filterObj.id})

        #getFilterFromID(id, model)

    @needs_student
    def satprepinfo(self, request, tl, one, two, module, extra, prog):
	manipulator = SATPrepInfoManipulator()
	new_data = {}
	if request.method == 'POST':
		new_data = request.POST.copy()
		
		errors = manipulator.get_validation_errors(new_data)
		
		if not errors:
			manipulator.do_html2python(new_data)
			new_reginfo = SATPrepRegInfo.getLastForProgram(request.user, prog)
			new_reginfo.addOrUpdate(new_data, request.user, prog)

                        return self.goToCore(tl)
	else:
		satPrep = SATPrepRegInfo.getLastForProgram(request.user, prog)
		
		new_data = satPrep.updateForm(new_data)
		errors = {}

	form = forms.FormWrapper(manipulator, new_data, errors)
	return render_to_response('program/modules/satprep_stureg.html', request, (prog, tl), {'form':form})

