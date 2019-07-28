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
from django.contrib.auth.models import User
# from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from datetime import *
from koncepts.models import *
from myutils.myutils import split_list
from settings import printdebug, BOOTSTRAP

# from koncepts.tag import get_tag_cloud	
from koncepts.forms import *









def inbox(request, username):
	"""
	""" 
	person = get_object_or_404(User, username=username)
	
	context = {'person' : person} # initialize context
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
	else:
		context['mykoncepts'] = False
		raise Http404
		
	return render_to_response(BOOTSTRAP + 'tools/inbox.html',
							context,
							context_instance=RequestContext(request))








def comments(request, username):
	"""
	""" 
	person = get_object_or_404(User, username=username)
	
	context = {'person' : person} # initialize context
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
	else:
		context['mykoncepts'] = False
		raise Http404
		
	return render_to_response(BOOTSTRAP + 'tools/comments.html',
							context,
							context_instance=RequestContext(request))










def settings(request, username):
	"""
	""" 
	person = get_object_or_404(User, username=username)
	user = request.user
	context = {'person' : person} # initialize context
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
	else:
		context['mykoncepts'] = False
		raise Http404


	# 
	# edit action: form has been passed							
	#		
	
	if request.method == 'POST': 
		# If the form has been submitted... 

		form = SettingsForm(request.POST)

		if form.is_valid():

			# do something 
			
			privateKonceptDefault = form.cleaned_data['privateKonceptDefault']
			privateUser = form.cleaned_data['privateUser']
						
			user.profile.defaultPrivate = privateUser
			user.profile.defaultPrivateKoncepts = privateKonceptDefault

			user.profile.save()
			
			context.update({	  
						'form' : form,
						'success' : True, 
						})
										
			return render_to_response(BOOTSTRAP + 'tools/settings.html',
									context,
									context_instance=RequestContext(request))

	# 
	# if not POST action or form isn't valid ===>  form is created							
	#


	if not request.method == 'POST':
		default_values = {}
		
		default_values['privateUser'] = user.profile.defaultPrivate
		default_values['privateKonceptDefault'] = user.profile.defaultPrivateKoncepts
		
		form = SettingsForm(initial=default_values)


	context.update({	  
				'form' : form,
				})
						
	return render_to_response(BOOTSTRAP + 'tools/settings.html',
							context,
							context_instance=RequestContext(request))
							
							
							


@login_required
def profile(request, username):
	"""
	Edits a user profile
	"""

	person = get_object_or_404(User, username=username)
	
	context = {'person' : person} # initialize context
	
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
		user = person
	else:
		context['mykoncepts'] = False
		raise Http404
				
	# 
	# edit action: form has been passed							
	#		
	
	if request.method == 'POST': 
		# If the form has been submitted... 

		form = ProfileForm(request.POST)

		if form.is_valid():

			# do something 
			
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			timezone = form.cleaned_data['timezone']
			
			if first_name:
				user.first_name = first_name
			if last_name:
				user.last_name = last_name
			if first_name or last_name:
				user.save()
			
			
			profile = user.profile
				
			if timezone:
				profile.timezone = timezone
				profile.save()

			context.update({	  
						'form' : form,
						'success' : True, 
						})
										
			return render_to_response(BOOTSTRAP + 'tools/profile.html',
									context,
									context_instance=RequestContext(request))

	# 
	# if not POST action or form isn't valid ===>  form is created							
	#


	if not request.method == 'POST':
		default_values = {}
		
		# NB: username and email are taken directly in the template, outside the form instance (cause they are not editable)

		default_values['first_name'] = user.first_name
		default_values['last_name'] = user.last_name
		default_values['timezone'] = user.profile.timezone
		
		form = ProfileForm(initial=default_values)


	context.update({	  
				'form' : form,
				})
				
	return render_to_response(BOOTSTRAP + 'tools/profile.html', 
							context,
							context_instance=RequestContext(request))


		
									
							
						
							
