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

from django.contrib import messages
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

import os.path
from StringIO import StringIO

from koncepts.models import *
from koncepts.forms import *
from koncepts.importUtils import *

from myutils.myutils import monoSpacedString

from settings import printdebug, BOOTSTRAP, MEDIA_ROOT

from datetime import datetime

from django import forms
from django.forms.formsets import formset_factory






# ===========
# KINDLE STUFF
# ===========




@login_required
def importkindle(request):
	"""
	View that either displays the kindle import homepage or the list of documents extracted from a kindle highlights file
	
	"""
	form, documents_list, filepath =  None, [], None
	person = request.user
	username = person.username
	context = {'person' : person, 'mykoncepts' : True} # initialize context
			
	if request.method == 'POST':
		# print "POST OK"
		form = ImportFileForm(request.POST, request.FILES)
		if form.is_valid():
			# print "FORM OK"
			# get the data to parse and save them to a file
			
			if request.FILES.has_key('file'):
				if request.FILES['file'].multiple_chunks():
					pass	 # @todo: see above
				else:
					filepath = saveTmpFile(request.FILES['file'], username, "kindle")
					
			elif form.cleaned_data['text']:
				filepath = saveTmpFile(StringIO(form.cleaned_data['text']), username, "kindle")
			
			# step 1: try to extract only the list of documents
			
			if filepath:	
				# print "Filepath OK"		
				documents_list = extract_kindle(open(filepath))
			
			# check that the contents are good
			
			if documents_list:
				template_name = 'tools/importkindle_select_doc.html'
				# _message = "This Kindle highlights file contains %d document%s" % (len(documents_list), "s"[len(documents_list)==1:])
				# messages.success(request, _message)	
			else:
				template_name = 'tools/importkindle.html'
				_message = "Sorry. Could not find any Kindle highlights!"	
				messages.error(request, _message)

		
	if not form:
		template_name = 'tools/importkindle.html'
		form = ImportFileForm()
		if importFileExists(username, "kindle"):
			context.update({'previousKindleImport': True })
		
	context.update({'form': form , 
					'documents_list' : documents_list,
					'page_flag' : "kindle",  # x dynamic top menu
				})

	request.session['documents_list'] = documents_list
		
	return render_to_response(BOOTSTRAP + template_name,
							context,
							context_instance=RequestContext(request))




def getLatestKindleImport(request):
	"""
	"""
	form, documents_list, filepath =  None, [], None
	person = request.user
	username = person.username
	context = {'person' : person, 'mykoncepts' : True} # initialize context

	pathtofile = getTmpFile(username, "kindle")

	if pathtofile and importFileExists(username, "kindle"):	
		# print "Filepath OK: %s" % pathtofile
		documents_list = extract_kindle(open(pathtofile))
	else:
		return HttpResponseRedirect(reverse('importkindle' ,))
	
	# check that the contents are good
	
	if documents_list:
		template_name = 'tools/importkindle_select_doc.html'
		# _message = "This Kindle highlights file contains %d document%s" % (len(documents_list), "s"[len(documents_list)==1:])
		# messages.success(request, _message)
	else:
		template_name = 'tools/importkindle.html'
		_message = "Sorry. Could not find any Kindle highlights!"	
		messages.error(request, _message)
		
					
	context.update({'documents_list' : documents_list,
					'page_flag' : "kindle",  # x dynamic top menu
				})
	request.session['documents_list'] = documents_list
	return render_to_response(BOOTSTRAP + template_name,
							context,
							context_instance=RequestContext(request))





def extract_kindle(filename, whichBook=False, user=None):
	"""
	Algo: read the file and accumulates the text into a buffer till it finds the "=======" line. 
	Then processes the buffer.	
	
	FORMAT:
	# <Book Title>	
	# - Your Highlight on Page <numbers> | Added on Saturday, August 4, 2012 4:03:10 PM
	# 
	# <highlight content in single line>
	# ==========
	"""

	lineBuffer = []
	# books = {}
	BAG = []
	
	lines = filename.read().splitlines()
	for line in lines:
		if line == "==========":
			res = process_kindle_contents(lineBuffer, whichBook, user)
			if res:
				if whichBook:
					# in this case a list with a a dict inside
					BAG += res	
				else:
					if res not in BAG:	 
						# in this case a single item - no duplicates!
						BAG += [res] 
			lineBuffer = []
		else:
			if line:
				lineBuffer += [line.strip()]
		
	# eventually
	if not whichBook:
		# BAG = sorted(BAG)
		BAG.reverse()
		
	return BAG


def process_kindle_contents(lineBuffer, whichBook, user):
	"""
	Util that extract data already grouped by highlight unit
	If whichBook is passed, it returns the highlights. Otherwise it just returns a list of books.
	"""
	# print " ** ".join([x for x in lineBuffer])
	
	if len(lineBuffer) == 3:	
				
		page = lineBuffer[1].split("|")[0].strip()
		# removes the standard location text - warning: it may change in the future
		standardText = "- Your Highlight Location "
		if page.find(standardText) == 0:
			page = page.replace(standardText, "")
		
		date = lineBuffer[1].split("|")[1].strip()
		standardText = "Added on "
		if date.find(standardText) == 0:
			date = date.replace(standardText, "")					
			try: # try parsing the date into a datetime obj; fails silently
				date=dparser.parse(date) 
			except: 
				pass
		
		# July 30, 2014: found out that titles with more than one space in-between words caused a bug
		book = monoSpacedString(lineBuffer[0]) 
		
		if whichBook:
			# extract all snippets from a specific book
			if force_unicode(book) == force_unicode(whichBook):
				
				if True:
					page = "%s (Kindle highlight location)" % page	# add page info
				if True:
					txt = lineBuffer[2].strip() # July 30, 2014: no page number
				if False:
					kon = truncate_words(txt, 6) #simulate a kon name  # June 23, 2014: DEPRECATED			
				# date not being used at the moment				
				# return [{'name' : kon, 'frag' : txt, 'source' : book}]
				duplicates_info = alreadyExistingFrag(txt, user)
				
				# note: these keywords map directly to the form fields names!
				return [{'name' : "", 
						'frag' : txt, 
						'location' : page, 
						'source' : book, 
						'duplicates_info' : duplicates_info}]
						
						
			else:
				return None
		else:

			# just return the book information
			return force_unicode(book)	



@login_required
def previewDocumentImport(request):
	"""
	After a document has been selected, this function extracts all the snippets 
	from it using again the <extract_kindle> function.
	"""
		
	form, contents =  None, None

	person = request.user
	username = person.username
	
	context = {'person' : person, 'mykoncepts' : True} # initialize context
	
	doc = request.GET.get('d', None) 
	timestamp = request.GET.get('t', None)
	
	# print doc, timestamp
	
	if (not doc and timestamp) or (not doc and not timestamp):
		raise Http404
	
	pathtofile = getTmpFile(username, "kindle")
	new_file = open(pathtofile, "r")
	
	# step 2: extract koncepts
	contents = extract_kindle(new_file, whichBook=doc, user=request.user)
	new_file.close()
			
	if contents:
		KonceptsFormSet = formset_factory(ImportKonceptForm, extra=0)
		formset = KonceptsFormSet(initial=contents)
		context.update({'formset' : formset, 'doctitle' : doc})
		# May 14, 2014				
		_message = "%d snippet%s found!" % (len(contents), "s"[len(contents)==1:])		
		messages.success(request, _message)		
		
	else:
		_message = "Sorry could not extract any snippets from: <i>%s</i>" % (doc)		
		messages.error(request, _message)


	if request.session['documents_list']:
		context.update({'documents_list' : request.session['documents_list']})
	
	context.update({'kindle_document' : doc, 
					'page_flag' : "kindle",  # x dynamic top menu
				})	#so that in case something goes wrong we can reload this one
				
	return render_to_response(BOOTSTRAP + 'tools/import_review.html', 
								context, 
								context_instance=RequestContext(request))















