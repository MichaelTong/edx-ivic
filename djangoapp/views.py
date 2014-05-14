from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from vmtemplates.models import VMTemplate

def home(request):
	return render_to_response('home.html')

def profile(request):
	limit = 10
	templates = VMTemplate.objects.all()
	paginator = Paginator(templates, limit)
	page = request.GET.get('page')
	try:
		templates = paginator.page(page)
	except PageNotAnInteger:
		templates = paginator.page(1)
	except EmptyPage:
		templates = paginator.page(paginator.num_pages)

	return render_to_response('profile.html',{'templates':templates})

def template(request, tp):
	template = VMTemplate.objects.get(id = tp)
	return render_to_response('showtemplate.html',{'template':template})

def signup(request):
	return render_to_response('signup.html')
