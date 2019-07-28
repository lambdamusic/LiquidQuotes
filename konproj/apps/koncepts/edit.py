#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for EDIT actions - mostly the ajax ones as NEW.py handles many edit actions too 
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from datetime import datetime

from myutils.myutils import paginator_helper
from myutils.template import render_block_to_string

from django.utils import simplejson

from koncepts.models import *
# from koncepts.tag import get_tag_cloud
from koncepts.forms import *
from settings import printdebug, BOOTSTRAP
from context_processors import which_labels









# ===========
# Functions that apply to all object types
# ===========





@login_required
def make_fragment_private(request):
	"""
	View that changes the public/private status of a fragment
	Normally called via ajax
	
	Accepts 3 kind of params:
	frag_id: switches a specific quote
	kon_id: indicate whether a koncept + all quotes linked to it  should be switched
	doc_id: the global one for documents + all quptes
	
	March 4, 2015: koncepts and documents privacy is changed too
	 
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []
	if request.method == "GET":
		
		# 1) change public/private for a specific FRAGMENT
		
		if request.GET.has_key(u'frag_id'):
				
			value = request.GET[u'frag_id']

			try: 
				fragment = Fragment.objects.get(pk=int(value), created_by=user)
			except:
				return HttpResponseForbidden()
						
			if fragment.isprivate:
				fragment.isprivate = False
				results = { 'private': 'false' } 
			else:
				fragment.isprivate = True
				results = { 'private': 'true' } 
			fragment.save()
						
			# print results
			json = simplejson.dumps(results)
			return HttpResponse(json, mimetype='application/json')
			# except:
			#	pass
		
		
		
		# 2) change public/private for a specific KONCEPT
		
		
		if request.GET.has_key(u'kon_id'):
			
			# change public/private for all fragments attached to koncept (seeded randomly based on firt intfrag available)
			value = request.GET[u'kon_id']
			privacy = request.GET[u'privacy']  # 1=Public 0=Private
			if not privacy:
				privacy = 0	 #defaults to private=True			
			privacy = not(bool(int(privacy)))
				
			try: 
				k = Koncept.objects.get(pk=int(value), created_by=user)
				k.isprivate = privacy
				k.save()
			except:
				return HttpResponseForbidden()
		
			fragments = Fragment.objects.filter(intfrag__koncept=k)
			
			
			
			for f in fragments:					
				f.isprivate = privacy
				f.save()
			results = { 'private': str(privacy) }
					
			# print results
			json = simplejson.dumps(results)
			return HttpResponse(json, mimetype='application/json')
			# except:
			#	pass




		# 3) change public/private for a specific DOCUMENT
		
		
		if request.GET.has_key(u'doc_id'):
			
			# change public/private for all fragments attached to koncept (seeded randomly based on firt intfrag available)
			value = request.GET[u'doc_id']
			privacy = request.GET[u'privacy']  # 1=Public 0=Private
			if not privacy:
				privacy = 0	 #defaults to private=True			
			privacy = not(bool(int(privacy)))

			try: 
				d = Document.objects.get(pk=int(value), created_by=user)
				d.isprivate = privacy
				d.save()
			except:
				return HttpResponseForbidden()
						
			fragments = Fragment.objects.filter(source=d)

			for f in fragments:					
				f.isprivate = privacy
				f.save()
			results = { 'private': str(privacy) }			
						
			# print results
			json = simplejson.dumps(results)
			return HttpResponse(json, mimetype='application/json')
			# except:
			#	pass
			
			
			
	return HttpResponse("")










# ===========
# Quote
# ===========





@login_required
def make_fragment_clipboard(request):
	"""
	View that changes the pinned/unpinned status of a fragment
	Normally called via ajax
	
	2015-11-27: added
	 
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []
	if request.method == "GET":
		
		# 1) change public/private for a specific FRAGMENT
		
		if request.GET.has_key(u'frag_id'):
				
			value = request.GET[u'frag_id']

			try: 
				fragment = Fragment.objects.get(pk=int(value), created_by=user)
			except:
				return HttpResponseForbidden()
						
			if fragment.clipboard:
				fragment.clipboard = False
				results = { 'clipboard': 'false' } 
			else:
				fragment.clipboard = True
				results = { 'clipboard': 'true' } 
			fragment.save()
						
			# print results
			json = simplejson.dumps(results)
			return HttpResponse(json, mimetype='application/json')
			# except:
			#	pass

			
	return HttpResponse("")








@login_required
def make_fragment_favorite(request):
	"""
	View that changes the favorite status of a fragment
	Normally called via ajax
	
	2015-11-27: added 
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []
	if request.method == "GET":
		
		# 1) change public/private for a specific FRAGMENT
		
		if request.GET.has_key(u'frag_id'):
				
			value = request.GET[u'frag_id']

			try: 
				fragment = Fragment.objects.get(pk=int(value), created_by=user)
			except:
				return HttpResponseForbidden()
						
			if fragment.favorite:
				fragment.favorite = False
				results = { 'favorite': 'false' } 
			else:
				fragment.favorite = True
				results = { 'favorite': 'true' } 
			fragment.save()
						
			# print results
			json = simplejson.dumps(results)
			return HttpResponse(json, mimetype='application/json')
			# except:
			#	pass

			
	return HttpResponse("")











@login_required
def edit_quote_title(request):
	"""
	Ajax action for modifying the title of a quote
	"""
	user = request.user ## in the future we'll have to handle username too

	quote_id = request.GET.get('quote_id', None)
	newname = request.GET.get('name', "")

	results = []
	
	if not newname.strip():
		return HttpResponseForbidden()
	try: 
		f1 = Fragment.objects.get(pk=int(quote_id), created_by=user)
	except:
		return HttpResponseForbidden()
	
	f1.title = newname
	f1.save()
	
	results = { 'new_name': f1.title }				
	json = simplejson.dumps(results)
	return HttpResponse(json, mimetype='application/json')






# February 26, 2015: this will have to be revised
@login_required
def changeQuoteKoncept(request):
	"""
	ajax call
	attaches a new Koncept to a Quote. If there was an old koncept, that is left as it
	is. However if the old koncept has no interpretations left, it is deleted.
	"""
	user = request.user
	k_old = None
	try:
		quoteid = int(request.GET.get('quoteid', False))
		f1 = Fragment.objects.get(pk=int(quoteid), created_by=user)
	except:
		return HttpResponse("Fragment ID not matches users data")
	try:
		newname = request.GET.get(u'name', False)
	except:
		newname = ""
			
	if request.method == "GET":
		if newname.strip() and not(newname.isdigit()):
							
			# reuse a koncept with exact same name, if available
			try: 
				k1 = Koncept.objects.get(name=newname, created_by=user)
				k1.updated_at = datetime.today()
			except: 
				k1 = Koncept(name=newname, created_by=user)
			k1.save()

	
			intfrag = f1.get_interpretation()	
			if intfrag:
				k_old = intfrag.koncept
				intfrag.koncept=k1
				intfrag.fragment=f1
				intfrag.updated_at = datetime.today()		
			else:
				intfrag = IntFrag(koncept=k1, fragment=f1, created_by=user)
				
			intfrag.save()	
				
	
			# if koncept is an orphan, delete it!
			if k_old:
				if k1.id != k_old.id:				
					if k_old.intfrag_set.count():
						k_old.cleanIntFragOrdering() 
					else:
						printdebug("Deleting Koncept %s" % str(k_old))
						k_old.delete()
	
	
			results = { 'saved_name': newname.capitalize(), 
						'new_url' : k1.get_absolute_url(),
						'page_flag' : 'new',
						}				
			json = simplejson.dumps(results)
			return HttpResponse(json, mimetype='application/json')
	
	# if it fails
	return HttpResponse("Some error occurred. Most probably name is not empty or contains only digits")








@login_required
def edit_quote_subjects(request):
	"""
	Ajax action for modifying the title of a quote
	"""
	user = request.user ## in the future we'll have to handle username too
	context = {}

	quote_id = request.GET.get('quote_id', None)
	newsubjects = request.GET.get('subjects', "")
	page = request.GET.get('page', "")

	if page == "search_quotes":
		context['ALIGNMENT'] = 'left'
		context['search_quotes_page'] = True,
	else:
		pass

	data = { 'new_subjects' : "" }
	
	try:
		f1 = Fragment.objects.get(pk=int(quote_id), created_by=user)
	except:
		return HttpResponseForbidden()
	
	newsubjects = newsubjects.strip().split(",")	
	
	old_subjects = list(f1.subjects.all())
	
	if not newsubjects and not old_subjects:
		pass
	
	else:		
		# clear tags and recreate them
		f1.subjects.clear()					
		if newsubjects:
			for el in newsubjects:
				if el:
					try:
						subject = Subject.objects.get(name=el.strip().lower(), created_by=user)
					except:
						subject = Subject(name=el.strip().lower(), created_by=user)
						subject.save()
					f1.subjects.add(subject)

			context.update({'snippet' : f1, 'mykoncepts' : True,
							'SUBJECT_LABEL' : which_labels(request)['SUBJECT_LABEL']})
			# return_str = render_block_to_string('bstrap3.2.0/components/tags_snippet.html', 
			return_str = render_block_to_string('bstrap3.2.0/components/sidebar_tagsinfo.html', 
												'snippet_tags_snippet',
												context)
														
			data = { 'new_subjects' : return_str }
			
		Subject.cleanUpUserSubjects(user, old_subjects)
	
			
	json = simplejson.dumps(data)
	return HttpResponse(json, mimetype='application/json')






			


# ===========
# Documents
# ===========



@login_required
def edit_document(request, doc_id=None):
	"""
	Edit a single document details. 
	Since this is done within a modal window, the form is actually created elsewhere (document.py)
	Here we just parse it and try to make changes to the DB. 
	"""

	user = request.user
	d1 = get_object_or_404(Document, pk=int(doc_id), created_by=user)
				
	if request.method == 'POST': 
		
		# 
		# edit action: process a submitted form						
		#
		
		form = NewDocumentForm(request.POST)

		if form.is_valid() and form.cleaned_data['sourcetitle']: # TITLE is compulsory: otherwise it'll fail silently for now
 
			try:
				d1.title = form.cleaned_data['sourcetitle']
				d1.author = form.cleaned_data['sourceauthor']
				d1.description = form.cleaned_data['sourcedesc']
				d1.pubyear = form.cleaned_data['sourcepubyear']
				d1.url = form.cleaned_data['sourceurl']
				d_new.save()
				print d1

				if False:
					# 2016-05-16: @todo revisit the merge case

					# reuse a source with exact same data, if available [= the autocompletion should make all data surface]
					# Note: this will match also if we change just a field in a preexisting source
					d_new = Document.objects.get(title=form.cleaned_data['sourcetitle'], created_by=user)
					
					# overwrite if anything's changed
					if d_new.author != form.cleaned_data['sourceauthor'] or d_new.description != form.cleaned_data['sourcedesc'] or d_new.pubyear!=form.cleaned_data['sourcepubyear'] or d_new.url != form.cleaned_data['sourceurl']:
						d_new.author = form.cleaned_data['sourceauthor']
						d_new.description = form.cleaned_data['sourcedesc'] 
						d_new.pubyear=form.cleaned_data['sourcepubyear']
						d_new.url = form.cleaned_data['sourceurl']
						d_new.save()
					
					if d_new.id != d1.id:
						d_new.mergeWithDocument(d1)
						# to make the redirect variable work
						d1 = d_new
					
			except:
				# if title isn't already existing, overwrite completely the old one (but keep the ID)	
				
				d1.title = form.cleaned_data['sourcetitle']
				d1.author = form.cleaned_data['sourceauthor']
				d1.description = form.cleaned_data['sourcedesc'] 
				d1.pubyear=form.cleaned_data['sourcepubyear']
				d1.url = form.cleaned_data['sourceurl']
				d1.save()


		

	return HttpResponseRedirect('%s' % d1.get_absolute_url())





@login_required
def edit_source_quotes_order(request, doc_id):
	"""
	Ajax action for modifying the ordeno of a fragment within a source

	@todo: only stubbed on 2015-03-12
		
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []

	# make sure the user owns the Document, or raise a permissions error
	try:
		d1 = Document.objects.get(pk=doc_id, created_by=user)
	except:
		return HttpResponseForbidden()

	ukeys = request.GET.getlist('o[]')

	if d1 and ukeys:
		for x in range(len(ukeys)):
			try:
				f = Fragment.objects.get(source=d1, id=ukeys[x], created_by=user)
				# print i.fragment.id
				f.orderno = x+1	 # because the iterator is zero-based
				f.save()
			except:
				printdebug("== Error updating source-quote order for %s" % str(d1))

		d1.cleanOrdering()
		results = { 'new_url': d1.get_absolute_url() }
		json = simplejson.dumps(results)
		return HttpResponse(json, mimetype='application/json')
	
	# if it fails
	return HttpResponse("") 














# ===========
# Koncept / Collection
# ===========



@login_required
def edit_koncept_details(request, kon_id=None):
	"""
	Ajax action for modifying the name&description of a Koncept (cross-interpretations)
	
	2015-03-17: - upgraded from <edit_koncept_name>
				- now a koncept is never merged by default
		
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []

	newname = request.GET.get('name', "")
	newdesc = request.GET.get('desc', "")
	if not newname.strip():
		return HttpResponseForbidden()		
	if newname.isdigit():
		return HttpResponseForbidden()	
		
	# make sure the user owns the Koncept, or raise a permissions error
	try: 
		k1 = Koncept.objects.get(pk=kon_id, created_by=user)
	except:
		return HttpResponseForbidden()
	
	k1.name = newname
	k1.description = newdesc
	k1.updated_at = datetime.today()
	k1.save()
		
	# 2015-03-17: mergin operation is disabled
		# k_new = Koncept.objects.get(name=request.GET[u'name'], created_by=user)
		# k_new.updated_at = datetime.today()
		# k_new.mergeWithKoncept(k1)
		# k1 = k_new

	results = { 'new_url': k1.get_absolute_url() }				
	json = simplejson.dumps(results)
	return HttpResponse(json, mimetype='application/json')
	
	




@login_required
def edit_koncept_quotes_order(request, kon_id):
	"""
	Ajax action for modifying the ordeno of a fragment within a koncept
	
	IntFrag.orderno
		
	"""
	user = request.user ## in the future we'll have to handle username too

	results = []

	# make sure the user owns the Koncept, or raise a permissions error
	try: 
		k1 = Koncept.objects.get(pk=kon_id, created_by=user)
	except:
		return HttpResponseForbidden()
	
	ukeys = request.GET.getlist('o[]')
	
	if k1 and ukeys:
		for x in range(len(ukeys)):
			try:
				i = IntFrag.objects.get(koncept=k1, fragment__id=ukeys[x], created_by=user)
				# print i.fragment.id
				i.orderno = x+1	 # because the iterator is zero-based 
				i.save()
			except:
				printdebug("== Error updating collection-quote order for %s" % str(k1))
				
		k1.cleanIntFragOrdering()
		results = { 'new_url': k1.get_absolute_url() }				
		json = simplejson.dumps(results)
		return HttpResponse(json, mimetype='application/json')
	
	# if it fails
	return HttpResponse("") 













