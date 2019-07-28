#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	tools views
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from myutils.myutils import paginator_helper, truncate_words
from django.contrib.auth.models import User

from django.utils.safestring import mark_safe


from StringIO import StringIO

from koncepts.models import *
from koncepts.forms import *


from settings import printdebug, BOOTSTRAP

from datetime import datetime

from django import forms
from django.forms.formsets import formset_factory



@login_required
def bookmarklet(request):
	"""
	""" 
	person = request.user
	
	context = {'person' : person, 'mykoncepts' : True} # initialize context

	bookmarklet_dynamic = "http://%s%s"	 % (request.get_host(), reverse('addonthefly'))

	context.update({'bookmarklet' : bookmarklet_dynamic , 'page_flag' : 'new', })
		
	return render_to_response(BOOTSTRAP + 'tools/bookmarklet.html',
							context,
							context_instance=RequestContext(request))



