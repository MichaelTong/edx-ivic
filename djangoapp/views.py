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
def template(request, tp):
    try:
        user = request.user
        template = VMTemplate.objects.get(filename = tp, create_user = user)
        return render_to_response('showtemplate.html',{'template':template,'username':user.username})
    except:
        return render_to_response('showdenied.html',{'username':user.username})

@login_required
def add(request):
    if request.method == 'POST':
        rawDict = loadFromRequest(request)
        filename = hashFilename(rawDict)
        print rawDict
        new_template = createNew(rawDict,filename)
        redirect_url = "../template/"+filename+"/"
        return HttpResponseRedirect(redirect_url)
    else:
        user = request.user
        t = get_template('add.html')
        return render(request, 'add.html', {'username':user.username,'deploy_method':'nfsmount','node_type':'undefined','capabilities':'vNode'})
    
def signup(request):
   if request.method == 'POST':
      return verification.register(request)
   else:
      return render(request,'signup.html')
