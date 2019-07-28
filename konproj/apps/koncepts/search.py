#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for search and public koncept/doc pages - created on 9Feb2013
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from datetime import *

from myutils.myutils import paginator_helper, split_list
from koncepts.models import *
# from koncepts.tag import get_tag_cloud
from settings import printdebug, BOOTSTRAP

from koncepts.document import _prePopulateEditDocumentForm





@login_required
def search_quotes(request, username, favorites=False, clipboard=False):
	"""
	February 24, 2015: 
		removed collection and added group_var
	View that performs a search based on the query string, or returns the whole list of snippets.

	searchdict =  main list of AND constraints

	July 31, 2014: first version
	April 8, 2015: updated and removed <url_encode>
	
	"""
	
	PAGINATION_SET = 50
	
	# get init values
	searchdict = {}
	qset = Fragment.objects.filter()

	quickEditForm = None

	searchval = request.GET.get('q', "") 
	exactmatch = request.GET.get('exact', "") 
	group_var = request.GET.get('g', "") 
	sourcefacet_var = request.GET.get('d', "") 
	# tag = request.GET.get('tag', None) 
	subject = request.GET.get('subject', None) 
	view_var = request.GET.get('v', 'list')	 # March 28, 2014: not used
	sort_var = request.GET.get('sort', 'created')
	if sort_var not in ['alpha', 'modified', 'created']: sort_var = 'created'	 # default sort value
	sorting = {'alpha' : ["text", "-updated_at"], 
				'modified': ["-updated_at", "text"], 
				'created': ["-created_at", "text"]} [sort_var]
	if group_var not in ['all', 'last-week', 'last-month', 'no-collection', 'no-title']: group_var = 'all'
	
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	person = get_object_or_404(User, username=username)
	
	context = {'person' : person} # initialize context
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
		searchdict['created_by'] = request.user
		usertags = [s.name for s in Subject.subjectsListPerUser(request.user)]
		if usertags:
			context['usertags'] = usertags
		if favorites:
			searchdict['favorite'] = True
			context.update({'page_flag' : "favorites" })
			# context['page_flag'] = "favorites",  # x dynamic top menu
		elif clipboard:
			searchdict['clipboard'] = True
			context.update({'page_flag' : "clipboard" })	
		else:
			context.update({'page_flag' : "searchquotes" })
		
	else:
		context['mykoncepts'] = False
		raise Http404


	try:
		sourcefacet_var = int(sourcefacet_var)
		source = Document.objects.get(pk=sourcefacet_var, created_by=request.user)
		quickEditForm = _prePopulateEditDocumentForm(source)
	except:
		sourcefacet_var, source = None, None

	# printdebug(tag)		


	if subject:
		try:
			subject = Subject.objects.get(pk=int(subject), created_by=person)
			subjects_tree = subject.get_descendants(include_self=True)
			if len(subjects_tree) > 1:
				context.update({
				'tree_inheritance' : True,
				})

		except:
			subjects_tree = None
			subject = None

	if subject:
		# GENERATE A BIG OR QUERY FOR THE SUBJECT TREE
		# searchdict['subjects__id'] = subject.id  # previusly..
		searchval = ""
		# Turn list of values into one big Q objects
		query = reduce(lambda q,value: q|Q(subjects__id=value.id), subjects_tree, Q())
		qset = qset.filter(query)


	if searchval:
		if exactmatch:
			_searchval = ' ' + searchval + ' '
			qset = qset.filter(text__icontains=_searchval)
			print "searchval is", searchval	
		else:  # fuzzy
			multi_search_val = [x.strip() for x in searchval.split(" ") if x]
			for x in multi_search_val:
				qset = qset.filter(text__icontains=x)


	if sourcefacet_var:
		searchdict['source__id'] = sourcefacet_var # already casted to a number

	else:
		# COLLECTIONS
		if group_var == 'all':
			pass # no need for other filters
		elif group_var == 'last-week':
			today = datetime.today()
			searchdict['created_at__gte'] = today - timedelta(days=7)
		elif group_var == 'last-month':
			today = datetime.today()
			searchdict['created_at__gte'] = today - timedelta(days=30)
		elif group_var == 'no-title':
			searchdict['title'] = None
		elif group_var == 'no-collection':
			searchdict['intfrag'] = None

	
	# qset = Fragment.objects.filter(**searchdict).distinct().order_by(*sorting)
	data = qset.filter(**searchdict).distinct().order_by(*sorting)
				

	# 2015-03-29: sources facet only if keyword is passed
	if searchval:
		# if a facet filter is available, remove it before recalc the facets
		if sourcefacet_var: # note: this was previously added
			searchdict.pop("source__id")
		# sourcesfacet = Fragment.objects.filter(**searchdict).order_by('source__title').values_list('source__title', 'source').distinct()
		sourcesfacet = qset.filter(**searchdict).order_by('source__title').values_list('source__title', 'source').distinct()
		
		# transform sourcefacet_var from id to a tuple
		for x in sourcesfacet:
			if x[1] == sourcefacet_var:
				sourcefacet_var = x
				break
		
	else:
		sourcesfacet = []
	
	

	if subject or searchval:
		if subject:
			related_subjects = Subject.objects.exclude(id=subject.id).filter(fragment__in=data).distinct()
		else:
			related_subjects = Subject.objects.filter(fragment__in=data).distinct()
		context.update({'related_subjects' : related_subjects})
	
	# set up pagination and prepare for specific viz
	
	paginator = Paginator(data, PAGINATION_SET)
	try:
		page_object = paginator.page(page)
	except (EmptyPage, InvalidPage):  # If page request is out of range, deliver last page of results.
		page_object = paginator.page(paginator.num_pages)
	page_object.extrastuff = paginator_helper(page, paginator.num_pages)
	page_object.totcount = paginator.count

	if view_var == "list":
		template_name = BOOTSTRAP + 'pages/search_quotes.html'
	else:
		template_name = BOOTSTRAP + 'pages/search_quotes_viewbysource.html'

	# finally...
	context.update({	  
				'page_object' : page_object,
				'searchval' : searchval, 
				'exactmatch' : exactmatch, 
				'sort_var' : sort_var,
				'view_var' : view_var,
				'subject' : subject,
				'active_group' : group_var,
				'sourcesfacet' : sourcesfacet,
				'active_sourcefacet' : sourcefacet_var,
				'active_source' : source,
				'form' : quickEditForm , # for document
				})
	return render_to_response(template_name, 
							context,
							context_instance=RequestContext(request))








# 2015-08-24: deprecated in attesa di tempi migliori

		
@login_required
def search_koncept(request, username, collection=""):
	"""
	
	main view for koncepts list page
	
	"""

	# get init values
	searchdict = {}
	qset = Koncept.objects.filter()
		
	searchval = request.GET.get('q', "") 
	group_var = request.GET.get('g', "") 
	sort_var = request.GET.get('sort', 'alpha')
	if sort_var not in ['alpha', 'modified', 'created']: sort_var = 'alpha'
	sorting = {'alpha' : ["name", "-updated_at"], 
				'modified': ["-updated_at", "name"], 
				'created': ["-created_at", "name"]} [sort_var]
	
	if group_var not in ['all', 'last-week', 'last-month']: group_var = 'all'
	
	letter_var = request.GET.get('start', None)	
	letters = None
	
	person = get_object_or_404(User, username=username)
	
	context = {'person' : person} # initialize context
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
		searchdict['created_by'] = request.user
	else:
		context['mykoncepts'] = False
		raise Http404

	# GROUPS
	if group_var == 'all':
		pass # no need for other filters
	elif group_var == 'last-week':
		today = datetime.today()
		searchdict['created_at__gte'] = today - timedelta(days=7)	 
	elif group_var == 'last-month':
		today = datetime.today()
		searchdict['created_at__gte'] = today - timedelta(days=30)
	else:
		raise Http404	

	# printdebug(tag)	
	
	if group_var == 'all' and not searchval:
		# displaying all 
		letters = list(qset.filter(**searchdict).order_by('first_letter').values_list('first_letter', flat=True).distinct())	
	
		if letters:  # = if there's contents at all
			if letters[0] == "*":
				letters.append(letters.pop(0))
	
			if not letter_var:
				letter_var = letters[0] # if not passed, default to first letter available
		
		totcount = Koncept.objects.filter(**searchdict).distinct().count()
		searchdict['first_letter'] = letter_var
		data = qset.filter(**searchdict).distinct().order_by(*sorting)
				
	else:
		# search or time based search 
		multi_search_val = [x.strip() for x in searchval.split(" ") if x]
		for x in multi_search_val:
			qset = qset.filter(name_url__icontains=x)
			# searchdict['name_url__icontains'] = url_encode_search(x)	
		data = qset.filter(**searchdict).distinct().order_by(*sorting)
		totcount = len(data)
		letter_var = ""


	template_name = BOOTSTRAP + 'pages/search_koncepts.html'
	data.totcount = totcount
			
	# finally...
	context.update({	  
				'searchval' : searchval, 
				'sort_var' : sort_var,
			    'letters' : letters,	
			    'active_letter' : letter_var,
				'active_group' : group_var,
				'page_object' : data,
				'ideas_search' : True, # simple flag
				'page_flag' : "searchkoncepts",  # x dynamic top menu
				})
	return render_to_response(template_name, 
							context,
							context_instance=RequestContext(request))










@login_required
def search_document(request, username):
	"""
	
	View that performs a search based on the query string, or returns the whole list of Documents.

	searchdict =  main list of AND constraints
	
	April 2, 2014: currenlty you can search only for your own documents
	
	February 24, 2015: added groups and reactivated view
	
	"""
	
	PAGINATION_SET = 50
	
	# get init values
	searchdict = {}
	qset = Document.objects.filter()
	
	searchval = request.GET.get('q', None) 
	group_var = request.GET.get('g', "") 	
	# view_var = request.GET.get('v', 'list') 
	sort_var = request.GET.get('sort', 'created')
	
	if sort_var not in ['alpha', 'modified', 'created']: sort_var = 'created'	
	if group_var not in ['all', 'last-week', 'last-month']: group_var = 'all'

	sorting = {'alpha' : ["title", "-updated_at"], 
				'modified': ["-updated_at", "title"], 
				'created': ["-created_at", "title"]} [sort_var]
						
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	person = get_object_or_404(User, username=username)
	
	context = {'person' : person} # initialize context
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
		searchdict['created_by'] = request.user		
	else:
		context['mykoncepts'] = False
		raise Http404
	
	
	if searchval:
		multi_search_val = [x.strip() for x in searchval.split(" ") if x]
		for x in multi_search_val:
			qset = qset.filter(searchindex__icontains=x)
			# searchdict['searchindex__icontains'] = url_encode_search(x)
	else:	
		# GROUPS
		if group_var == 'all':
			pass # no need for other filters
		elif group_var == 'last-week':
			today = datetime.today()
			searchdict['created_at__gte'] = today - timedelta(days=7)	 
		elif group_var == 'last-month':
			today = datetime.today()
			searchdict['created_at__gte'] = today - timedelta(days=30)

	# print searchdict
	qset = qset.filter(**searchdict).distinct().order_by(*sorting)
					
	
	# set up pagination and prepare for specific viz
	
	paginator = Paginator(qset, PAGINATION_SET)
	try:
		page_object = paginator.page(page)
	except (EmptyPage, InvalidPage):  # If page request is out of range, deliver last page of results.
		page_object = paginator.page(paginator.num_pages)
	page_object.extrastuff = paginator_helper(page, paginator.num_pages)
	page_object.totcount = paginator.count

	template_name = BOOTSTRAP + 'pages/search_documents.html'

	# finally...
	context.update({	  
				'page_object' : page_object,
				'searchval' : searchval, 
				'sort_var' : sort_var,
				'active_group' : group_var,
				'page_flag' : "searchdocs",  # x dynamic top menu
				})
	return render_to_response(template_name, 
							context,
							context_instance=RequestContext(request))





