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

from myutils.myutils import paginator_helper

from koncepts.models import *

from myutils.myutils import split_list
from settings import printdebug, BOOTSTRAP

		
from koncepts.forms import *


#
# 
#

def homepage(request):
	"""
	Homepage: shows the banner, info and login/out/register info
	
	If a user is logged in, by default he's redirected to his personal home page. 
	However if a GET param <f> is passed, we return the global homepage.  
	"""
	
	forcehomepage = request.GET.get('f', None)
	
	if not forcehomepage and request.user.is_authenticated():
		return redirect('search_user_quotes', username=request.user.username)

	else:
		return render_to_response(BOOTSTRAP + 'splashpage.html', 
								{'splashpage' : True},
								context_instance=RequestContext(request))		





def person_home(request, username):
	"""
	Person homepage: a shortcut dispatcher. 
	
	If a user is logged in, by default it redirects to his private dashboard. 
	Otherwise we return the public homepage.  
	"""
	
	person = get_object_or_404(User, username=username)

	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		return redirect('search_user_quotes', username=request.user.username)
	else:
		return redirect('person_public_page', username=person.username)

								
								
								
								


				

def dispatcher(request):
	"""
	Generic view pointing to templates in <templates-global> folder
	"""
	
	this_context = {}
	
	if "toc" in request.path:
		template = BOOTSTRAP + 'siteinfo/toc.html'
	elif "faq" in request.path:
		this_context['faqs'] = FAQitem.objects.all()
		template = BOOTSTRAP + 'siteinfo/faq.html'
	elif "about" in request.path:
		template = BOOTSTRAP + 'siteinfo/about.html'
	elif "help" in request.path:
		template = BOOTSTRAP + 'siteinfo/help.html'

						
	return render_to_response(template, 
								this_context,
								context_instance=RequestContext(request))	














							
							
