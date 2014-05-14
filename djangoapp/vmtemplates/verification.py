from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import auth
import json

def check_username(request):
   if request.method == 'GET':
      username = request.GET.get('username','')
      if username == '':
          return HttpResponse(json.dumps({'msg':'Username invalid'}))
      try:
         user = User.objects.get(username = username)
         if user is not None:
            return HttpResponse(json.dumps({'msg':'Username existed'}))
      except:
         return HttpResponse(json.dumps({'msg':'Username availiable'}))

def register(request):
    print request
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        rpassword = request.POST.get('rpassword','')
        email = request.POST.get('email','')
        if username == '':
            return render(request,'signup.html',{'msg':'Invaild username'})
        if password != rpassword:
            return render(request,'signup.html',{'msg':'Two passwords do not match','username':username})
        user = User.objects.create_user(username, email, password)
        if user is not None:
            user.save()
            return HttpResponseRedirect("../")
        else:
            return render(request,'signup.html',{'msg':'Sign up failed','username':username})

def signin(request):
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    user = auth.authenticate(username = username, password = password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect("../profile/")
        else:
            return render(request,'home.html',{'msg':'User is not active','username':username})
    else:
        return render(request,'home.html',{'msg':'Sign in failed','username':username})


def signout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")
