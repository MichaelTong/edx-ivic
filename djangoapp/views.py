from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from vmtemplates.models import VMTemplate,loadFromRequest,hashFilename,createNew,exsit
from vmtemplates import verification
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher
from multiprocessing.connection import Client
from djangoapp.settings import *

def sentToQueue(item):
    address = ('localhost',int(QUEUE_PORT))
    conn = Client(address, authkey = AUTHKEY)
    conn.send(item)
    conn.close()

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
	    msg += 'Name '
	if rawDict['description']=='':
	    rawDict['description'] = 'No Discription'
	if rawDict['capabilities']=='':
	    rawDict['capabilities'] = '<vNode/>'
	if rawDict['os_type']=='':
	    msg += 'OSType '
	if rawDict['distribution']=='':
	    msg += 'Distribution '
	if rawDict['release']=='':
	    msg += 'Release '
	if rawDict['kernel']=='':
	    msg += 'Kernel '
	if rawDict['packages']=='':
	    rawDict['packages'] = 'base-files'
	if rawDict['repository']=='':
	    rawDict['repository'] = 'local'
	if rawDict['memory'] == 0:
	    msg += 'Memory '
	if rawDict['disk'] ==0 :
	    msg += 'Disk '
	if rawDict['newconfig']=='':
	    rawDict['newconfig'] = 'something'
	if rawDict['deploy_method']=='':
	    rawDict['deploy_method'] = 'nfsmount'
	if rawDict['deploy_url']=='':
	    msg += 'DeployUrl '
	if rawDict['cowdir']=='':
	    msg += 'COWDir '
        if msg != '':
            msgDict = rawDict.copy()
            msgDict['msg']=msg+"need to be corrected!"
            msgDict['username']= user.username
            return render(request,'add.html',msgDict)
        filename = hashFilename(rawDict)
        if exsit(filename):
            msg = 'Failed to create new template. You perhaps have created a same template.'
            msgDict = rawDict.copy()
            msgDict['msg'] = msg
            msgDict['username'] = user.username
            return render(request, 'add.html', msgDict)
        else:
            new_template = createNew(rawDict,filename)
            if new_template is not None:
                redirect_url = "../profile/"+user.username+"/template/"+filename+"/"
                return HttpResponseRedirect(redirect_url)
            else:
                msg = 'Failed to create new template.'
                msgDict = rawDict.copy()
                msgDict['msg'] = msg
                msgDict['username'] = user.username
                return render(request, 'add.html', msgDict)
    else:
        t = get_template('add.html')
        return render(request, 'add.html', {'username':user.username,'deploy_method':'nfsmount','packages':'base-files','capabilities':'<vNode/>','repository':'local','newconfig':'something'
})

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
@csrf_exempt
def tpreq(request, username, tp):
    user = request.user
    if request.method == 'POST':

        sessionid = request.COOKIES.get('sessionid')
        method = request.POST.get('method')
        template = request.POST.get('template')
        redis_publisher = RedisPublisher(facility='foobar', sessions=[sessionid])
        message = RedisMessage("1")# 1 Request Recieved
        redis_publisher.publish_message(message)
        msg = {'method':method,'sessionid':sessionid,'template':template}
        try:
            sentToQueue(msg)
        except Exception,e:
            print e
        return HttpResponse('OK')
    else:
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
