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

from django.db.models import Q

import operator, datetime, calendar

from myutils.myutils import paginator_helper
from koncepts.models import *
from settings import printdebug, BOOTSTRAP
from koncepts.importKindle import importFileExists





	
		
@login_required
def person_dashboard(request, username):
	""" 
	Private view for the person dashboard.	
	2015-03-10: separated from private profile
	"""
	
	person = get_object_or_404(User, username=username)
	
	context = {'person' : person} # initialize context
		
	if request.user and request.user.is_authenticated() and person.username == request.user.username:
		context['mykoncepts'] = True
		user = person
	else:
		raise Http404

	
		
	# get some useful info for the person
	
	if False:
		context.update({'totKoncepts' : person.profile.get_koncepts(onlypublic=False, count=True)})
		context.update({'totDocuments' : person.profile.get_documents(onlypublic=False, count=True)})
		context.update({'totFrags' : person.profile.get_fragments(onlypublic=False, count=True)})
	
	# context.update({'tagCloud' : person.profile.get_tags_cloud()})

	# popularKoncepts = person.profile.get_koncepts(onlypublic=False, count=False, ordering="popular")[:MAX]
	# popularDocuments = person.profile.get_documents(onlypublic=False, count=False, ordering="popular")[:MAX]
	context.update({'recentKoncepts' : person.profile.get_koncepts(onlypublic=False, count=False, ordering="created")[:15]})
	context.update({'recentDocuments' : person.profile.get_documents(onlypublic=False, count=False, ordering="created")[:15]})
	context.update({'recentSnippets' : person.profile.get_fragments(onlypublic=False, count=False, ordering="created")[:10]})

	if importFileExists(username, "kindle"):
		context.update({'previousKindleImport': True })
	
	context.update({'creationStats' : _getStats(person)})
		

	return render_to_response(BOOTSTRAP + 'pages/person_dashboard.html', 
							context,
							context_instance=RequestContext(request))







def person_public_page(request, username):
	""" 
	View that shows only PUBLIC info on a person	
	2015-03-10: separated from person dashboard
	"""
	
	person = get_object_or_404(User, username=username)
	# if person.userprofile__defaultPrivate == True:
	#	raise Http404
	
	MAX = 14
	
	context = {'person' : person} # initialize context
	context['mykoncepts'] = False  # always view as if content isn't mine

	context.update({'recentKoncepts' : person.profile.get_koncepts(onlypublic=True, count=False, ordering="created")[:MAX]})
	context.update({'recentDocuments' : person.profile.get_documents(onlypublic=True, count=False, ordering="created")[:MAX]})
	context.update({'recentSnippets' : person.profile.get_fragments(onlypublic=True, count=False, ordering="created")[:MAX]})
			

	return render_to_response(BOOTSTRAP + 'pages/person_public_page.html', 
							context,
							context_instance=RequestContext(request))












def people_list(request):
	"""
	Lists all users of the site - public view
	"""

	# get init values
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1


	# note: users with private only fragments here are listed @todo better query
	qset = User.objects.exclude(created_fragment=None).exclude(userprofile__defaultPrivate=True).distinct().order_by('-date_joined')
	
	
	# qset = [u for u in qset if u.profile.get_fragments(onlypublic=True, count=True)]
	

	# present data
	paginator = Paginator(qset, 30)
	try:
		page_object = paginator.page(page)
	except (EmptyPage, InvalidPage):  # If page request is out of range, deliver last page of results.
		page_object = paginator.page(paginator.num_pages)
	page_object.extrastuff = paginator_helper(page, paginator.num_pages)
	page_object.totcount = paginator.count

	template_name = BOOTSTRAP + 'pages/people_list.html'

	# finally...
	context = {	  
				'page_object' : page_object,
				}
	return render_to_response(template_name, 
							context,
							context_instance=RequestContext(request))






def _getStats(user):
	"""
	returns stats on number of entities over time in this format (for c3 graph)
	
    ['data1', 30, 20, 50, 40, 60, 50],
    ['data2', 200, 130, 90, 240, 130, 220],
    ['data3', 300, 200, 160, 400, 250, 250]
	
	"""

	if False:  # testing
		return {'quotes' : [30, 20, 50, 40, 60, 50], 
				'collections' : [200, 130, 90, 240, 130, 220],
				'documents' : [300, 200, 160, 400, 250, 250],
				}
	else:
		
		# construct a series of dates going back month by month 
		# min 2 dates - then add only if user.date_joined is <
		seed_date = datetime.date.today()
		dates_list = []
		for x in range(15):
			if x == 0:
				dates_list.insert(0, seed_date)
			else:
				date = seed_date - datetime.timedelta(seed_date.day)
				if x > 1:
					if user.date_joined.date() <= date:
						dates_list.insert(0, date)
						seed_date = date
				else:
					dates_list.insert(0, date)
					seed_date = date
		

		# bootstrap return dict
		d = {'data' : [], 'categories' : []}
		d['data'] = {'quotes' : [], 'collections' : [], 'documents' : []}	
		
		# in each case, keep summing counts up
		for x in dates_list:
				
			if d['data']['quotes']:	
				c = Fragment.objects.filter(created_by=user, created_at__month=x.month, created_at__year=x.year ).count()		
				d['data']['quotes'].append(c + d['data']['quotes'][-1])
			else:
				# only first time, get the total up to that month
				last_day_of_month = calendar.monthrange(x.year, x.month)[1]
				new_date = datetime.date(x.year, x.month, last_day_of_month) 
				c = Fragment.objects.filter(created_by=user, created_at__lte=new_date).count()
				d['data']['quotes'].append(c)
			
						
			if d['data']['collections']:	
				c = Koncept.objects.filter(created_by=user, created_at__month=x.month, created_at__year=x.year ).count()		
				d['data']['collections'].append(c + d['data']['collections'][-1])
			else:
				last_day_of_month = calendar.monthrange(x.year, x.month)[1]
				new_date = datetime.date(x.year, x.month, last_day_of_month)
				c = Koncept.objects.filter(created_by=user, created_at__lte=new_date).count()
				d['data']['collections'].append(c)
								
						
			if d['data']['documents']:			
				c = Document.objects.filter(created_by=user, created_at__month=x.month, created_at__year=x.year ).count()
				d['data']['documents'].append(c + d['data']['documents'][-1])
			else:
				last_day_of_month = calendar.monthrange(x.year, x.month)[1]
				new_date = datetime.date(x.year, x.month, last_day_of_month)
				c = Document.objects.filter(created_by=user, created_at__lte=new_date).count()
				d['data']['documents'].append(c)

		# finally, fill in the categories
		d['categories'] = ["%s-%02d" % (x.year, x.month) for x in dates_list]
			
		return d





def __recentKonceptsChart(request, username):
	"""
	@todo: April 3, 2014 copied code from the old dashboard function
	=======needs to be revised....========
		May 7, 2014: did some updates
	"""
	
	person = get_object_or_404(User, username=username)
	recentKoncepts = [] 
			
	searchdict = {}
	searchdict['created_by'] = request.user
	
	RECENT_CONTENT_FRAME = 14  # in days
	today = datetime.today()
	timeframe = today - timedelta(days=RECENT_CONTENT_FRAME)
	MINIMUM_KONCEPTS_SIZE = 10	# in num of items

	koncepts = Koncept.objects.filter(**searchdict).distinct().count()
	
	if koncepts:
		recentKoncepts = Koncept.objects.filter(**searchdict).filter(updated_at__gt=timeframe).distinct().order_by("-updated_at")	
		if len(recentKoncepts) < MINIMUM_KONCEPTS_SIZE: 
			recentKoncepts = Koncept.objects.filter(**searchdict).distinct().order_by("-updated_at")[:MINIMUM_KONCEPTS_SIZE]
		lastKoncept = list(recentKoncepts)[-1]
		delta = today - lastKoncept.created_at
		weeks = delta.days / 7
		tot = len(recentKoncepts)

		konceptsStat = "%d Koncept%s updated in the last %s week%s, %d in total" % (tot, 
			"s"[tot==1:], str(weeks) if weeks > 1 else "", "s"[weeks==1:], koncepts)

	return recentKoncepts











