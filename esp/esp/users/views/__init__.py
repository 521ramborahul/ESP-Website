from esp.users.views.usersearch import *
from esp.users.views.registration import *
from esp.users.views.password_reset import *
from esp.users.views.emailpref import *

from django.http import HttpResponseRedirect, HttpResponse
from esp.web.util.main import render_to_response
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required

from esp.tagdict.models import Tag

def filter_username(username, password):
    #   Allow login by e-mail address if so specified
    if username and '@' in username and Tag.getTag('login_by_email'):
        accounts = User.objects.filter(email = username)
        matches = []
        for u in accounts:
            if u.check_password(password):
                matches.append(u)
        if len(matches) > 0:
            username = matches[0].username
            
    return username

def login_checked(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    #   Run the username through the filter_username function in
    #   case it has any alternatives to suggest.
    if request.method == 'POST':
        new_post = request.POST.copy()
        new_post['username'] = filter_username(request.POST['username'], request.POST['password'])
        request.POST = new_post
        
    return login(request, *args, **kwargs)

def ajax_login(request, *args, **kwargs):
    import simplejson as json
    from django.contrib.auth import authenticate, login as auth_login
    from django.template.loader import render_to_string

    username = None
    password = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

    username = filter_username(username, password)

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            result_str = 'Login successful'
        else:
            result_str = 'Account disabled'
    else:
        result_str = 'Invalid username or password'
        
    request.user = user
    content = render_to_string('users/loginbox_content.html', {'request': request, 'login_result': result_str})
    
    return HttpResponse(json.dumps({'loginbox_html': content}))

def signed_out_message(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    return render_to_response('registration/logged_out.html',
                              request, request.get_node('Q/Web/myesp'),
                              {})
                              
@login_required
def disable_account(request):
    
    curUser = request.user
    
    if 'enable' in request.GET:
        curUser.is_active = True
        curUser.save()
    elif 'disable' in request.GET:
        curUser.is_active = False
        curUser.save()
        
    context = {'user': curUser}
        
    return render_to_response('users/disable_account.html', request, request.get_node('Q/Web/myesp'), context)
