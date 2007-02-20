from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl, meets_deadline
from esp.program.modules import module_ext
from esp.web.util        import render_to_response
from django.contrib.auth.decorators import login_required
from esp.miniblog.models import Entry
from esp.datatree.models import GetNode

class TeacherRegCore(ProgramModuleObj):
    
    @meets_deadline()
    @needs_teacher
    def teacherreg(self, request, tl, one, two, module, extra, prog):
        """ Display a teacher eg page """
        context = {}
        modules = self.program.getModules(self.user, 'teach')
        
        context['completedAll'] = True
        for module in modules:
            if not module.isCompleted() and module.required:
                context['completedAll'] = False
                
            context = module.prepare(context)

                    
        context['modules'] = modules
        context['one'] = one
        context['two'] = two

        context['progposts'] = Entry.find_posts_by_perms(self.user,GetNode('V/Subscribe'),
                                                         self.program.anchor.tree_create(['Announcements', 'Teachers']))

        return render_to_response(self.baseDir()+'mainpage.html', request, (prog, tl), context)

    def isStep(self):
        return False
    
    @needs_teacher
    def teacherregold(self, request, tl, one, two, module, extra, prog):
	""" Display the registration page to allow a teacher to register for a program """
        context = {}
	context['one'] = one
	context['two'] = two
	context['teacher'] = self.user
	context['timeslots'] = self.program.anchor.tree_create(['Templates', 'TimeSlots']).series_set.all()
	
	clsList = [ x for x in self.user.getEditable(Class) if x.parent_program == self.program ]
	
#	if len(clsList) == 0:
#            return program_teacherreg2(request, tl, one, two, module, extra, prog)
            
	context['classes'] = clsList
	
	return render_to_response('program/selectclass', request, (prog, tl), context)


