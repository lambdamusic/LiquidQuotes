#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for exporting data
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
# from django.utils.html import strip_tags, escape
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse

import datetime

from koncepts.models import *
from koncepts.export import *
from settings import printdebug, MEDIA_ROOT



# ======
# ===========
# TXT - simple text file
# ===========
# ======



@login_required
def export_txt(request):
	"""
	Export data in TXT format
	"""
	
	# try to extract a valid instance 
	valid_obj = get_object(request)
	
	txt_output = ""
	
	if valid_obj:
		response = HttpResponse(mimetype='text/plain')
		response['Content-Disposition'] = 'attachment; filename=' + valid_obj['filename'] + '.txt'
		response.write(u'\ufeff'.encode('utf8'))


		# ---
		# single quote 
		# ---
		
		if 'quote' in valid_obj.keys():
			
			# get fields
			
			quote = valid_obj['quote']
			
			txt_output += writeSingleQuote(request, quote)
		
		
		elif 'document' in valid_obj.keys():	
			
			document = valid_obj['document']
			
			txt_output += writeDocumentHeader(request, document)
			
			for quote in document.fragment_set.all():
				txt_output += writeSingleQuote(request, quote, False)
			

		elif 'koncept' in valid_obj.keys():	
			
			koncept = valid_obj['koncept']
			
			txt_output += writeCollectionHeader(request, koncept)
			
			for intf in koncept.intfrag_set.all():
				txt_output += writeSingleQuote(request, intf.fragment)
		
		else:
			raise Http404
				
		response.write(txt_output)
		return response
	
	
	else:
		raise Http404




def addNewLine(out, obj):
	"util to speed up the creation of txt file"
	return out + smart_str(obj) + "\n"


def writeSingleQuote(request, quote, includeSource=True):
	""" 
	returns a string with data from a single quote in this format: 
	
	---------------------------------
	TITLE:
	We need teachers who have...
	QUOTE:
	My nice quote
	SOURCE:
	Theories Of Childhood, Second Edition: An Introduction To Dewey, Montessori, Erikson, Piaget & Vygotsky (redleaf Professional Library) (mooney, Carol Garhart), , 
	---------------------------------
	http://127.0.0.1:8000/mpasin/quotes/2351
	Created on: 12, Jan 2015
	Downloaded on: 18, Mar 2015
	---------------------------------	
	
	"""
	output = ""	

	# compose document	
	output = addNewLine(output, "---------------------------------")
	output = addNewLine(output, "TITLE:")
	output = addNewLine(output, quote.title)
	output = addNewLine(output, "QUOTE:")
	output = addNewLine(output, quote.text)
	
	if includeSource:
		output = addNewLine(output, "SOURCE:")
		if quote.source:
			sourcetitle = quote.source.title
			sourceauthor = quote.source.author
			sourcepubyear = quote.source.pubyear or ""
			sourcedesc = quote.source.description
			sourceurl = quote.source.url	

			bigtitle = ", ".join([sourcetitle, sourceauthor, str(sourcepubyear)])
			output = addNewLine(output, bigtitle)

			if sourcedesc:
				output = addNewLine(output, sourcedesc)

			if sourceurl:
				output = addNewLine(output, sourceurl)
		else:
			output = addNewLine(output, "not available")
	
	output = addNewLine(output, "---------------------------------")

	# metadata
	uri = request.build_absolute_uri(quote.get_absolute_url())
	created = "Created on: {:%d, %b %Y}".format(quote.created_at)
	downloaded = "Downloaded on: {:%d, %b %Y}".format(datetime.date.today())
	
	output = addNewLine(output, uri)
	output = addNewLine(output, smart_str(created))
	output = addNewLine(output, smart_str(downloaded))
	output = addNewLine(output, "---------------------------------")	
	output = addNewLine(output, "")
	output = addNewLine(output, "")
	output = addNewLine(output, "")
	
	return output
	




def writeDocumentHeader(request, source):
	""" 
	Writes the header for a document-dowload page
	
	Includes two bigger sections delimiters for source metadata and 
	quotes lists
	
	"""
	output = ""
	
	output = addNewLine(output, "#######")
	output = addNewLine(output, "SOURCE:")
	output = addNewLine(output, "#######")
	output = addNewLine(output, "")
	
	output = addNewLine(output, "---------------------------------")	
	sourcetitle = source.title
	sourceauthor = source.author
	sourcepubyear = source.pubyear or ""
	sourcedesc = source.description
	sourceurl = source.url	

	bigtitle = ", ".join([sourcetitle, sourceauthor, str(sourcepubyear)])
	output = addNewLine(output, bigtitle)

	if sourcedesc:
		output = addNewLine(output, sourcedesc)

	if sourceurl:
		output = addNewLine(output, sourceurl)

	output = addNewLine(output, "---------------------------------")	
	
	# metadata
	uri = request.build_absolute_uri(source.get_absolute_url())
	created = "Created on: {:%d, %b %Y}".format(source.created_at)
	downloaded = "Downloaded on: {:%d, %b %Y}".format(datetime.date.today())
	
	output = addNewLine(output, uri)
	output = addNewLine(output, smart_str(created))
	output = addNewLine(output, smart_str(downloaded))
	output = addNewLine(output, "---------------------------------")	
	output = addNewLine(output, "")
	output = addNewLine(output, "")
	output = addNewLine(output, "")
	output = addNewLine(output, "")
	output = addNewLine(output, "#######")
	output = addNewLine(output, "QUOTES:")
	output = addNewLine(output, "#######")
	output = addNewLine(output, "")
	output = addNewLine(output, "")
		
	return output




def writeCollectionHeader(request, koncept):
	""" 
	Writes the header for a collection-dowload page
	
	Includes two bigger sections delimiters for Collection metadata and 
	Quotes lists
	
	"""
	output = ""
	
	output = addNewLine(output, "#######")
	output = addNewLine(output, "COLLECTION:")
	output = addNewLine(output, "#######")
	output = addNewLine(output, "")
	
	output = addNewLine(output, "---------------------------------")
	output = addNewLine(output, koncept.name)
	if koncept.description:
		output = addNewLine(output, koncept.description)
	output = addNewLine(output, "---------------------------------")	
	
	# metadata
	uri = request.build_absolute_uri(koncept.get_absolute_url())
	created = "Created on: {:%d, %b %Y}".format(koncept.created_at)
	downloaded = "Downloaded on: {:%d, %b %Y}".format(datetime.date.today())
	
	output = addNewLine(output, uri)
	output = addNewLine(output, smart_str(created))
	output = addNewLine(output, smart_str(downloaded))
	output = addNewLine(output, "---------------------------------")	
	output = addNewLine(output, "")
	output = addNewLine(output, "")
	output = addNewLine(output, "")
	output = addNewLine(output, "")
	output = addNewLine(output, "#######")
	output = addNewLine(output, "QUOTES:")
	output = addNewLine(output, "#######")
	output = addNewLine(output, "")
	output = addNewLine(output, "")
		
	return output
	
					
							
