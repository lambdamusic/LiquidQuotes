#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for /source/	- created on 9Feb2013
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage


from myutils.myutils import paginator_helper

from django.contrib.auth.models import User
from koncepts.models import *
from koncepts.tag import get_tag_cloud
from koncepts.forms import NewDocumentForm
from koncepts.graphs import *


from settings import printdebug, BOOTSTRAP




def get_document(request, username, source_name):
	"""
	View that returns a document with all of its interpretations/koncepts
	
	December 27, 2015: if the document is not owned by the user, it is not shown
	
	August 27, 2014: removed the Intfrags and tried to use only Koncept list
	- no pagination anymore temporarily, nor sorting
	
	December 29, 2014: added mechanism to make this work via IDs only
	eg '617-mind-a-brief-introduction-fundamentals-of-philosophy-searle-john-r'
	 is reduced to 617.
	"""

	d1, quickEditForm, qset, relatedDocuments, koncepts = None, None, None, None, None
	nodes, edges = [], []
	searchdict = {}
	PAGINATION_SET = 50
	MAX_RELATED_ITEMS = 7
	
	# try to extract the number ID
	try:
		pos = source_name.find("-")
		if pos > 0:
			source_id = int(source_name[:pos])
		else:
			source_id = int(source_name)
	except:
		raise Http404
	
	person = get_object_or_404(User, username=username)
	context = {'person' : person} # initialize context
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
		usertags = [s.name for s in Subject.subjectsListPerUser(request.user)]
		if usertags:
			context['usertags'] = usertags
	else:
		context['mykoncepts'] = False
								
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1

	sort_snippets = request.GET.get('sort', 'words')
	if sort_snippets not in ['words', 'order',]: sort_snippets = 'words'	 # default 

	# compose search dictionary: 
	
	if context['mykoncepts']:
		searchdict['created_by'] = request.user
		# searchdict['name_url'] = url_encode(source_name)
		searchdict['id'] = source_id
	else:
		searchdict['created_by'] = person
		# searchdict['name_url'] = url_encode(source_name)
		searchdict['id'] = source_id
		
	try:
		d1 = Document.objects.filter(**searchdict).distinct()[0]
	except:		
		# return HttpResponseRedirect('/search/source/%s' % url_encode(source_name))  #always fallback to search
		raise Http404


	# get the objects to be displayed
	
	if context['mykoncepts']:

		quickEditForm = _prePopulateEditDocumentForm(d1)
		#temp: June 23, 2014
		snippets = Fragment.objects.filter(source=d1, created_by=person)
		
		if sort_snippets == "words":
			snippets_overview = sorted(snippets, key=lambda x: len(x.text.split()))
		else:
			snippets_overview = snippets
			
		if False:
			nodes, edges = getSourceQuotesGraph(d1)

	else:

		snippets = Fragment.objects.filter(source=d1, created_by=person, isprivate=False)
		snippets_overview = snippets

				
		# if the document has no public intfrags, then it is hidden
		if not snippets:
			raise Http404

	
	if False:
		# set up pagination == August 27, 2014: Removed
		paginator = Paginator(qset, PAGINATION_SET)			
		try:
			page_object = paginator.page(page)
		except (EmptyPage, InvalidPage):  # If page request is out of range, deliver last page of results.
			page_object = paginator.page(paginator.num_pages)
		page_object.extrastuff = paginator_helper(page, paginator.num_pages)
		page_object.totcount = paginator.count


	# printdebug(context['mykoncepts'])


	# finally...
	context.update({	  
				'd1' : d1,
				'page_flag' : 'document_detail', 
				# 'page_object' : page_object,
				'sort_snippets_var' : sort_snippets,
				'form' : quickEditForm ,
				'person' : person,
				'snippets': snippets,
				'snippets_overview': snippets_overview,
				# 'recentDocuments' : recentDocuments,
				'relatedDocuments' : relatedDocuments,
				'koncepts' :koncepts, 
				# 'nodes': simplejson.dumps(nodes),
				# 'edges': simplejson.dumps(edges),
				})
	
	return render_to_response(BOOTSTRAP + 'pages/document_detail.html', 
							context,
							context_instance=RequestContext(request))









def _prePopulateEditDocumentForm(d1):
	"""
	Logic very similar to the one in 'new.py'
	Note: this is returned only if a user is looking at his own document.
	"""
	dict1 = {}
	dict1['sourcetitle'] = d1.title
	dict1['sourceurl'] = d1.url
	dict1['sourceauthor'] = d1.author
	dict1['sourcepubyear'] = d1.pubyear
	dict1['sourcedesc'] = d1.description
	
	form =	NewDocumentForm(dict1)
	
	if form.is_valid():
		printdebug(form.data['sourcedesc'])
	else:
		printdebug(form.errors) 
	return form







