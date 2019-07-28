#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for /koncept/
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse

from datetime import datetime
from myutils.myutils import paginator_helper

from koncepts.models import *
from koncepts.forms import *
from settings import printdebug, BOOTSTRAP





@login_required
def delete_fragment(request):
	"""
	Delete a fragment attached to a koncept
	
	November 17, 2015:
	updated so that subjects are used instead of tags
	
	February 15, 2015:
	Updated and simplified. Fragments are deleted in isolation, without touching 
	any other objects. Only tags are checked for cascade deletion. 
	
	February 21, 2014:
	The related koncept is deleted only if the koncept is an orphan
	If the related source is an orphan, it gets deleted too.
	
	June 27, 2014
	islinked : flag to differentiate from delete on fragments+intfrags from single fragments

	"""
	fragment_id = request.GET.get('fid', None)
	return_page = request.GET.get('page', None)  # not implemented in front end yet
	document, old_document_id = None, None
	user = request.user 
	
	fragment = get_object_or_404(Fragment, pk=int(fragment_id), created_by=user)
	
	if fragment.source:
		old_document_id = fragment.source.id
	old_subjects = list(fragment.subjects.all())
	
	fragment.source = None
	fragment.subjects.clear()	
	for intfrag in fragment.intfrag_set.all():  # remove associations to koncepts
		intfrag.delete()
	# finally:
	fragment.delete()
	printdebug("===Deleted=== fragment %s" % fragment_id)
	
	# clean up relations
	Subject.cleanUpUserSubjects(user, old_subjects)	
	if old_document_id:
		document = Document.objects.get(pk=old_document_id)
		document.cleanOrdering()
	
	_message = "Delete operation successfull."		
	messages.success(request, _message)
	if document:
		return HttpResponseRedirect(reverse('get_document' , args=(user.username, document.id)))
		# return HttpResponseRedirect('%s' % document.get_absolute_url()) 
	else:
		return HttpResponseRedirect(reverse('search_user_quotes' , args=(user.username,)))






@login_required
def unlink_fragment(request):
	"""
	Unlinks a fragment from the interpretation is linked to. 
	Note: this is done by passing just the intfrag_id - as there is only 
	one fragment associated to it
	"""
	intfrag_id = request.GET.get('intfrag_id', 0)
	user = request.user 
	
	intfrag = get_object_or_404(IntFrag, pk=int(intfrag_id), created_by=user)

	koncept = intfrag.koncept
	intfrag.delete()

	koncept.cleanIntFragOrdering() # March 21, 2014: ensure ordering is sequential
			
	_message = "Remove operation successfull."	
	redirect_url = 	'%s' % koncept.get_absolute_url()		
	messages.success(request, _message)
	return HttpResponseRedirect(redirect_url)









@login_required
def delete_koncept(request):
	"""
	Deletes a collection [koncept] without touching its related fragments
	"""

	kon_id = request.GET.get('kon_id', 0)
	user = request.user 
	koncept = get_object_or_404(Koncept, pk=int(kon_id), created_by=user)

	for intfrag in koncept.intfrag_set.all():
		intfrag.delete()

	koncept.delete()
	_message = "Delete operation successfull."		
	messages.success(request, _message)
	return HttpResponseRedirect(reverse('search_user_koncepts' , args=(user.username,)))
	# return HttpResponseRedirect('/')








@login_required
def delete_document(request):
	"""
	Delete a document
	
	February 21, 2014: related content isn't touched at all
	"""
	document_id = request.GET.get('document_id', 0)
	user = request.user ## in the future we'll have to handle username too
	document = get_object_or_404(Document, pk=int(document_id), created_by=user)


	for fragment in document.fragment_set.all():
		fragment.source = None
		fragment.save()

		
	# finally
	document.delete()
	
	_message = "Delete operation successfull."		
	messages.success(request, _message)
	
	return HttpResponseRedirect(reverse('search_user_quotes' , args=(user.username,)))








