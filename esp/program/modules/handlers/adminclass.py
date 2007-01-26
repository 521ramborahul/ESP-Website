from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl
from esp.program.modules import module_ext
from esp.web.data        import render_to_response
from django.contrib.auth.decorators import login_required
from esp.program.models import Class, Program
from esp.users.models import UserBit, ESPUser
from django.utils.datastructures import MultiValueDict
from esp.cal.models              import Event

class AdminClass(ProgramModuleObj):


    def getClassSizes(self):
        min_size, max_size, class_size_step = (0, 200, 10)
        if self.classRegInfo.class_min_size:
            min_size = self.classRegInfo.class_min_size
            
        if self.classRegInfo.class_max_size:
            max_size = self.classRegInfo.class_max_size
            
        if self.classRegInfo.class_size_step:
            class_size_step = self.classRegInfo.class_size_step

        return range(min_size, max_size+1, class_size_step)

    def getClassGrades(self):
        min_grade, max_grade = (6, 12)
        if self.program.grade_min:
            min_grade = self.program.grade_min
        if self.program.grade_max:
            max_grade = self.program.grade_max

        return range(min_grade, max_grade+1)

    def getClasses(self):
        return self.user.getEditable(Class)
        
    def prepare(self, context={}):
        classes = self.getClasses()
        context['noclasses'] = (len(classes) == 0)
        context['classes']   = classes
        return context

    @needs_admin
    def approveclass(self, request, tl, one, two, module, extra, prog):
        classes = Class.objects.filter(id = extra)
        if len(classes) != 1 or not self.user.canEdit(classes[0]):
                return render_to_response(self.baseDir()+'cannoteditclass.html', request, (prog, tl),{})
        cls = classes[0]
        cls.accept()
        return self.goToCore(tl)        

    @needs_admin
    def rejectclass(self, request, tl, one, two, module, extra, prog):
        classes = Class.objects.filter(id = extra)
        if len(classes) != 1 or not self.user.canEdit(classes[0]):
                return render_to_response(self.baseDir()+'cannoteditclass.html', request, (prog, tl),{})
        cls = classes[0]
        cls.reject()
        return self.goToCore(tl)
    
    @needs_admin
    def main(self, request, tl, one, two, module, extra, prog):
        """ Display a teacher eg page """
        context = {}
        modules = self.program.getModules(self.user, 'manage')
        
        for module in modules:
            context = module.prepare(context)

                    
        context['modules'] = modules
        context['one'] = one
        context['two'] = two

        return render_to_response(self.baseDir()+'mainpage.html', request, (prog, tl), context)

    
 
    @needs_admin
    def deleteclass(self, request, tl, one, two, module, extra, prog):
        classes = Class.objects.filter(id = extra)
        if len(classes) != 1 or not self.user.canEdit(classes[0]):
                return render_to_response(self.baseDir()+'cannoteditclass.html', request, (prog, tl),{})
        cls = classes[0]
        cls.delete(True)
        return self.goToCore(tl)

    @needs_admin
    def coteachers(self, request, tl, one, two, module, extra, prog):
        from esp.users.models import ESPUser 
        if not request.POST.has_key('clsid'):
            return self.goToCore(tl) # just fails.

        if extra == 'nojs':
            ajax = False
        else:
            ajax = True
            
        classes = Class.objects.filter(id = request.POST['clsid'])
        if len(classes) != 1 or not self.user.canEdit(classes[0]):
            return render_to_response(self.baseDir()+'cannoteditclass.html', request, (prog, tl),{})

        cls = classes[0]

        # set txtTeachers and coteachers....
        if not request.POST.has_key('coteachers'):
            coteachers = cls.teachers()
            coteachers = [ ESPUser(user) for user in coteachers
                           if user.id != self.user.id           ]
            
            txtTeachers = ",".join([str(user.id) for user in coteachers ])
            
        else:
            txtTeachers = request.POST['coteachers']
            coteachers = txtTeachers.split(',')
            coteachers = [ x for x in coteachers if x != '' ]
            coteachers = [ ESPUser(ESPUser.objects.get(id=userid))
                           for userid in coteachers                ]

        op = ''
        if request.POST.has_key('op'):
            op = request.POST['op']

        conflictingusers = []
        error = False
        
        if op == 'add':

            if len(request.POST['teacher_selected'].strip()) == 0:
                error = 'Error - Please click on the name when it drops down.'

            elif (request.POST['teacher_selected'] == str(self.user.id)):
                error = 'Error - You cannot select yourself as a coteacher!'
            elif request.POST['teacher_selected'] in txtTeachers.split(','):
                error = 'Error - You already added this teacher as a coteacher!'

            if error:
                return render_to_response(self.baseDir()+'coteachers.html', request, (prog, tl),{'class':cls,
                                                                                                 'ajax':ajax,
                                                                                                 'txtTeachers': txtTeachers,
                                                                                                 'coteachers':  coteachers,
                                                                                                 'error': error})
            
            # add schedule conflict checking here...
            teacher = ESPUser.objects.get(id = request.POST['teacher_selected'])

            if cls.conflicts(teacher):
                conflictingusers.append(teacher.first_name+' '+teacher.last_name)
            else:    
                coteachers.append(teacher)
                txtTeachers = ",".join([str(coteacher.id) for coteacher in coteachers ])
            
        elif op == 'del':
            ids = request.POST.getlist('delete_coteachers')
            newcoteachers = []
            for coteacher in coteachers:
                if str(coteacher.id) not in ids:
                    newcoteachers.append(coteacher)

            coteachers = newcoteachers
            txtTeachers = ",".join([str(coteacher.id) for coteacher in coteachers ])
                         

        elif op == 'save':
            #            if
            for teacher in coteachers:
                if cls.conflicts(teacher):
                    conflictingusers.append(teacher.first_name+' '+teacher.last_name)
            if len(conflictingusers) == 0:
                for teacher in cls.teachers():
                    cls.removeTeacher(teacher)
                    cls.removeAdmin(teacher)

                # add self back...
                cls.makeTeacher(self.user)
                cls.makeAdmin(self.user, self.classRegInfo.teacher_class_noedit)

                # add bits for all new (and old) coteachers
                for teacher in coteachers:
                    cls.makeTeacher(teacher)
                    cls.makeAdmin(teacher, self.classRegInfo.teacher_class_noedit)                    
                
                return self.goToCore(tl)


        
        return render_to_response(self.baseDir()+'coteachers.html', request, (prog, tl),{'class':cls,
                                                                                         'ajax':ajax,
                                                                                         'txtTeachers': txtTeachers,
                                                                                         'coteachers':  coteachers,
                                                                                         'conflicts':   conflictingusers})
    @needs_admin
    def editclass(self, request, tl, one, two, module, extra, prog):
        classes = Class.objects.filter(id = extra)
        if len(classes) != 1 or not self.user.canEdit(classes[0]):
            return render_to_response(self.baseDir()+'cannoteditclass.html', request, (prog, tl),{})
        cls = classes[0]

        return self.makeaclass(request, tl, one, two, module, extra, prog, cls)

    @needs_admin
    def makeaclass(self, request, tl, one, two, module, extra, prog, newclass = None):
        
        new_data = MultiValueDict()
        context = {'module': self}
        new_data['grade_max'] = str(self.getClassGrades()[-1:][0])
        new_data['class_size_max']  = str(self.getClassSizes()[-1:][0])
        
        manipulator = manipulators.TeacherClassRegManipulator(self)

        if request.method == 'POST' and request.POST.has_key('class_reg_page'):
            if not self.deadline_met():
                return self.goToCore();
            
            new_data = request.POST.copy()
            #assert False, new_data            
            errors = manipulator.get_validation_errors(new_data)
            if not errors:
                manipulator.do_html2python(new_data)

                if newclass is None:
                    newclass = Class()

                if len(new_data['message_for_directors'].strip()) > 0 and \
                       new_data['message_for_directors'] != newclass.message_for_directors and \
                       self.classRegInfo.director_email:

                    send_mail('['+self.program.anchor.parent.friendly_name+"] Directors' Comments for Teacher Reg", \
                              """ Directors\' comments below:\nClass Title: %s\n\n %s\n\n>>>>>>>>>>>EOM""" % \
                              (new_data['title'], new_data['message_for_directors']) , \
                              ('%s <%s>' % (self.user.first_name + ' ' + self.user.last_name, self.user.email,)), \
                              [self.classRegInfo.director_email], True)


                for k, v in new_data.items():
                    if k != 'resources' and k != 'viable_times':
                        newclass.__dict__[k] = v

                if new_data['duration'] == '':
                    newclass.duration = 0.0
                else:
                    newclass.duration = float(new_data['duration'])
                    
                # datatree maintenance
                newclass.parent_program = self.program
                newclass.category = ClassCategories.objects.get(id=new_data['category'])
                newclass.anchor = self.program.anchor.tree_create(['DummyClass'])
                newclass.anchor.save()
                newclass.enrollment = 0
                newclass.save()
                newclass.anchor.delete()
                
                nodestring = newclass.category.category[:1].upper() + str(newclass.id)
                newclass.anchor = self.program.classes_node().tree_create([nodestring])
                newclass.anchor.friendly_name = newclass.title
                newclass.anchor.save()
                newclass.save()


                # ensure multiselect fields are set
                newclass.viable_times.clear()
                for block in new_data.getlist('viable_times'):
                    tmpQsc = DataTree.objects.get(id = int(block))
                    newclass.viable_times.add(tmpQsc)


                newclass.resources.clear()
                for resource in new_data.getlist('resources'):
                    tmpQsc = DataTree.objects.get(id = int(resource))
                    newclass.resources.add(tmpQsc)

                # add userbits
                newclass.makeTeacher(self.user)
                newclass.makeAdmin(self.user, self.classRegInfo.teacher_class_noedit)

                return self.goToCore(tl)
                            
        else:
            errors = {}
            if newclass is not None:
                new_data = newclass.__dict__
                new_data['category'] = newclass.category.id
                new_data['resources'] = [ resource.id for resource in newclass.resources.all() ]
                new_data['viable_times'] = [ event.id for event in newclass.viable_times.all() ]
                new_data['title'] = newclass.anchor.friendly_name
                new_data['url']   = newclass.anchor.name
                context['class'] = newclass

        #assert False, new_data
        context['one'] = one
        context['two'] = two
        if newclass is None:
            context['addoredit'] = 'Add'
        else:
            context['addoredit'] = 'Edit'

        #        assert False, new_data
        context['form'] = forms.FormWrapper(manipulator, new_data, errors)


        if len(self.getDurations()) < 2:
            context['durations'] = False
        else:
            context['durations'] = True
            
        return render_to_response(self.baseDir() + 'classedit.html', request, (prog, tl), context)


    @needs_admin
    def teacherlookup(self, request, tl, one, two, module, extra, prog, newclass = None):
        limit = 10
        from esp.web.json import JsonResponse
        from esp.users.models import UserBit
        from django.db.models import Q

        # Initialize anchors for identifying teachers
        q = GetNode( 'Q' )
        v = GetNode( 'V/Flags/UserRole/Teacher' )

        # Select teachers
        queryset = UserBit.bits_get_users(q, v)

        # Search for teachers with names that start with search string
        if not request.GET.has_key('q'):
            return self.goToCore()
        
        startswith = request.GET['q']
        parts = [x.strip() for x in startswith.split(',')]
        Q_name = Q(user__last_name__istartswith=parts[0])
        if len(parts) > 1:
            Q_name = Q_name & Q(user__first_name__istartswith=parts[1])

        # Isolate user objects
        queryset = queryset.filter(Q_name)[:(limit*10)]
        users = [ub.user for ub in queryset]
        user_dict = {}
        for user in users:
            user_dict[user.id] = user
        users = user_dict.values()

        # Construct combo-box items
        obj_list = [[user.last_name + ', ' + user.first_name + ' ('+user.username+')', user.id] for user in users]

        # Operation Complete!
        return JsonResponse(obj_list)
