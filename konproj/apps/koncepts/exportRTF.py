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

from PyRTF import *



# ======
# ===========
# RTF   :: 2015-03-18 : DISABLED IN FAVOR OF PLAIN TEXT 
# ===========
# ======



@login_required
def export_rtf(request):
	"""
	Export data in CSV format
	"""
	
	# try to extract a valid instance 
	valid_obj = get_object(request)
	
	if valid_obj:
		response = HttpResponse(mimetype='text/rtf')
		response['Content-Disposition'] = 'attachment; filename=' + valid_obj['filename'] + '.rtf'

		doc		= Document()
		ss		= doc.StyleSheet
		section = Section()
		doc.Sections.append( section )


		# ---
		# single quote 
		# ---
		
		if 'quote' in valid_obj.keys():
			
			# get fields
			
			quote = valid_obj['quote']
			uri = request.build_absolute_uri(quote.get_absolute_url())
			created = "Created on: {:%d, %b %Y}".format(quote.created_at)
			downloaded = "Downloaded on: {:%d, %b %Y}".format(datetime.date.today())
			
			if quote.source:
				sourcetitle = quote.source.title
				sourceauthor = quote.source.author
				sourcepubyear = quote.source.pubyear or ""
				sourcedesc = quote.source.description
				sourceurl = quote.source.url
				
			# compose document	

			p = Paragraph( ss.ParagraphStyles.Heading1 )
			p.append( uri )
			section.append( p )
			
			p = Paragraph( ss.ParagraphStyles.Heading2 )
			p.append( smart_str(quote.title) )
			section.append( p )
					
			p = Paragraph( ss.ParagraphStyles.Normal )
			p.append( smart_str(quote.text))
			section.append( p )
		
			if quote.source:  
				
				para_props = ParagraphPS()
				para_props.SetLeftIndent( TabPropertySet.DEFAULT_WIDTH *  2 )
				p = Paragraph( ss.ParagraphStyles.Normal, para_props )
				bigtitle = ", ".join([sourcetitle, sourceauthor, str(sourcepubyear)])
				p.append( smart_str(bigtitle) )
				section.append( p )
				
				if sourcedesc:
					p = Paragraph( ss.ParagraphStyles.Normal, para_props )
					p.append( smart_str(sourcedesc))
					section.append( p )

				if sourceurl:
					p = Paragraph( ss.ParagraphStyles.Normal, para_props )
					p.append( smart_str(sourceurl) )
					section.append( p )

			
			section.append( '' ) # blank paragraph

			tps = TextPS( colour=ss.Colours.Grey )  # grey text
			p = Paragraph( ss.ParagraphStyles.Normal )
			text = Text( smart_str(created), tps )
			p.append(text )
			section.append( p )			
			p = Paragraph( ss.ParagraphStyles.Normal )
			text = Text( smart_str(downloaded), tps )
			p.append(text )
			section.append( p )			
			
		
		DR = Renderer()
		DR.Write( doc, response )
		return response
	
	
	else:
		raise Http404







							
							
