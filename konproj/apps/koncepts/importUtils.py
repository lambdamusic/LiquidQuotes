
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
from myutils.myutils import monoSpacedString

from settings import printdebug, BOOTSTRAP, MEDIA_ROOT

from datetime import datetime

from django import forms
from django.forms.formsets import formset_factory









##################
#  
#  data handling for koncept creation phase
#
##################






@login_required
def do_import(request):
	"""
	view that happens only when the final form is passed on! 
	
	note: this works only via a POST request
	"""
	
	KonceptsFormSet = formset_factory(ImportKonceptForm)
	doc = request.GET.get('d', None) # for a kindle import, we also have the title
	
	person = request.user
	username = person.username
	context = {'person' : person, 'mykoncepts' : True, 'doctitle': doc} # initialize context
	 
	if request.method == 'POST':
		formset = KonceptsFormSet(request.POST, request.FILES)

		if formset.is_valid():
			snippets_out, new_doc = create_koncepts(formset, request.user)
			if snippets_out:
				# May 14, 2014				
				_message = "Success! You've added %d new Snippet%s" % (len(snippets_out), "s"[len(snippets_out)==1:])				
				messages.success(request, _message)				
				# return redirect('search_user_koncepts', username=request.user.username)
				return redirect(new_doc.get_absolute_url())
					
				# return HttpResponseRedirect("/%s/import/success" % username)
				# return render_to_response(BOOTSTRAP + 'tools/import_success.html', 
				#							context, 
				#							context_instance=RequestContext(request))


		# if not context.has_key('newkoncepts'):
		context['formset'] = formset
		_message = "There was an error. Have you selected at least one item from the list?"		
		messages.error(request, _message)

		return render_to_response(BOOTSTRAP + 'tools/import_review.html', 
									context, 
									context_instance=RequestContext(request))
	else:
		raise Http404

















def create_koncepts(formset, user):
	"""
	"""

	snippets_out, d1 = [], None

	for form in formset:
		if form.cleaned_data['doimport']:  # if the checkbox is True

			# reuse a document with exact same name, if available
			test = Document.objects.filter(title=form.cleaned_data['source'], created_by=user)
			if test:
				d1 = test[0]
				printdebug("Import > found existing Document ID %d (total docs matching title: %d)" % (d1.id, len(test)))
			else:
				d1 = Document(title=form.cleaned_data['source'], created_by=user)
				printdebug("Import > created new Document (title: <%s>)" % (form.cleaned_data['source']))
			d1.save() # so to force the updated date
			
			# always create new fragment obj
			f1 = Fragment(text=form.cleaned_data['frag'], location=form.cleaned_data['location'], created_by=user)
			f1.source = d1
			f1.save()
			
			snippets_out += [f1]
			
			# if a koncept is provided, create an interpretation too
			
			koncept_title = form.cleaned_data['name']
			
			if koncept_title:				

				# reuse a koncept with exact same name, if available
				try:
					k1 = Koncept.objects.get(name__iexact=koncept_title, created_by=user)
					k1.updated_at = datetime.today()
				except: 
					#the prob is here:
					#maybe use searchdict['name_url'] = url_encode(koncept_name) ???
					# print "here" + " " + str(koncept_title)
					k1 = Koncept(name=koncept_title, created_by=user)
				k1.save()

				# new interpretation
				defaultPrivate = user.userprofile.defaultPrivateKoncepts
				int1 = IntFrag(koncept=k1, fragment=f1, isprivate=defaultPrivate, created_by=user)
				int1.save()


				

	return [snippets_out, d1]









##################
#  
#  utils for file management
#
##################






def importFileExists(username, importtype):
	"""check if a kindle file was previously imported"""
	pathtofile = getTmpFile(username, importtype)
	if os.path.isfile(pathtofile):
		return True
	else:
		return False 




def saveTmpFile(input_file, username, importtype):
	"""
	When import is using a FILE, this saves it in the /upload/tmp/ folder 
	This is used for 2-step uploads as with Kindle files 
	
	PS: with simple-text upload there is no 2 steps process yet, but we still create the file..
	
	importtype: 'kindle' or 'text'
	"""
	# timestamp = int(time.time())
	# filename = "import_%s_%s.txt" % (username, timestamp)
	
	filename = "import_%s_%s.txt" % (username, importtype)
	pathtofile = MEDIA_ROOT + '/tmp/' + filename
	new_file = open(pathtofile, "wr")
	#July 30, 2014: tip based on https://pythonhosted.org/kitchen/unicode-frustrations.html
	# string_for_output = input_file.read().encode('utf8', 'replace')
	# new_file.write(string_for_output)
	new_file.write(input_file.read())
	new_file.close()
	return pathtofile

def getTmpFile(username, importtype, timestamp=None):
	"""
	Gets the import tmp file for a user
	NOTE: timestamp is notused
	"""
	filename = "import_%s_%s.txt" % (username, importtype)
	pathtofile = MEDIA_ROOT + '/tmp/' + filename
	return pathtofile



def alreadyExistingFrag(frag, user):
	"""
	Checks if a fragment with same exact content already exists
	Returns the first related fragment/document found
	June 23, 2014: updated so that it checks for fragments directly, not Koncepts!
	"""
	try:
		# k1 = Koncept.objects.filter(intfrag__fragment__text__istartswith=frag[:100], created_by=user)
		# if k1:
		#	return "WARNING: this snippet already exists! <br />See <a class='konceptcolor' href='%s' target='_blank'>%s</a>" % (k1[0].get_absolute_url(), k1[0].name.upper())
		# else:
		#	return ""
	
		duplicate = Fragment.objects.filter(created_by=user, text__istartswith=frag[:100])
		if duplicate:
			return "Heads Up! Haven't you saved this fragment already? <br />Please check the source: <a class='text-danger' href='%s' target='_blank'>%s</a>" % (duplicate[0].source.get_absolute_url(), duplicate[0].source.title.upper())
		else:
			return ""
				
	except:
		k1 = None
		printdebug("Error: import.py/alreadyExistingFrag raised an exception!")
		return ""



