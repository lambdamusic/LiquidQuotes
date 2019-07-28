#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for /tag/  - created on 9Feb2013
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.db.models import Count


from myutils.myutils import paginator_helper

from koncepts.models import *

from settings import printdebug, BOOTSTRAP





# April 3, 2014: moved this into registration/models.py

@login_required
def get_tag_cloud(request):
	"""
	
	"""
	user = request.user

	if Tag.objects.filter(created_by=user).count() > 15: 
		tags = Tag.objects.filter(created_by=user).annotate(count=Count('fragment')).filter(count__gt=2)
	else:
		tags = Tag.objects.filter(created_by=user).annotate(count=Count('fragment'))
	
	return tags



			








# April 3, 2014: not used anymore as we do not have tag pages

#
# @login_required
# def get_tag(request, username, tag_name=""):
# 	"""
# 	"""
# 	user = request.user
#
# 	if not user.username == username:  ## TODO: handle username too
# 		return render_to_response('401.html', {}, context_instance=RequestContext(request))
#
# 	try:
# 		page = int(request.GET.get('page', '1'))
# 	except ValueError:
# 		page = 1
# 	sort_var = request.GET.get('sort', 'date')
# 	if sort_var not in ['alpha', 'creationdate',]: sort_var = 'date'	 # default sort value
# 	sorting = {'alpha' : ["name", "-updated_at"],
# 				'date': ["-updated_at", "name"]} [sort_var]
#
#
# 	# search
# 	t1 = get_object_or_404(Tag, name_url=url_encode(tag_name))
# 	qset = t1.intfrag_set.filter(created_by=user)
#
#
#
# 	# set up pagination
# 	paginator = Paginator(qset, 15)
# 	try:
# 		page_object = paginator.page(page)
# 	except (EmptyPage, InvalidPage):  # If page request is out of range, deliver last page of results.
# 		page_object = paginator.page(paginator.num_pages)
# 	page_object.extrastuff = paginator_helper(page, paginator.num_pages)
# 	page_object.totcount = paginator.count
#
#
# 	# finally...
# 	context = {
# 				't1' : t1,
# 				'page_object' : page_object,
# 				'sort_var' : sort_var,
# 				'tagscloud' : get_tag_cloud(request)
# 				}
# 	return render_to_response('koncepts/pages/tag_detail.html',
# 							context,
# 							context_instance=RequestContext(request))
#
#
#









