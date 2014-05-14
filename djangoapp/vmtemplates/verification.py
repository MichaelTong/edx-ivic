from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import auth
import json

def check_username(request):
	if request.method == 'GET':
		try:
			user = User.objects.get(username = request.GET['username']);
			if user is not None:
				return HttpResponse(json.dumps({'msg':'Username existed'}))
		except:
			return HttpResponse(json.dumps({'msg':'Username availiable'}))

def register(request):
	if request.method == 'GET':
		username = request.GET['username']
		password = request.GET['password']
		rpassword = request.GET['rpassword']
		email = request.GET['email']
		if password != rpassword:
			return HttpResponse(json.dumps({'msg':'Two passwords do not match'}))
		user = User.objects.create_user(username, email, password)
		if user is not None:
			user.save()
			return HttpResponse(json.dumps({'msg':'ok'}))
		else:
			return HttpResponse(json.dumps({'msg':'Sign up failed'}))

def signin(request):
	username = request.GET['username']
	password = request.GET['password']
	user = auth.authenticate(username = username, password = password)
	if user is not None:
		if user.is_active:
			auth.login(request, user)
			return HttpResponseRedirect("../profile/")
		else:
			return HttpResponse(json.dumps({'msg':'User is not active'}))
	else:
		return HttpResponse(json.dumps({'msg':'Sign in failed'}))

