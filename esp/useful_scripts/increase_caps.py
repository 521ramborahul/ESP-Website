#!/usr/bin/env python2

# Find classes which capacity below the room capacity, and send the teacher an email asking if
# they want to increase their class capacity to the room capacity

from script_setup import *

from esp.dbmail.models import send_mail

program = Program.objects.get(url='Spark/2015')

email_subject_template = 'Your Spark class %(email_code)s: "%(title)s"'
email_template = '''
Hi %(teacher_names)s,

Thanks for teaching for Spark!  We've scheduled your class %(email_code)s:
"%(title)s", with capacity %(class_cap)s.  Some of the sections are scheduled in
rooms with more space than that:

%(section_texts)s

Would you be willing to increase the max size of your class to the room size
(or to any amount in between)?  If you would like to do so, please let us know
by replying to this email by 11:59pm on Friday, February 27.  If not, you can
simply ignore this email.

Thanks,
Miriam and Taylor
Spark 2015 Directors
'''
section_template = '%(email_code)s: room %(room)s (capacity %(room_cap)s)'

from_address = 'spark@mit.edu'
extra_headers = {
    'Sender': 'server@esp.mit.edu',
}

def listify(l):
    """Convert a list [a,b,c] to text "a, b, and c" or similar."""
    l = list(l)
    if len(l) == 0:
        raise Exception
    if len(l) == 1:
        return l[0]
    if len(l) == 2:
        return ' and '.join(l)
    else:
        l[-1] = 'and ' + l[-1]
        return ', '.join(l)

for c in program.classes():
    section_texts = []
    for s in c.sections.all():
        if (s.classrooms().exists()
                and s.capacity < s._get_room_capacity()
                and s.capacity < 150):
            section_texts.append(section_template % {
                'email_code': s.emailcode(),
                'room': s.initial_rooms()[0].name,
                'room_cap': s._get_room_capacity(),
            })
    if section_texts:
        teacher_names = listify(c.teachers.values_list('first_name', flat=True))
        email_text = email_template % {
            'teacher_names': teacher_names,
            'email_code': c.emailcode(),
            'title': c.title,
            'class_cap': c.class_size_max,
            'section_texts': '\n'.join(section_texts),
        }
        subject = email_subject_template % {
            'email_code': c.emailcode(),
            'title': c.title,
        }
        to_address = '%s-teachers@esp.mit.edu' % c.emailcode()

        send_mail(subject, email_text, from_address,
                  [to_address, from_address], extra_headers=extra_headers)

        
            
