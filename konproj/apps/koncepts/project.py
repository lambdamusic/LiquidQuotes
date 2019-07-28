#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for /quote/	 - created on 2014-10-17
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils import simplejson
from django.core.urlresolvers import reverse

from myutils.myutils import paginator_helper

from koncepts.models import *
from settings import printdebug, BOOTSTRAP




@login_required
def addProject(request):
	"""
	ajax call
	create a new project (collection) for a user
	"""
	user = request.user
	results = { 'error': "Sorry, this name is already taken or invalid (only numbers and letters are accepted)" }
	
	try:
		userid = int(request.GET.get('userid', False))
		person = get_object_or_404(User, id=userid)
	except:
		return HttpResponseForbidden()
	
	if user.id != person.id:
		return HttpResponseForbidden()	
	try:
		newname = request.GET.get(u'name', False)
	except:
		newname = ""
		

	if newname.replace(" ", "").isalnum():
						
		# reuse a koncept with exact same name, if available
		
		p1 = Project.objects.filter(name_url=nice_url_name(newname), created_by=person)
		if p1:
			pass
		else:
			p1 = Project(created_by=person, name=newname)
			p1.save()	

			results = { 'saved_url': p1.get_absolute_url(), }				
			

	json = simplejson.dumps(results)
	# print json
	return HttpResponse(json, mimetype='application/json')







@login_required
def editProject(request):
	"""
	ajax call
	edit a new project (collection) for a user
	"""
	user = request.user
	results = { 'error': "Sorry, this name is already taken or invalid (only numbers and letters are accepted)" }
	
	try:
		coll_id = int(request.GET.get('coll_id', False))
		p1 = get_object_or_404(Project, id=coll_id, created_by=user)
	except:
		return HttpResponseForbidden()
	
	try:
		newname = request.GET.get(u'name', False)
	except:
		newname = ""
		

	if newname.replace(" ", "").isalnum():
						
		# reuse a koncept with exact same name, if available
		
		test = Project.objects.filter(name_url=nice_url_name(newname), created_by=user)
		if test:
			pass
		else:
			p1.name=newname
			p1.save()	

			results = { 'saved_url': p1.get_absolute_url(), }				
			

	json = simplejson.dumps(results)
	# print json
	return HttpResponse(json, mimetype='application/json')
	
	
	
	


@login_required
def deleteProject(request):
	"""
	ajax call
	delete a new project (collection) for a user
	all items in project are disattached but not deleted
	"""
	user = request.user
	results = { 'error': "Sorry, this name is already taken or invalid (only numbers and letters are accepted)" }

	try:
		coll_id = int(request.GET.get('coll_id', False))
		p1 = get_object_or_404(Project, id=coll_id, created_by=user)
	except:
		return HttpResponseForbidden()


	p1.koncepts.clear()
	p1.fragments.clear()
	p1.delete()
	
	_message = "Delete operation successfull."		
	messages.success(request, _message)
	return HttpResponseRedirect(reverse('search_user_koncepts' , args=(user.username,)))




@login_required
def addKoncept2Project(request):
	"""
	ajax call
	adds a koncept to the project
	
	"""
	user = request.user
	results = { 'error': "Sorry, this name is already taken or invalid (only numbers and letters are accepted)" }

	# print kon_id
	
	fieldname = request.POST.get('name', False)
	kon_pk = request.POST.get('pk', False)
	collection_pks = request.POST.getlist('value[]')

	print fieldname, kon_pk, collection_pks
	
	try:
		k1 = get_object_or_404(Koncept, id=int(kon_pk), created_by=user)
	except:
		return HttpResponseBadRequest("Ops.. cannot update at this time.")
	
	# try:
	new_collections = []
	for x in collection_pks:
		temp = Project.objects.get(id=int(x), created_by=user)
		print temp
		new_collections += [temp]
	# except:
	# 	return HttpResponseBadRequest("Ops.. cannot update at this time.")
	
	# first clear, then add 
	k1.project_set.clear()		
	for proj in new_collections:
		proj.koncepts.add(k1)
	return HttpResponse("Success.")
						
	# collections = [get_object_or_404(Project, id=coll_id, created_by=user) for coll_id in collection_pks]
	# # print request.POST
	# # try:
	# # 	coll_id = int(request.GET.get('coll_id', False))
	# # 	p1 = get_object_or_404(Project, id=coll_id, created_by=user)
	# # except:
	# # 	return HttpResponseForbidden()
	#
	# if False:
	# 	return HttpResponse("Success.")
	# else:
	# 	return HttpResponseBadRequest("Ops.. cannot update at this time.")

	# p1.koncepts.clear()
	# p1.fragments.clear()
	# p1.delete()
	#
	# _message = "Delete operation successfull."
	# messages.success(request, _message)
	# return HttpResponseRedirect(reverse('search_user_koncepts' , args=(user.username,)))

