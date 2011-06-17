from esp.program.models import *
from esp.datatree.models import DataTree
from django.db.models import Model
from django.db.models.related import RelatedObject
from django.db.models.fields.related import RelatedField, ManyToManyField
from inspect import isclass
import string

def path_v1(*args):
    '''
Finds a path from args[0] to args[1], or returns [] if they aren't related in the forward direction.

If they are both models, returns a list of strings, which represent valid field lookup paths that can filter the first based on the second. For example, path_v1(StudentRegistration, User) would return ['user'], and path_v1(StudentRegistration, ClassSubject) would return ['section__parent_class'].

If the first is a model and the second is an instance, a filter is applied to the model, subject to the constaint of the instance. Roughly, this means that path_v1(model, instance)[i] is equivalent to model.objects.filter(path_v1(model, type(instance))[i]=instance).

If the first is an instance and the second is a model, the function returns the instance of the model that is linked to the given instance. For example, path_v1(sr, User) would return sr.user, and path_v1(sr, ClassSubject) would return sr.section.parent_class (where sr is an instance of StudentRegistration).
    '''
    if 2 != len(args):
        raise TypeError("path_v1 expected 2 arguments, got "+str(len(args)))
    instances = [None for i in range(2)]
    classes = [None for i in range(2)]
    for i in range(2):
        if (not (isclass(args[i]) and issubclass(args[i], Model))) and (not isinstance(args[i], Model)): 
            raise TypeError("path_v1 argument "+str(i+1)+" must be a model or an instance of a model")
        if isclass(args[i]):
            classes[i] = args[i]
        else:
            instances[i] = args[i]
            classes[i] = type(args[i])
    if instances[0] and instances[1]:
        raise TypeError("at least one of the path_v1 arguments must be a model")
    stack = [((classes[0],),())]
    paths = []
    while stack:
        (model_heirarchy, path) = stack.pop()
        model = model_heirarchy[-1]
        if issubclass(model, DataTree):
            continue
        relatedObjects = {}
        if issubclass(model, classes[1]):
            paths.append(path)
        for name, field in model._meta.init_name_map().iteritems():
            if not isinstance(field[0], RelatedObject) and not isinstance(field[0], ManyToManyField):
                if isinstance(field[0], RelatedField):
                    stack.append((model_heirarchy+(field[0].rel.to,), path+(name,)))
            else:
                relatedObjects[name] = field
    results = [None for i in range(len(paths))]
    if instances[0]:
        for i in range(len(paths)):
            obj = instances[0]
            for attr in paths[i]:
                obj = getattr(obj, attr)
            results[i] = obj
    elif instances[1] and not instances[0]:
        results = [classes[0].objects.filter(**{'__'.join(path): instances[1]}) for path in paths]
    else:
        results = ['__'.join(path) for path in paths]
    if not results or not results[0]:
        return []
    return results

def path_v2(model, *conditions):
    '''
Returns a filter of all objects of type model, subject to the list of conditions. 

The first argument, model, must be a model. It cannot be an instance of a model, or any other object.

The list of conditions can be arbitrarily long, but must consist entirely of instances of models.

The function uses path_v1() to find the forward path from model to conditions[i] (for all i), and then applies the appropriate filter.

If there is more than one path from model to conditions[i], the functions asks the user (via the raw_input() function) which path(s) to filter on.
    '''
    if not (isclass(model) and issubclass(model, Model)):
        raise TypeError("path_v2 argument 1 must be a model")
    if not len(conditions):
        return model.objects.all()
    models = [None for i in range(len(conditions))]
    for i in range(len(conditions)):
        if not isinstance(conditions[i], Model): 
            raise TypeError("path_v2 argument 2 must be a list of instances of models")
        models[i] = type(conditions[i])
    kwargs = {}
    paths = None
    repeat = None
    use = None
    for i in range(len(conditions)):
        paths = path_v1(model, models[i])
        if len(paths) == 1:
             kwargs[paths[0]] = conditions[i]
        elif len(paths) > 1:
            for path in paths: 
                repeat = True
                while repeat:
                    use = raw_input("Include the path "+path+" as a condition ([y]/n)? ")
                    if string.lower(use) == 'y' or string.lower(use) == 'yes' or not use:
                        kwargs[path] = conditions[i]
                        repeat = False
                    elif string.lower(use) == 'n' or string.lower(use) == 'no':
                        repeat = False
    return model.objects.filter(**kwargs)
