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
import csv

from koncepts.models import *
from koncepts.export import *
from settings import printdebug, MEDIA_ROOT




# ======
# ===========
# CSV
# ===========
# ======



@login_required
def export_csv(request):
	"""
	Export data in CSV format
	"""
	
	# try to extract a valid instance 
	valid_obj = get_object(request)
	
	if valid_obj:
		
		response = HttpResponse(mimetype='text/csv')
		response['Content-Disposition'] = 'attachment; filename=' + valid_obj['filename'] + '.csv'
		writer = csv.writer(response, csv.excel)
		response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)


		# ---
		# header
		# ---
		
		writer.writerow([
			smart_str(u"Url"),
			smart_str(u"Title"),
			smart_str(u"Text"),
			smart_str(u"Location"),
			smart_str(u"Tags"),
			smart_str(u"Source"),
			smart_str(u"Source Author"),
			smart_str(u"Source PubYear"),
			smart_str(u"Source Url"),
			smart_str(u"Source Full Reference"),
			smart_str(u"LiquidQuotes Source Url"),
		])
		
		
		# ---
		# contents
		# ---
		
		if 'quote' in valid_obj.keys():
			
			quote = valid_obj['quote']
		
			writer = writeSingleQuote(writer, request, quote)	
		
		elif 'document' in valid_obj.keys():	
			
			document = valid_obj['document']
						
			for quote in document.fragment_set.all():
				writer = writeSingleQuote(writer, request, quote)
			

		elif 'koncept' in valid_obj.keys():	
			
			koncept = valid_obj['koncept']
			
			for intf in koncept.intfrag_set.all():
				writer = writeSingleQuote(writer, request, intf.fragment)		
				
		else:
			raise Http404
			
				
		
		
		return response
		
	
	else:  # if we dont have a valid object
		raise Http404
				




def writeSingleQuote(writer, request, quote):
	""" 
	Writes one line for a single quote
	"""
		
	uri = request.build_absolute_uri(quote.get_absolute_url())

	if quote.tags.all():
		tags = "; ".join([x.name for x in quote.subjects.all()])
	else:
		tags = ""
	if quote.source:
		sourcetitle = quote.source.title
		sourceauthor = quote.source.author
		sourcepubyear = str(quote.source.pubyear)
		sourceurl = quote.source.url
		sourcedesc = quote.source.description
		sourceURI = request.build_absolute_uri(quote.source.get_absolute_url())
	else:
		sourcetitle, sourceauthor, sourcepubyear, sourceurl, sourcedesc, sourceURI = "", "", "", "", "", ""
					
	writer.writerow([
		smart_str(uri),
		smart_str(quote.title),
		smart_str(quote.text),
		smart_str(quote.location),
		smart_str(tags),
		smart_str(sourcetitle),
		smart_str(sourceauthor),
		smart_str(sourcepubyear),
		smart_str(sourceurl),
		smart_str(sourcedesc),
		smart_str(sourceURI),
	])
	
	return writer
							
							
