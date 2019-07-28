#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for /koncept/	 - created on 9Feb2013
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
from django.utils import simplejson
from django.core.urlresolvers import reverse

from django.db.models import Q
import operator

from myutils.myutils import paginator_helper

from koncepts.models import *
# from koncepts.tag import get_tag_cloud
from settings import printdebug, BOOTSTRAP

import difflib

from context_processors import which_labels




def get_koncept(request, username, koncept_name):
	"""
	View that manages the single-koncept request. 
	
	person = the user associated to the koncept requested via the url path
	user = the user currenlty logged in (if any)
	
	Note: If the kon name is passed but not found, it defaults to a search for that koncept name.
	
	December 29, 2014: added mechanism to make this work via IDs only
	eg '5-algorithmic-composition' is reduced to 5.
	
	"""
	
	k1 = None
	
	searchdict = {}
	related_koncepts, nodesJit = [], []
	nodes1, edges1 = None, None
	nodes2, edges2 = None, None
	
	view_var = request.GET.get('v', None) 

	# try to extract the number ID
	try:
		pos = koncept_name.find("-")
		if pos > 0:
			koncept_id = int(koncept_name[:pos])
		else:
			koncept_id = int(koncept_name)
	except:
		raise Http404
		
	person = get_object_or_404(User, username=username)	
	context = {'person' : person} # initialize context
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
	else:
		context['mykoncepts'] = False
	
	# compose search dictionary: private koncept-intepretations are seen only by logged in users
	
	if context['mykoncepts']:
		searchdict['created_by'] = request.user
		# searchdict['name_url'] = url_encode(koncept_name)
		searchdict['id'] = koncept_id
	else:
		searchdict['created_by'] = person
		# searchdict['name_url'] = url_encode(koncept_name)
		searchdict['id'] = koncept_id
		searchdict['intfrag__fragment__isprivate'] = False
	

	# do the search
	try:
		k1 = Koncept.objects.filter(**searchdict).distinct()[0]
	except: 
		raise Http404
		# return HttpResponseRedirect('/%s/ideas/?q=%s' % (username, url_encode(koncept_name))) 
		# return HttpResponseRedirect(reverse('search_user_koncepts' , args=(user.username,)))


	# HISTORY view : October 4, 2013 bootstrap
	
	if view_var == "history":
		if request.user.is_authenticated():	 #and username == request.user.username
			pass
		else:
			pass
		context.update({	  
					'k1' : k1,
					})

		return render_to_response(BOOTSTRAP + 'pages/koncept_history.html', 
								context,
								context_instance=RequestContext(request))




	# STANDARD VIEW : get the interpretations 
	
	if context['mykoncepts']:

		interpretations = k1.intfrag_set.all().order_by('orderno')
		documents = k1.getSources(include_private=True, countFragments=True) # dict including counts
		
		if False:  # March 16, 2015: temp hidden
			nodes1, edges1 = graphData_relatedSources(k1, request.user, False)
			# nodes2, edges2 = graphData_similarKonceptsVisJs(k1, request.user, False)
			nodesJit = graphData_similarKonceptsJIT(k1, request.user, False)
			# related_koncepts = k1.getSimilarKoncepts(n=6, user=request.user, onlypublic=False)

		

		
	else: 
		interpretations = k1.intfrag_set.filter(fragment__isprivate=False).order_by('orderno')
		# documents = list(set([x.fragment.source for x in interpretations]))
		documents = k1.getSources(include_private=False, countFragments=True) # dict including counts
		# related_koncepts = k1.getSimilarKoncepts(n=6, user=k1.created_by)
		# @TODO? GRAPH FOR NON OWNED KONCEPTS?


	context.update({	  
				'k1' : k1,
				'interpretations' : interpretations,
				'documents' : documents,
				'related_koncepts' : related_koncepts ,
				# 'tagscloud' : get_tag_cloud(request), 
				'mynodes_relatedSources' : nodes1,
				'myedges_relatedSources' : edges1,
				# 'mynodes_similarKoncepts' : nodes2,
				# 'myedges_similarKoncepts' : edges2,
				'nodesJit' : nodesJit,
				})
				

	return render_to_response(BOOTSTRAP + 'pages/koncept_detail.html', 
							context,
							context_instance=RequestContext(request))


						



def graphData_relatedSources(a_koncept, user=None, onlypublic=True):
	"""
	creates the json structures needed by the visjs library
	
	graph: network of koncept > sources > others koncepts
	"""

	KONCEPT_LABEL = which_labels(None)['KONCEPT_LABEL']
	DOCUMENT_LABEL = which_labels(None)['DOCUMENT_LABEL']


	def addBRspace(stringa):
		""" util to add linebreaks """
		SIZE = 3
		ss = stringa.split()
		return '\n'.join(' '.join(ss[pos:pos+SIZE]) for pos in xrange(0, len(ss), SIZE))	

	# koncept sources + their related koncepts
	nodes1  = [] 
	edges1  = []

	rootid = "k_"+ str(a_koncept.id)
	INDEX1 = [rootid] #hack to keep track of what's in there already - the js libs fails otherwise
	top = {'id' : rootid, 'label' : addBRspace(a_koncept.name), 'group' : 'group_root'}
	nodes1 += [top]

	for s in a_koncept.getSources():
		sid = "s_"+ str(s.id)
		s_label = addBRspace(s.title) + "\n" + s.get_url_domain().strip("http://")
		nodes1 += [{'id' : sid, 'label' : s_label, 'group' : 'group_source'}]
		edges1 += [{'from' : rootid, 'to' : sid, 'label' : "%s" % DOCUMENT_LABEL.lower()}]
		
		for k in s.get_koncepts():
			kid = "k_"+ str(k.id)
			if kid != rootid:
				if kid not in INDEX1:
					INDEX1 += [kid]					
					nodes1 += [{'id' : kid, 'label' : addBRspace(k.name), 'group' : 'group_koncept'}]
				edges1 += [{'from' : sid, 'to' : kid, 'label' : "%s" % KONCEPT_LABEL.lower()}]
	
	
	return [simplejson.dumps(nodes1), simplejson.dumps(edges1)] 





def graphData_similarKonceptsJIT(a_koncept, user=None, onlypublic=True):
	"""
	creates the json structures needed by the JIT library
	
	graph: network of koncept > similar koncepts
	"""

	# 1) get related koncepts recursively 
	def nav_tree(el, level=None):
		if level==None:
			level = 1
		d = {}
		d['id'] =  el.id
		d['name'] = el.name
		d['data'] = {'url' : el.get_absolute_url()}

		if level < 2: # and el.get_children() and not TESTING:			
			d['children'] = [nav_tree(x, level+1) for x in el.getSimilarKoncepts(n=3, user=user, onlypublic=onlypublic)]
		else:
			d['children'] = []
		return d
		
	tree = {'id': a_koncept.id, 'name': a_koncept.name, 'children': [],  'data': {'url' : a_koncept.get_absolute_url()}}

	for x in a_koncept.getSimilarKoncepts(n=6, user=user, onlypublic=onlypublic):
		tree['children'] += [nav_tree(x)]
	
	
	return simplejson.dumps(tree)








def graphData_similarKonceptsVisJs(a_koncept, user=None, onlypublic=True):
	"""
	creates the json structures needed by the visjs library
	
	graph: network of koncept > similar koncepts > related sources
	"""

	KONCEPT_LABEL = which_labels(None)['KONCEPT_LABEL']
	DOCUMENT_LABEL = which_labels(None)['DOCUMENT_LABEL']


	def addBRspace(stringa):
		""" util to add linebreaks """
		SIZE = 3
		ss = stringa.split()
		return '\n'.join(' '.join(ss[pos:pos+SIZE]) for pos in xrange(0, len(ss), SIZE))
	
	
	if True:
		# only koncepts similar
		nodes  = [] 
		edges  = []
		rootid = "k_"+ str(a_koncept.id)
		
		INDEX_KONS = [rootid] #hack to keep track of what's in there already - the js libs fails otherwise	
		INDEX_DOCS = []
		top = {'id' : rootid, 'label' : a_koncept.name, 'group' : 'group_root'}
		nodes += [top]
	
		for x in a_koncept.getSimilarKoncepts(n=6, user=user, onlypublic=onlypublic):
			x_id = "k_"+ str(x.id)
			if x_id not in INDEX_KONS:
				INDEX_KONS += [x_id]
				nodes += [{'id' : x_id, 'label' : addBRspace(x.name), 'group' : 'group_koncept'}]
				edges += [{'from' : rootid, 'to' : x_id, 'label' : "", 'color' : '#848484'}]
				
				for s in x.getSources():
					sid = "s_"+ str(s.id)
					if sid not in INDEX_DOCS:
						s_label = addBRspace(s.title) + "\n" + s.get_url_domain().strip("http://")
						nodes += [{'id' : sid, 'label' : s_label, 'group' : 'group_source'}]
						INDEX_DOCS += [sid]					
					edges += [{'from' : x_id, 'to' : sid, 'label' : "%s" % DOCUMENT_LABEL.lower(),  'color' : '#2B7CE9'}]
					
	
				if False:
					for x1 in x.getSimilarKoncepts(n=6, user=user, onlypublic=onlypublic):
						x1_id = "k_"+ str(x1.id)
						if x1_id not in INDEX_KONS:
							INDEX_KONS += [x1_id]
							nodes += [{'id' : x1_id, 'label' : addBRspace(x1.name), 'group' : 'group_koncept'}]
						edges += [{'from' : x_id, 'to' : x1_id, 'label' : "similar to" }]
		
		return [simplejson.dumps(nodes), simplejson.dumps(edges)]
		






#
# def get_similar_koncepts(user, kon1, n=3):
# 	"""
# 	Util that does some string matching to suggest similar koncepts.
# 	If the user is None, only public koncepts are returned.
# 	"""
#
# 	def similar(seq1, seq2):
# 		return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.3
#
# 	def removeArticles(text):
# 		articles = ['and', 'a', 'the', 'an', 'of', 'for', 'to', 'in', 'by', 'at', 'with']
# 		newText = ''
# 		for word in text.lower().split(' '):
# 			if word not in articles:
# 				newText += word+' '
# 		return newText[:-1]
#
# 	output = []
# 	if not user:
# 		qset = Koncept.objects.filter(intfrag__isprivate=False)
# 	else:
# 		qset = Koncept.objects.filter(created_by=user)
# 	# get a queryset that (roughly) matches the nouns in the Koncept name
# 	predicates = [('name__icontains', x) for x in removeArticles(kon1.name).split()]
#
# 	qset = qset.filter(reduce(operator.or_, [Q(x) for x in predicates]))
#
# 	# iterate over it and extract the best matches
# 	for x in qset:
# 		# print "*" * 10, x
# 		if x.id != kon1.id and similar(removeArticles(kon1.name), removeArticles(x.name)):
# 			if x not in output:
# 				output += [x]
# 				if len(output) == n:
# 					break
#
# 	# add koncepts from related sources
#
# 	for el in kon1.getRelatedKonceptsViaSources()[:5]:
# 		if el not in output:
# 			output = [el] + output
#
# 	return output
#



def get_random_koncept(request):
	
	"""
	View that ...
	"""

	searchdict = {}

	# compose search dictionary
	if request.user.is_authenticated(): 
		searchdict['created_by'] = request.user
	else:
		searchdict['intfrag__fragment__isprivate'] = False
	
	try:
		k =Koncept.objects.filter(**searchdict).order_by('?')[0]
		return HttpResponseRedirect('%s' % k.get_absolute_url())
	except:
		return HttpResponseRedirect('/')








