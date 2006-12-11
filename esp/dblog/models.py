from django.db import models
from traceback import format_stack

# Create your models here.

class Log(models.Model):
    # Store/log errors
    text = models.TextField(blank=True)
    extra = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    current_date = models.DateTimeField(auto_now_add=True)

def error(err_txt, extra = '', stack_trace = None):
    # Log an error to the database
    # Let programmers be lame.  Auto stack trace.
    if stack_trace == None:
        stack_trace = "\n".join(format_stack())

    # Save the error as a database record
    err = Log()
    err.text = err_txt
    err.stack_trace = stack_trace
    err.extra = extra
    err.save()
