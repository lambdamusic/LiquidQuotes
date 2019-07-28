#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for the autocomplete mechanisms
#
##################


"""
from django.utils import simplejson

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required

from koncepts.models import *
from settings import printdebug, BOOTSTRAP





# ===========
# koncepts
# ===========



@login_required
def autocomplete_koncepts(request):
	"""
	View that supports the boostrap typeahead widget. Returns a list of Koncept names.
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []
	if request.method == "GET":
		if request.GET.has_key(u'term'):
			value = request.GET[u'term']
			model_results = Koncept.objects.filter(name__icontains=value, created_by=user)[:30]
			results = [ x.name for x in model_results ]	
			# results = [ {'name': x.name, 'id': x.id} for x in model_results ]	
			json = simplejson.dumps(results)
			return HttpResponse(json, mimetype='application/json')
	return HttpResponse("")



@login_required
def autocomplete_koncept_details(request):
	"""
	view that adds the extra info for a koncept after the autocomplete succeeds (2nd ajax call)
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []
	if request.method == "GET":
		if request.GET.has_key(u'title'):
			value = request.GET[u'title']
			model_results = Koncept.objects.filter(name=value, created_by=user)
			if len(model_results) == 1:
				results = { 'link' : model_results[0].get_absolute_url(), 'fragcount' : model_results[0].intfrag_set.count()  } 
				# print results
				json = simplejson.dumps(results)
				return HttpResponse(json, mimetype='application/json')
			else:
				printdebug("*koncept_details* : More than one koncept with same name, so failing silently: %s" % value)
				return HttpResponse("")

	return HttpResponse("")




	# ===========
	# documents
	# ===========



@login_required
def autocomplete_sources(request):
	"""
	View that supports the boostrap typeahead widget. Returns a list of Document names and ids
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []
	if request.method == "GET":
		if request.GET.has_key(u'term'):
			value = request.GET[u'term']
			model_results = Document.objects.filter(title__icontains=value, created_by=user)[:30]
			# results = [ x.title for x in model_results ]	
			results = [ { 'id': x.id, 'title': x.title} for x in model_results ]	
			# print results
			json = simplejson.dumps(results)
			return HttpResponse(json, mimetype='application/json')
	return HttpResponse("")



@login_required
def autocomplete_source_details(request):
	"""
	view that adds the extra info for a source after a title-autocomplete succeeds (2nd ajax call)
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []
	if request.method == "GET":
		if request.GET.has_key(u'title'):
			value = request.GET[u'title']
			model_results = Document.objects.filter(title=value, created_by=user)
			if len(model_results) == 1:
				results = { 'url': model_results[0].url, 'desc': model_results[0].description, 'author': model_results[0].author,   'pubyear': model_results[0].pubyear, 'link' : model_results[0].get_absolute_url() , 'koncount' : len(model_results[0].get_koncepts())  } 
				# print results
				json = simplejson.dumps(results)
				return HttpResponse(json, mimetype='application/json')
			else:
				printdebug("*source_details* : More than one source with same name, so failing silently: %s" % value)
				return HttpResponse("")

	return HttpResponse("")






# ===========
# tags
# 2016-07-31: disabled totally
# ===========



	
@login_required
def autocomplete_tags(request):
	"""
	tags [2015-02-15: not used anywhere]
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []
	if request.method == "GET":
		if request.GET.has_key(u'term'):
			value = request.GET[u'term']
			model_results = Subject.objects.filter(name__icontains=value, created_by=user)[:30]  #created_by=user
			results = [ x.name for x in model_results ]	
			json = simplejson.dumps(results)
			return HttpResponse(json, mimetype='application/json')
	return HttpResponse("")


