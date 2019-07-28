#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for the top level (eg homepage, presentation) still unused
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
# from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse

from datetime import *
import string, json
from myutils.myutils import paginator_helper

from koncepts.models import *

from myutils.myutils import split_list
from settings import printdebug, BOOTSTRAP



#
# ===========
# TESTS
# ===========



def blockquote(request):
	"""test for	 new blockquote"""
	data = Fragment.objects.all().order_by('?')[0]
	return render_to_response(BOOTSTRAP + 'test/test-blockquote.html',	
							{ 
							  'data': data,		
							},
							context_instance=RequestContext(request))
							


						
							
def summernote(request):
	"""test for summernote.js"""
	data = Fragment.objects.all().order_by('?')[0]
	return render_to_response(BOOTSTRAP + 'test/test-summernote.html',	
							{ 
							  'data': data,		
							},
							context_instance=RequestContext(request))	


def quotelist_table(request):
	"""
	returns a list of recent quotes formatted very simply
	"""
	
	letter_var = request.GET.get('start', 'a')
	
	letters = list(string.lowercase)
	letters += ['0-9']

	searchdict = {}
	sort_var = request.GET.get('sort', 'created')
	if sort_var not in ['alpha', 'modified', 'created']: sort_var = 'modified'	 # default sort value
	sorting = {'alpha' : ["text", "-updated_at"], 
				'modified': ["-updated_at", "text"], 
				'created': ["-created_at", "text"]} [sort_var]
	
	# if letter_var == "0-9":
	#	# Keyword.objects.exclude(keyword__regex=r'^[a-zA-Z]')
	#	data = Koncept.objects.exclude(name__regex=r'^[a-zA-Z]')
	# else:
	#	data = Koncept.objects.filter(name__istartswith=letter_var)
	searchdict['created_by'] = request.user		
	data = Fragment.objects.filter(**searchdict).distinct().order_by(*sorting)[:100]
		
	return render_to_response(BOOTSTRAP + 'test/test-quotelist-table.html', 
							{ 
							  'data': data,		
							  'letters' : letters,	
							  'active_letter' : letter_var,
							},
							context_instance=RequestContext(request))
							
							
							
							
def konlist_table(request):
	"""
	returns a list of recent koncepts formatted very simply
	"""
	
	letter_var = request.GET.get('start', 'a')
	
	letters = list(string.lowercase)
	letters += ['0-9']
	
	if letter_var == "0-9":
		# Keyword.objects.exclude(keyword__regex=r'^[a-zA-Z]')
		data = Koncept.objects.exclude(name__regex=r'^[a-zA-Z]')
	else:
		data = Koncept.objects.filter(name__istartswith=letter_var)
	return render_to_response(BOOTSTRAP + 'test/test-konlist-table.html',	
							{ 
							  'data': data,		
							  'letters' : letters,	
							  'active_letter' : letter_var,
							},
							context_instance=RequestContext(request))
							



							
def konlist_tree(request):
	"""
	returns a list of koncepts as a tree
	"""
		
	return render_to_response(BOOTSTRAP + 'test/test-konlist-tree.html',	
							{ 'data': [],},
							context_instance=RequestContext(request))
							

def ajax_konlist_tree(request):
	"""
	ajax loader : https://github.com/gilek/bootstrap-gtreetable#configuration
	example json: http://gtreetable2.gilek.net/index.php?r=site%2FnodeChildren&id=0
	
	{"nodes":
		[
			{"id":4070,"name":"123.","level":0,"type":"default"},
			{"id":4100,"name":"asd","level":0,"type":"default"}
		]
	}	
	"""
	_id = request.GET.get('id', None)		

	response_data = {'nodes' : []}
		
	if _id == '0':
		data = Subject.tree.root_nodes().filter(created_by=request.user)[:30]
	else:
		try:
			s = Subject.objects.get(pk=int(_id), created_by=request.user)
			data = s.get_children()
		except:
			raise Http404
		
	for el in data:
		obj_data = {}
		obj_data['id'] = el.id
		obj_data['name'] = """<a class="kon_list_item konceptcolor underline" href="%d">%s</a>""" % (el.id, el.name)	#el.get_absolute_url()			
		obj_data['level'] = el.level				
		obj_data['type'] = 'default' 

		response_data['nodes'] += [obj_data]
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")						
								


def ajax_konlist_create(request):
	"""
	nb this works for both CREATE and UPDATE actions
	""" 
	_id = request.GET.get('id', None) # only for update
	_idDestination = request.GET.get('related', None)		
	_position = request.GET.get('position', '')
	_name = request.GET.get('name', '')

	# print request.GET	  # should be POST data, but here we are testing....
	response_data = {}
	
	if _id and _name:
		# it's an UPDATE
		try:
			s = Subject.objects.get(id = int(_id), created_by=request.user)
			s.name = _name			
			s.save()
							
			obj_data = {}
			obj_data['id'] = s.id
			obj_data['name'] = """<a class="kon_list_item konceptcolor underline" href="%d">%s</a>""" % (s.id, s.name)	#el.get_absolute_url()			
			obj_data['level'] = s.level				
			obj_data['type'] = 'default'
		
			response_data = obj_data
		
		except:
			raise Http404
	
	elif _idDestination and _name:
		# it's	CREATE
		try:
			s = Subject(name = _name, created_by=request.user)
			destination = Subject.objects.get(pk=int(_idDestination), created_by=request.user)
		
			if _position == "lastChild":
				_position = "last-child"		
			elif _position == "firstChild":
				_position = "first-child"
			elif _position == "before":
				_position = "left"
			elif _position == "after":
				_position = "right"						
		
			s.save()	
			s.move_to(destination, _position)
		
			obj_data = {}
			obj_data['id'] = s.id
			obj_data['name'] = """<a class="kon_list_item konceptcolor underline" href="%d">%s</a>""" % (s.id, s.name)	#el.get_absolute_url()			
			obj_data['level'] = s.level				
			obj_data['type'] = 'default'
		
			response_data = obj_data
		
		except:
			raise Http404
		
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")						






def ajax_konlist_move(request):
	"""
	https://django-mptt.github.io/django-mptt/models.html#insert-at-target-position-first-child-save-false
	"""
	_id = request.GET.get('id', None)		
	_idDestination = request.GET.get('related', None)		
	_position = request.GET.get('position', '')
		
	# print request.GET	  # should be POST data, but here we are testing....
	response_data = {'nodes' : []}
	
	try:
		s = Subject.objects.get(pk=int(_id), created_by=request.user)
		destination = Subject.objects.get(pk=int(_idDestination), created_by=request.user)
		
		if _position == "lastChild":
			_position = "last-child"		
		elif _position == "firstChild":
			_position = "first-child"
		elif _position == "before":
			_position = "left"
		elif _position == "after":
			_position = "right"						
			
		s.move_to(destination, _position)
		
		obj_data = {}
		obj_data['id'] = s.id
		obj_data['name'] = """<a class="kon_list_item konceptcolor underline" href="%d">%s</a>""" % (s.id, s.name)	#el.get_absolute_url()			
		obj_data['level'] = s.level				
		obj_data['type'] = 'default'
		
		response_data['nodes'] += [obj_data]
		
	except:
		raise Http404
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")						
		



def ajax_konlist_delete(request):
	"""
	"""
	_id = request.GET.get('id', None)		

	# print request.GET	  # should be POST data, but here we are testing....
	# response_data = {}
	
	response_data = {'nodes' : []}

	try:
		s = Subject.objects.get(pk=int(_id), created_by=request.user)
		print "Deleting %s" % s
		s.delete()				
		# @todo update interpretations etc...
	except:
		raise Http404

	
	return HttpResponse(json.dumps(response_data), content_type="application/json")						
	


#
# END OF TREE DEMO
#





							
def taglist(request):
	"""
	2015-12-01
	returns a list of all tags

	"""
	user = request.user
	data = Subject.subjectsListPerUser(user).order_by('name')

	return render_to_response(BOOTSTRAP + 'test/test-taglist.html', 
							{ 
							  'data': data,		
							},
							context_instance=RequestContext(request))
	


		
							
def konlist(request):
	"""
	returns a list of recent koncepts formatted very simply
	
	@todo
	- list of letters should be inferred or statically typed with many disabled
	- default letter should be inferred from dataset
	"""
	
	letter_var = request.GET.get('start', 'a')
	
	letters = list(string.lowercase)
	letters += ['0-9']
	
	if letter_var == "0-9":
		# Keyword.objects.exclude(keyword__regex=r'^[a-zA-Z]')
		data = Koncept.objects.exclude(name__regex=r'^[a-zA-Z]')
	else:
		data = Koncept.objects.filter(name__istartswith=letter_var)
	return render_to_response(BOOTSTRAP + 'test/test-konlist.html', 
							{ 
							  'data': data,		
							  'letters' : letters,	
							  'active_letter' : letter_var,
							},
							context_instance=RequestContext(request))
	



def doclist(request):
	"""
	returns a list of recent documents formatted very simply
	
	"""
	
	# letter_var = request.GET.get('start', 'a')
	
	data = Document.objects.all()[:100]
	return render_to_response(BOOTSTRAP + 'test/test-doclist.html', 
							{ 
							  'data': data,		
							  # 'letters' : string.lowercase,
							  # 'active_letter' : letter_var,
							},
							context_instance=RequestContext(request))
	


def tilesdocs(request):
	"""
	returns a list of recent documents in a tile format
	http://www.bootply.com/kmqk8tgYvF
	http://stackoverflow.com/questions/26765464/how-to-use-bootstrap-3-grid-if-elements-are-tiled-with-different-height-and-widt
	
	"""
	
	# letter_var = request.GET.get('start', 'a')
	
	data = Document.objects.all()[:100]
	return render_to_response(BOOTSTRAP + 'test/test-tilesdocs.html',	
							{ 
							  'data': data,		
							  # 'letters' : string.lowercase,
							  # 'active_letter' : letter_var,
							},
							context_instance=RequestContext(request))
	



def masonry(request):
	"""

	
	"""
	
	# letter_var = request.GET.get('start', 'a')
	
	data = Fragment.objects.all().order_by('created_at')[:20]
	return render_to_response(BOOTSTRAP + 'test/test-masonry.html',	
							{ 
							  'data': data,		
							},
							context_instance=RequestContext(request))
	





def sourceSummary(request):
	"""

	
	"""
	
	test_source = Document.objects.get(pk=715) # ego trick
	# letter_var = request.GET.get('start', 'a')

	return render_to_response(BOOTSTRAP + 'test/test-sourcesummary.html',	
							{ 
							  'source': test_source,		
							},
							context_instance=RequestContext(request))
	









# ===========
# visualizations
# ===========



def test_visjs(request):
	"""
	test viz using visjs
	"""
	from django.utils import simplejson
	a_koncept = Koncept.objects.get(pk=38) # ontology Koncept 897

	
	def addBRspace(stringa):
		SIZE = 3
		ss = stringa.split()
		return '\n'.join(' '.join(ss[pos:pos+SIZE]) for pos in xrange(0, len(ss), SIZE))
	
	
	if True:
		# only koncepts similar, at 2 levels 
		nodes  = [] 
		edges  = []
		INDEX = [a_koncept.id] #hack to keep track of what's in there already - the js libs fails otherwise
	
		rootid = "k_"+ str(a_koncept.id)
		top = {'id' : rootid, 'label' : a_koncept.name, 'group' : 'group_root'}
		nodes += [top]
	
		for x in a_koncept.getSimilarKoncepts():
			if x.id not in INDEX:
				INDEX += [x.id]
				nodes += [{'id' : x.id, 'label' : addBRspace(x.name), 'group' : 'group_koncept'}]
				edges += [{'from' : rootid, 'to' : x.id, 'label' : "similar to"}]
	
				for x1 in x.getSimilarKoncepts():
					if x1.id not in INDEX:
						INDEX += [x1.id]
						nodes += [{'id' : x1.id, 'label' : addBRspace(x1.name), 'group' : 'group_koncept'}]
					edges += [{'from' : x.id, 'to' : x1.id, 'label' : "similar to" }]
			

	if True:
		# koncept sources + their related koncepts
		nodes1	= [] 
		edges1	= []
	
		rootid = "k_"+ str(a_koncept.id)
		INDEX1 = [rootid] #hack to keep track of what's in there already - the js libs fails otherwise
		top = {'id' : rootid, 'label' : a_koncept.name, 'group' : 'group_root'}
		nodes1 += [top]
	
		for s in a_koncept.getSources():
			sid = "s_"+ str(s.id)
			nodes1 += [{'id' : sid, 'label' : addBRspace(s.title), 'group' : 'group_source'}]
			edges1 += [{'from' : rootid, 'to' : sid, 'label' : "from"}]
			
			for k in s.get_koncepts():
				kid = "k_"+ str(k.id)
				if kid != rootid:
					if kid not in INDEX1:
						INDEX1 += [kid]					
						nodes1 += [{'id' : kid, 'label' : addBRspace(k.name), 'group' : 'group_koncept'}]
					edges1 += [{'from' : sid, 'to' : kid, 'label' : "includes"}]
	
	
	return render_to_response(BOOTSTRAP + 'test/test-visjs.html',	 # based on one above
							{ 
							  'nodes': simplejson.dumps(nodes),
							  'edges': simplejson.dumps(edges), 
							  'nodes1': simplejson.dumps(nodes1),
							  'edges1': simplejson.dumps(edges1),					
							},
							context_instance=RequestContext(request))




def test_jit(request):
	"""
	test viz using jit
	"""
	from django.utils import simplejson
	
	# get a koncept for this test
	a_koncept = Koncept.objects.get(pk=38) # ontology Koncept
	
	
	if True:
		# 1) get related koncepts recursively 
		#  COULD WORK
		def nav_tree(el, level=None):
			if level==None:
				level = 1
			d = {}
			d['id'] =  el.id
			d['name'] = el.name
			# full_ogden = generate_text(el)
			# preview_ogden = "%s .." % ' '.join(el.textOgden().split()[:10]).replace("div", "span")
			d['data'] = {'url' : el.get_absolute_url()}
			if level < 2: # and el.get_children() and not TESTING:			
				d['children'] = [nav_tree(x, level+1) for x in el.getSimilarKoncepts()]
			else:
				d['children'] = []
			return d
			
		tree = {'id': a_koncept.id, 'name': a_koncept.name, 'children': [],	 'data': {'url' : a_koncept.get_absolute_url()}}

		for x in a_koncept.getSimilarKoncepts():
			tree['children'] += [nav_tree(x)]
	
	
	if False:
		#2) get koncept, interpretation sources, then more koncepts
		# TOO MESSY
		
		tree = {'id': a_koncept.id, 'name': a_koncept.name, 'children': [], }
		
		for x in a_koncept.getSources():
			d = {} 
			d['id'] =  x.id
			d['name'] = x.title
			d['children'] = []
			for k in x.get_koncepts():
				g = {} 
				g['id'] =  k.id
				g['name'] = k.name
				g['children'] = []
				d['children'] += [g]
			tree['children'] += [d]
		
	return render_to_response(BOOTSTRAP + 'test/test-jit.html',	 # based on one above
							{'json': simplejson.dumps(tree), 'k1' : a_koncept},
							context_instance=RequestContext(request))









							
							
