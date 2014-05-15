from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from vmtemplates.models import VMTemplate,loadFromRequest,hashFilename,createNew
from vmtemplates import verification
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import RequestContext

def home(request):
   if request.user.is_authenticated():
      return HttpResponseRedirect('/profile/')
   if request.method == 'POST':
      return verification.signin(request)
   else:
      return render(request,'home.html')

@login_required
def profile(request):
    user = request.user
    limit = 10
    templates = VMTemplate.objects.filter(create_user=user)
    paginator = Paginator(templates, limit)
    page = request.GET.get('page')
    try:
        templates = paginator.page(page)
    except PageNotAnInteger:
        templates = paginator.page(1)
    except EmptyPage:
        templates = paginator.page(paginator.num_pages)
    return render_to_response('profile.html',{'templates':templates,'username':user.username})

@login_required
def template(request,username, tp):
    try:
        user = request.user
        template = VMTemplate.objects.get(filename = tp, create_user = user)
        return render_to_response('showtemplate.html',{'template':template,'username':user.username})
    except:
        return render_to_response('showdenied.html',{'username':user.username})

@login_required
def add(request):
    user = request.user
    if request.method == 'POST':
        rawDict = loadFromRequest(request)
	msg=''
	if rawDict['name']=='':
	    msg += 'name '
	if rawDict['os_type']=='':
	    msg += 'os_type '
	if rawDict['distribution']=='':
	    msg += 'distribution '
	if rawDict['deploy_method']=='':
	    rawDict['deploy_method'] = 'nfsmount'
	if rawDict['kernel']=='':
	    msg += 'kernel '
	if rawDict['node_type']=='':
	    rawDict['node_type'] = 'undefined '
	if rawDict['capabilities']=='':
	    rawDict['capabilities'] = 'vNode '
	if rawDict['memory'] == 0:
	    msg += 'memory '
	if rawDict['disk'] ==0 :
	    msg += 'disk '
	if rawDict['repository']=='':
	    msg += 'repository '
	if rawDict['deploy_url']=='':
	    msg += 'deploy_url '
	if rawDict['description']=='':
	    rawDict['description'] = 'No Discription'
        if msg != '':
            msgDict = rawDict.copy()
            msgDict['msg']=msg+"need to be corrected!"
            msgDict['username']= user.username
            return render(request,'add.html',msgDict)
        filename = hashFilename(rawDict)
        print rawDict
        try:
            new_template = createNew(rawDict,filename)
            redirect_url = "../profile/"+user.username+"/template/"+filename+"/"
            return HttpResponseRedirect(redirect_url)
        except:
            msg = 'Failed to create new template. You perhaps have created a same template.'
            msgDict = rawDict.copy()
            msgDict['msg'] = msg
            msgDict['username'] = user.username
            return render(request, 'add.html',msgDict)
    else:
        t = get_template('add.html')
        return render(request, 'add.html', {'username':user.username,'deploy_method':'nfsmount','node_type':'undefined','capabilities':'vNode'})

@login_required
def delete(request, username, tp):
    user = request.user
    if username != user.username:
        return render(request, 'showdenied.html', { 'username':username })
    try:
        template = VMTemplate.objects.get(create_user=user, filename = tp)
        template.delete()
        return HttpResponseRedirect('../../../../')
    except:
        return render(request, 'showdenied.html',{'username':username})

@login_required
def tphowto(request, username, tp):
    user = request.user
    try:
        template = VMTemplate.objects.get(create_user=user, filename = tp)
        return render(request, 'tphowto.html',{'username':username, 'template':template})
    except:
        return render(request, 'showdenied.html',{'username':username})


@login_required
def tpreq(request, username, tp):
    user = request.user
    try:
        template = VMTemplate.objects.get(create_user=user, filename = tp)
        return render(request, 'tpreq.html',{'username':username,'template':template})
    except:
        return render(request, 'showdenied.html',{'username':username})

def signup(request):
   if request.method == 'POST':
      return verification.register(request)
   else:
      return render(request,'signup.html')
