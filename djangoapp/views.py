from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from vmtemplates.models import VMTemplate
from vmtemplates import verification
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher
from djangoapp.settings import *
from djangoapp.vmtemplates.utils import *
import thread

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
        if msg != '':
            msgDict = rawDict.copy()
            msgDict['msg']=msg+"need to be corrected!"
            msgDict['username']= user.username
            msgDict['vstores'] = VSTORES
            msgDict['methods'] = METHODS
            images = getImages()
            msgDict['images'] = images
            return render(request,'add.html',msgDict)
        urls = makeUrl(rawDict['deploy_method'], rawDict['deploy_vstore'])
        rawDict['deploy_url'] = urls['deploy_url']
        rawDict['cowdir'] = urls['cowdir']
        filename = hashFilename(rawDict)
        rawDict['deploy_url'] += filename +'.img'
        if exsit(filename):
            msg = 'Failed to create new template. You perhaps have created a same template. Give different description to differentiate them.'
            msgDict = rawDict.copy()
            msgDict['msg'] = msg
            msgDict['username'] = user.username
            msgDict['vstores'] = VSTORES
            msgDict['methods'] = METHODS
      	    images = getImages()
            msgDict['images'] = images
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
                msgDict['vstores'] = VSTORES
                msgDict['methods'] = METHODS
        	images = getImages()
                msgDict['images'] = images
                return render(request, 'add.html', msgDict)
    else:
        t = get_template('add.html')
        images = getImages()
        return render(request, 'add.html', {'images':images,'username':user.username,'methods':METHODS, 'vstores':VSTORES,'deploy_method':'nfsmount','packages':'base-files','capabilities':'<vNode/>','repository':'local','newconfig':'something'
})

@login_required
def delete(request, username, tp):
    user = request.user
    if username != user.username:
        return render(request, 'showdenied.html', { 'username':username })
    try:
        template = VMTemplate.objects.get(create_user=user, filename = tp)
        localFilePath = os.path.join(LOCAL_XML_DIR, tp+'.xml')
        url = template.deploy_url
        if template.deploy_method == 'nfsmount':
            end = url[6:].find('/')
            server = url[6:6+end]
        remoteFilePath = '/var/lib/ivic/vstore/nfsbase/' + tp + '.img'
        delLocal(localFilePath)
        template.delete()
        # Use nfs, no need to delete remote file
        # thread.start_new_thread(delRemote,(remoteFilePath,server, 22, VSTORE_USERNAME, VSTORE_PASSWD))

        # delete image
        thread.start_new_thread(delRemote,(remoteFilePath,server, 22, VSTORE_USERNAME, VSTORE_PASSWD))
        return HttpResponseRedirect('../../../../')
    except Exception, e:
        print e
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
            sessionid = request.COOKIES.get('sessionid')
            redis_publisher = RedisPublisher(facility='foobar', sessions=[sessionid])
            message = RedisMessage("0")# 0
            redis_publisher.publish_message(message)
            template = VMTemplate.objects.get(create_user=user, filename = tp)
            return render(request, 'tpreq.html',{'username':username,'template':template})
        except Exception,e:
            print e
            return render(request, 'showdenied.html',{'username':username})

def signup(request):
   if request.method == 'POST':
      return verification.register(request)
   else:
      return render(request,'signup.html')
