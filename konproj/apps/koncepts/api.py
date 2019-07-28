#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	API views
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.utils.html import strip_tags, escape
from django.utils import simplejson

from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator, InvalidPage, EmptyPage
# from django.db.models import Q
# from myutils.myutils import paginator_helper, split_list

from koncepts.models import *
from settings import printdebug, BOOTSTRAP





def apisearch(request):
	"""
	
	November 17, 2014: simple JSON api for returning list of koncepts
	
	"""
	
	# get init values
	searchdict = {}
	searchval = request.GET.get('q', "") 
	user = request.GET.get('u', None) 
	sort_var = request.GET.get('sort', 'created')

	if sort_var not in ['alpha', 'modified', 'created']: sort_var = 'created'
	sorting = {'alpha' : ["name", "-updated_at"], 
				'modified': ["-updated_at", "name"], 
				'created': ["-created_at", "name"]} [sort_var]	

	# we dont care about user for now
	
	if searchval:
		searchdict['name_url__icontains'] = url_encode(searchval)
	
	if True:
		# eventually we'll provide support for logged in users
		searchdict['intfrag__fragment__isprivate'] = False
	
	qset = Koncept.objects.filter(**searchdict).distinct().order_by(*sorting)[:20]

	data = []
	
	host = request.get_host()
	if not host.startswith("127.0.0.1"):
		host = "http://" + host
	
	for el in qset:
		d = {}
		d['id'] = el.id
		d['name'] = el.name
		d['url'] = host + el.get_absolute_url()
		data += [d]
	
	data = simplejson.dumps(data)
	return HttpResponse(data, mimetype='application/json')


