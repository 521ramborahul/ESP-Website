from esp.program.tests import ProgramFrameworkTest

class AvailabilityModuleTest(ProgramFrameworkTest):
    def setUp(self, *args, **kwargs):
        from esp.program.modules.base import ProgramModule, ProgramModuleObj
        
        # Set up the program -- we want to be sure of these parameters
        kwargs.update( {
            'num_timeslots': 3, 'timeslot_length': 50, 'timeslot_gap': 10,
            'num_teachers': 1, 'classes_per_teacher': 2, 'sections_per_class': 1
            } )
        super(AvailabilityModuleTest, self).setUp(*args, **kwargs)
        
        # Get and remember the instance of AvailabilityModule
        am = ProgramModule.objects.get(handler='AvailabilityModule')
        self.moduleobj = ProgramModuleObj.getFromProgModule(self.program, am)
        self.moduleobj.user = self.teachers[0]
        
        # Set the section durations to 0:50 and 1:50
        sec = self.program.sections()[0]
        sec.duration = '0.83'
        sec.save()
        sec = self.program.sections()[1]
        sec.duration = '1.83'
        sec.save()
        
        # Add the teacher to the classes
        for cls in self.program.classes():
            cls.makeTeacher( self.moduleobj.user )
    
    def runTest(self):
        # Now we have a program with 3 timeslots, 1 teacher, and 2 classes.
        # Grab the timeslots
        timeslots = self.program.getTimeSlots().values_list( 'id', flat=True )
        
        # Check that the teacher starts out without availability set
        self.failUnless( not self.moduleobj.isCompleted() )
        
        # Log in as the teacher
        self.failUnless( self.client.login( username='teacher0', password='password' ), "Couldn't log in as teacher" )
        
        # Submit availability, checking results each time
        # Available for one timeslot
        response = self.client.post( self.moduleobj.get_full_path(), data={ 'timeslots': timeslots[:1] } )
        self.failUnless( response.status_code == 302 )
        self.failUnless( not self.moduleobj.isCompleted() )
        # Two timeslots
        response = self.client.post( self.moduleobj.get_full_path(), data={ 'timeslots': timeslots[:2] } )
        self.failUnless( response.status_code == 302 )
        self.failUnless( not self.moduleobj.isCompleted() )
        # Three timeslots
        response = self.client.post( self.moduleobj.get_full_path(), data={ 'timeslots': timeslots } )
        self.failUnless( response.status_code == 302 )
        self.failUnless( self.moduleobj.isCompleted() )
