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
# SEARCH VIEW
# 


@login_required
def search_subject(request, username, collection=""):
	"""
	main view for subject search page	
	"""

	# get init values
	return redirect('subject_list', username=username)
	
	




# 
# LIST VIEW
# 




@login_required
def subject_list(request, username):
	"""
	returns a list of subjects in one sinegle html page
	"""	
	person = get_object_or_404(User, username=username)	
	context = {'person' : person} # initialize context
	# get init values
	searchdict = {}
	qset = Subject.objects.filter()
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
		searchdict['created_by'] = request.user
		context['totcount'] = qset.filter(**searchdict).count()

	else:
		context['mykoncepts'] = False
		raise Http404
	
	# finally...
	data = qset.filter(**searchdict).distinct().order_by('name')
	context.update({	  
				'page_flag' : "searchsubjects",  # x dynamic top menu
				'data' : data,
				})		

	return render_to_response(BOOTSTRAP + 'pages/search_subjects_list.html',	
							context,
							context_instance=RequestContext(request))
							





	
	


# 
# ALPHA VIEW
# 




@login_required
def subject_detail(request, username, collection=""):
	"""
	main view for subject search page	
	"""

	# get init values
	searchdict = {}
	qset = Subject.objects.filter()
		
	searchval = request.GET.get('q', "") 	
	sort_var = request.GET.get('sort', 'alpha')
	if sort_var not in ['alpha', 'modified', 'created']: sort_var = 'alpha'
	sorting = {'alpha' : ["name", "-updated_at"], 
				'modified': ["-updated_at", "name"], 
				'created': ["-created_at", "name"]} [sort_var]				
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

	
	if not searchval:
		# displaying all 
		letters = list(qset.filter(**searchdict).order_by('first_letter').values_list('first_letter', flat=True).distinct())	
	
		if letters:  # = if there's contents at all
			if letters[0] == "*":
				letters.append(letters.pop(0))
	
			if not letter_var:
				letter_var = letters[0] # if not passed, default to first letter available
		
		totcount = Subject.objects.filter(**searchdict).distinct().count()
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


	template_name = BOOTSTRAP + 'pages/search_subjects_detail.html'
	data.totcount = totcount
			
	# finally...
	context.update({	  
				'searchval' : searchval, 
			    'letters' : letters,	
			    'active_letter' : letter_var,
				'page_object' : data,
				'page_flag' : "searchsubjects",  # x dynamic top menu
				})
	return render_to_response(template_name, 
							context,
							context_instance=RequestContext(request))







# 
# TREE STUFF
# 



@login_required
def subject_tree(request, username):
	"""
	returns a list of koncepts as a tree
	"""	
	person = get_object_or_404(User, username=username)	
	context = {'person' : person} # initialize context
	# get init values
	searchdict = {}
	qset = Subject.objects.filter()
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
		searchdict['created_by'] = request.user
		context['totcount'] = qset.filter(**searchdict).count()

	else:
		context['mykoncepts'] = False
		raise Http404
	
	# finally...
	context.update({	  
				'page_flag' : "searchsubjects",  # x dynamic top menu
				})		

	return render_to_response(BOOTSTRAP + 'pages/search_subjects_tree.html',	
							context,
							context_instance=RequestContext(request))
							




@login_required
def ajax_subject_tree(request, username):
	"""
	ajax function calles by bootstrap-tree to load the hierarchy
	
	docs ajax loader : https://github.com/gilek/bootstrap-gtreetable#configuration
	example json: http://gtreetable2.gilek.net/index.php?r=site%2FnodeChildren&id=0
	
	needs to return something like this: 
	
	{"nodes":
		[
			{"id":4070,"name":"123.","level":0,"type":"default"},
			{"id":4100,"name":"asd","level":0,"type":"default"}
		]
	}	
	
	"""

	_id = request.GET.get('id', None)		
	response_data = {'nodes' : []}
	
	person = get_object_or_404(User, username=username)	
	context = {'person' : person} # initialize context
	searchdict = {}
	qset = Koncept.objects.filter()
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
		searchdict['created_by'] = request.user
	else:
		context['mykoncepts'] = False
		raise Http404
				
	if _id == '0':
		data = Subject.tree.root_nodes().filter(created_by=request.user)
	else:
		try:
			s = Subject.objects.get(pk=int(_id), created_by=request.user)
			data = s.get_children()
		except:
			raise Http404
		
	for el in data:
		obj_data = {}
		obj_data['id'] = el.id
		# obj_data['name'] = """<a class="kon_list_item konceptcolor underline" href="%d">%s</a>""" % (el.id, el.name)	#el.get_absolute_url()
		obj_data['name'] = """%s""" % (el.name)	#el.get_absolute_url()
		obj_data['level'] = el.level
		obj_data['type'] = 'default' 

		response_data['nodes'] += [obj_data]
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")						
								

@login_required
def ajax_subject_create(request, username):
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
			obj_data['name'] = """%s""" % (el.name)
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
			obj_data['name'] = """%s""" % (s.name)
			obj_data['level'] = s.level
			obj_data['type'] = 'default'
		
			response_data = obj_data
		
		except:
			raise Http404
		
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")						





@login_required
def ajax_subject_move(request, username):
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
		obj_data['name'] = """%s""" % (s.name)
		obj_data['level'] = s.level
		obj_data['type'] = 'default'
		
		response_data['nodes'] += [obj_data]
		
	except:
		raise Http404
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")						
		


@login_required
def ajax_subject_delete(request, username):
	"""
	cf https://django-mptt.github.io/django-mptt/mptt.models.html#mptt.models.MPTTModel.delete
	
	Calling delete on a node will delete it as well as its full subtree, as opposed to reattaching all the subnodes to its parent node.
	
	"""
	_id = request.GET.get('id', None)		

	# print request.GET	  # should be POST data, but here we are testing....
	# response_data = {}

	try:
		s = Subject.objects.get(pk=int(_id), created_by=request.user)
	except:
		raise Http404

	response_data = {'nodes' : [], 'first_letter' : s.first_letter }
	# note: the delete method contains logic to remove m2m relationships to fragmets for this subject and its descendants
	s.delete()

	return HttpResponse(json.dumps(response_data), content_type="application/json")						
	


#
# END OF TREE 
#




	



							
							
