#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for NEW and EDIT actions	 - created on 9Feb2013
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from datetime import datetime
from myutils.myutils import paginator_helper

from koncepts.models import *
# from koncepts.tag import get_tag_cloud
from koncepts.forms import *
from settings import printdebug, BOOTSTRAP





@login_required
def new_quote(request):
	"""
		View that handles the creation form at /actions/create/
		
			NOTE that this is also used for EDITING - via GET params.
		
		Koncept name is unique within a user
		Document title is unique within a user
		Tags must be user specific too [2015-02-14]
		
	"""
	
	user = request.user
	cancel_url = None

	# template-based creation eg for edit

	try:
		source_id = int(request.GET.get('source', False))
	except:
		source_id = None		
	try:
		fragment_id = int(request.GET.get('fragment', False))
	except:
		fragment_id = None	
	
					
	searchdict = {'created_by' : user}
	# recentKoncepts = Koncept.objects.filter(**searchdict).distinct().order_by("-updated_at")[:6]
	# recentDocuments = Document.objects.filter(**searchdict).distinct().order_by("-updated_at")[:6]
	#
						
	if request.method == 'POST': 
		
		# 
		# add action: process a submitted form						
		#
		
		f1 = _processForm(request, user, fragment_id)
		
		if f1:
			return HttpResponseRedirect('%s' % (f1.get_absolute_url()))

		else:
			# there's an error, return the form
			context = {	  
						'form' : NewQuoteForm(request.POST),
						'person' : user, 
						'usertags' : [t.name for t in Subject.subjectsListPerUser(user)],
						# 'recentKoncepts' : recentKoncepts,
						# 'recentDocuments' : recentDocuments,
						'increaseDocument' : source_id, 
						'increaseFragment' : fragment_id, 
						'cancel_url' : cancel_url,
						'page_flag' : 'new',
						}			
	else:
		
		# 
		# create the form (based on templates, if existing)					
		#	

		form = NewQuoteForm()
		defaultPrivate = user.userprofile.defaultPrivateKoncepts
		

		if source_id:
			try: 
				# check if a template needs to be used
				source = Document.objects.get(pk=source_id, created_by=user)
				form = _prePopulateForm(source=source, fragment=None, isprivate=defaultPrivate)
				cancel_url = source.get_absolute_url()
			except:
				source_id = None

		elif fragment_id:

			try: 
				# check if a template needs to be used
				fragment = Fragment.objects.get(pk=fragment_id, created_by=user)
				source = fragment.source
				tags = fragment.subjects.all() # named 'tags' for backward compatibility

				form = _prePopulateForm(source=source, fragment=fragment, tags=tags, isprivate=fragment.isprivate)
				cancel_url = fragment.get_absolute_url()
			except:
				fragment_id = None
				
		else:
			form = NewQuoteForm(initial={'isprivate' : defaultPrivate})
			
			


		context = {	  
					'form' : form,
					'person' : user, 
					# hack: in order to make select2 autocomplete work, we gotta put the autocomplete material on the page..
					'usertags' : [t.name for t in Subject.subjectsListPerUser(user)],
					# 'recentKoncepts' : recentKoncepts,
					# 'recentDocuments' : recentDocuments,
					'increaseDocument' : source_id, 
					'increaseFragment' : fragment_id, 
					'cancel_url' : cancel_url,
					'page_flag' : 'new',
					}

	return render_to_response(BOOTSTRAP + 'pages/koncept_new.html', 
							context,
							context_instance=RequestContext(request))







@login_required
def addonthefly(request):
	"""
	Add a new koncept using the bookmarklet 
	
	Inner method called is the same as in new.py
	"""
	user = request.user ## in the future we'll have to handle username too
	context = {'addonthefly' : True} # flag for template

	searchdict = {'created_by' : user}
	# recentKoncepts = Koncept.objects.filter(**searchdict).distinct().order_by("-updated_at")[:6]
						
	if request.method == 'POST': 
		
		# 
		# add action: process a submitted form						
		#
		
		f1 = _processForm(request, user)
		
		if f1:
			context.update({ 'fragment' : f1 })
		else:
			# there's an error, return the form
			context.update({	  
							'form' : NewQuoteForm(request.POST),
							'usertags' : [t.name for t in Subject.subjectsListPerUser(user)],
							# 'recentKoncepts' : recentKoncepts, 
							})	
						
	else:
		
		# 
		# create the form						
		#	
	
		text = request.GET.get('text', "unavailable") 
		title = request.GET.get('title', "unavailable") 
		url = request.GET.get('url', "unavailable") 
		
		defaultPrivate = user.userprofile.defaultPrivateKoncepts
		
		form = NewQuoteForm(initial={'text' : text, 'sourcetitle' : title, 'sourceurl' : url, 'isprivate' : defaultPrivate})	

		context.update({	  
						'form' : form,
						'usertags' : [t.name for t in Subject.subjectsListPerUser(user)],
						# 'recentKoncepts' : recentKoncepts, 
						})


	return render_to_response(BOOTSTRAP + 'components/addonthefly.html', 
								context,
								context_instance=RequestContext(request))









# ---------------------------------


#  Inner methods


# ---------------------------------





def _prePopulateForm(source=None, fragment=None, tags=None, isprivate=False):
	"""
		Adds existing fields to a form
	"""
	
	dict1 = {}
	try:
		
		dict1['isprivate'] = isprivate
		
		if source:
			dict1['sourcetitle'] = source.title
			dict1['sourceurl'] = source.url
			dict1['sourceauthor'] = source.author
			dict1['sourcedesc'] = source.description
			dict1['sourcepubyear'] = source.pubyear

		if fragment:
			dict1['text'] = fragment.text
			dict1['title'] = fragment.title
			dict1['location'] = fragment.location
			dict1['comment'] = fragment.comment
						
		if tags:
			dict1['tags'] = ", ".join([i.name for i in tags.all()]) 
			
		# print dict1

		return NewQuoteForm(initial=dict1)	

	except:
		return NewQuoteForm(initial={'title' : "Sorry: an error prevented loading the data"})









def _processForm(request, user, fragment_id=None):
	"""
	Creates quotes based on form data
	Used by both for new and addOnTheFly views
	
	fragment_id: for edit operations
		 		(for sources the title is used to identify preexisting stuff)
	TAGS: tags are linked to the fragment directly
				 
	"""
	d1, f1, tags = None, None, None

	form = NewQuoteForm(request.POST)	 #instance=interpretation

	if form.is_valid():
		
		# GET FRAGMENT obj if possible (and update text too)
		
		if fragment_id:
			f1 = get_object_or_404(Fragment, pk=fragment_id, created_by=user)
			f1.text = form.cleaned_data['text']
			f1.title = form.cleaned_data['title']
			f1.comment = form.cleaned_data['comment']
			f1.location = form.cleaned_data['location']
			f1.isprivate=form.cleaned_data['isprivate']
		else:
			f1 = Fragment(text=form.cleaned_data['text'], title=form.cleaned_data['title'], comment=form.cleaned_data['comment'], isprivate=form.cleaned_data['isprivate'], location=form.cleaned_data['location'], created_by=user)
			

		# GET DOCUMENT , add a source - otherwise the fragment will have Source=None
		
		if form.cleaned_data['sourcetitle']:
			try:
				# reuse a source with exact same data, if available [= the autocompletion should make all data surface]
				d1 = Document.objects.get(title=form.cleaned_data['sourcetitle'], created_by=user)
				
				# overwrite if anything's changed
				if d1.author != form.cleaned_data['sourceauthor'] or d1.description != form.cleaned_data['sourcedesc'] or d1.pubyear!=form.cleaned_data['sourcepubyear'] or d1.url != form.cleaned_data['sourceurl']:
					d1.author = form.cleaned_data['sourceauthor']
					d1.description = form.cleaned_data['sourcedesc'] 
					d1.pubyear=form.cleaned_data['sourcepubyear']
					d1.url = form.cleaned_data['sourceurl']
					d1.save()		
							
			except:	 
				# if title isn't already existing, create new Document 
				
				d1 = Document(title=form.cleaned_data['sourcetitle'], author=form.cleaned_data['sourceauthor'],
				 description=form.cleaned_data['sourcedesc'], pubyear=form.cleaned_data['sourcepubyear'], url=form.cleaned_data['sourceurl'], 
					created_by=user)	
				d1.save()		


		# ADD SOURCE (OR NONE) TO THE FRAGMENT 

		f1.source = d1
		f1.save()

		
		# clear tags and recreate them
		old_subjects = list(f1.subjects.all())
		f1.subjects.clear()			
		if form.cleaned_data['tags']:
			for el in form.cleaned_data['tags'].strip().split(","):
				if el:
					# NOTE: using `Subject.objects.get_or_create` throws an error
					try:
						subject = Subject.objects.get(name=el.strip().lower(), created_by=user)
					except:
						subject = Subject(name=el.strip().lower(), created_by=user)
						subject.save()
					f1.subjects.add(subject)
		
		Subject.cleanUpUserSubjects(user, old_subjects)		

		# FINALLY 
		return f1 

	else: # if form is not valid
		return False















