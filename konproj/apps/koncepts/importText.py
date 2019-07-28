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






@login_required
def importtext(request):
	"""
	
	View that renders the basic template for importing plain text
	
	August 16, 2014: this is currently geared for Sumnotes PDF highlights exports
	
	If POST data are found, the list of koncepts is extracted and passed for review.
	
	# TODO: if the file is too big...
	# with open('some/file/name.txt', 'wb+') as destination:
	#			for chunk in f.chunks():
	#				destination.write(chunk)
	
	"""
	form, file, contents = None, None, None
	MAX_KONCEPTS_PERUPLOAD = 50
		
	person = request.user 
	context = {'person' : person, 'mykoncepts' : True} # initialize context
	username = person.username

	if request.method == 'POST':
		form = ImportFileForm(request.POST, request.FILES)
		if form.is_valid():
			# get the file data and create a formset
			if request.FILES.has_key('file'):
				if request.FILES['file'].multiple_chunks():
					pass	 # @todo: see above
				else:
					file = saveTmpFile(request.FILES['file'], username, "text")
					
			elif form.cleaned_data['text']:
				file = saveTmpFile(StringIO(form.cleaned_data['text']), username, "text")
			
			# extract Koncepts from the text
			if file:
				contents = extractSumnotes(open(file), request.user)
			
			if contents:
				KonceptsFormSet = formset_factory(ImportKonceptForm, extra=0)
				formset = KonceptsFormSet(initial=contents[:MAX_KONCEPTS_PERUPLOAD])

				if len(contents) > MAX_KONCEPTS_PERUPLOAD:
					_message = "%d snippet%s were found, but only the first %d are shown here cause that's the maximum number of snippets you are allowed to upload at a single time - sorry!" % (len(contents), "s"[len(contents)==1:],  MAX_KONCEPTS_PERUPLOAD) 
					messages.warning(request, _message)
				
				else:
					_message = "Success! %d snippet%s were found." % (len(contents), "s"[len(contents)==1:]) 
					messages.success(request, _message)
										
					
				context.update({'formset' : formset, })
				return render_to_response(BOOTSTRAP + 'tools/import_review.html', 
											context, 
											context_instance=RequestContext(request))

			else:
				_message = "Sorry couldn't find any suitable data!" 
				messages.error(request, _message)

		
	if not form:
		form = ImportFileForm()

	context.update({'form': form ,})
		
	return render_to_response(BOOTSTRAP + 'tools/importtext.html',
							context,
							context_instance=RequestContext(request))









def extractSumnotes(filename, user):
	"""

	# 
	# IMPORT FROM SUMNOTES.NET EXPORT OR GOODREADER
	# approach: the rationale for this import is to import a list of snippets separated by empty lines
	NOTE: each snipper is in a single line! 
	# if the line starts with : <Page 1: > we try to extract the page numbers too (eg for sumnotes)
	"""

	BAG = []
	DEFAULT_SOURCE = "Document uploaded on %s " % datetime.now().strftime("%d %b %Y, %H:%M")
		
	lines = filename.read().splitlines()
	
	dyct = {}
	current_page = "undefined" # undefined location
	dyct[current_page] = []
	for line in lines:
		temp = line.strip()
		if temp:
			# sumnotes.net
			if temp.startswith("Page "):				
				current_page = temp.replace(":", "") # remove the final due punti
				if current_page not in dyct:
					dyct[current_page] = []
			# goodreader export	
			elif temp.startswith("--- Page "):
				current_page = temp.replace("--- ", "").replace(" ---", "") # remove the lines
				if current_page not in dyct:
					dyct[current_page] = []
			elif temp.startswith("Highlight (color #"):
				continue		
			else:
				dyct[current_page] += [line]
	
	if dyct:
		for location in sorted(dyct.keys()):
			for snippet in dyct[location]:
				if location == "undefined":
					location = ""
				BAG += [{	'name' : "", 
							'frag' : snippet, 
							'source' : DEFAULT_SOURCE, 
							'location' : location,
							'duplicates_info' : alreadyExistingFrag(snippet, user)}]
							
	return BAG
	
	





#
# def __OLDextractPlainText(filename, user):
#	"""
#
#	#
#	# IMPORT SIMPLE
#	# approach: the rationale for this import is to extract all continuous chunks of text as a new fragment;
#	# the first line (or the first 20 words max) is taken to be the Koncept name
#	#
#
#	FORMAT: koncepts+fragment+empty line
#
#	# KONCEPT NAME 1
#	# Fragment text
#
#	# KONCEPT NAME 2
#	# Fragment text
#
#	# ==========
#	"""
#
#	lineBuffer = []
#	BAG = []
#	DEFAULT_SOURCE = "Bulk import created on %s " % datetime.now()
#
#	lines = filename.read().splitlines()
#	for line in lines:
#		if line.strip() == "":	# remember that STRIP removes the newline characters!
#			out = __process_plaintext_contents(lineBuffer, DEFAULT_SOURCE, user)
#			if out:
#				BAG += out
#			lineBuffer = []
#		else:
#			if line:
#				lineBuffer += [line.strip()]
#
#	# if the last line has text, make sure we extract that too
#	if lineBuffer:
#		out = __process_plaintext_contents(lineBuffer, DEFAULT_SOURCE, user)
#		if out:
#			BAG += out
#
#	# eventually
#	return BAG
#
#
# def __OLDprocess_plaintext_contents(lineBuffer,  DEFAULT_SOURCE, user):
#	"Util that extract data"
#	# print " ** ".join([x for x in lineBuffer])
#	if len(lineBuffer) > 1:
#		# print koncepts
#		kon = monoSpacedString(lineBuffer[0])
#		frag = "\n".join([x.strip() for x in lineBuffer[1:]])
#
#		# note: these keywords map directly to the form fields names!
#		return [{'name' : kon,
#				'frag' : frag,
#				'source' : DEFAULT_SOURCE,
#				'duplicates_info' : __alreadyExistingFrag(frag, user)}]
#	return None














