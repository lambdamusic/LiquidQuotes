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

from settings import printdebug, MEDIA_ROOT

#
# NOTE: this file contains only utils COMMON to all export libraries 
#





def get_object(request):
	"""	 
	The /export GET request has a predefined number of parameters. 
	<quote_id, doc_idkon_id >  [change as needed]
	
	This function pulls the correct DB instance based on that and the user. 
	"""

	person = request.user
	output = {}

	try:
		quote_id = int(request.GET.get('quote_id', None))
		output['quote'] = Fragment.objects.get(pk=quote_id)
		# output['quote'] = Fragment.objects.get(created_by=person, pk=quote_id)
		output['filename'] = "LiquidQuotes_Quote-%s" % str(quote_id)
	except:
		pass
		
	try:
		doc_id = int(request.GET.get('doc_id', None))
		# output['document'] = Document.objects.get(created_by=person, pk=doc_id)
		output['document'] = Document.objects.get(pk=doc_id)
		output['filename'] = "LiquidQuotes_Source-%s" % str(doc_id)
	except:
		pass
		
	try:
		kon_id = int(request.GET.get('kon_id', None))
		output['koncept'] = Koncept.objects.get(created_by=person, pk=kon_id)
		output['filename'] = "LiquidQuotes_Collection-%s" % str(kon_id)
	except:
		pass
		
	return output









# ======
# ===========
# PDF
# ===========
# ======





# ====== PDF ==========
# February 17, 2015: can't install reportlab on homemac so not installed
# February 19, 2015: installed, but generating PDF seems too laborious!
# 
#
# 
# from reportlab.pdfgen import canvas
# from django.http import HttpResponse
#
# @login_required
# def export_pdf(request):
#	  # Create the HttpResponse object with the appropriate PDF headers.
#	  response = HttpResponse(mimetype='application/pdf')
#	  response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'
#
#	  # Create the PDF object, using the response object as its "file."
#	  p = canvas.Canvas(response)
#
#	  # Draw things on the PDF. Here's where the PDF generation happens.
#	  # See the ReportLab documentation for the full list of functionality.
#	  p.drawString(100, 100, "Hello world.")
#
#	  # Close the PDF object cleanly, and we're done.
#	  p.showPage()
#	  p.save()
#	  return response
#




							
							
