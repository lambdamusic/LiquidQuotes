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

from django.core.mail import send_mail

from settings import printdebug, BOOTSTRAP


def contactSendEmail(request):
	"""
	Receives the email data via ajax and sends an email
	/libs/agency/contact_me.js is the front end code talking to this function
	
	Returns a 404 or 200 
	"""

	name = request.GET.get('name', '')
	email = request.GET.get('email', '')
	message = request.GET.get('message', '')
	topic = request.GET.get('topic', '')
			
	if name and email and message:
		# then all data have been entered
	
		try:
			subject = "[www.liquidquotes.com] New mail from %s " % email
			final_message = """[This is a message sent using the contact form on www.liquidquotes.com]
		
Sender: %s
Email: %s
Topic: %s
---------------------------------
Message: %s
		
				"""	 % (name, email, topic, message)
		
			send_mail(subject, final_message, "masked@email.com",
				['michele.pasin@gmail.com'], fail_silently=False)
			success = True
		except Exception, e:
			printdebug("contactSendEmail > ", str(e))
			success = False
			pass
		
	else:
		# missing data in the form
		success = False 
	
	
	print success
	
	if success:
		return HttpResponse("Success")					
	else:
		raise Http404

	
	
	
	
	
	
	
	



	
	


# tolta quando ho aggiunto il nuovo template August 3, 2014

def OLD_contactPage(request):
	"""
	The contact page displaying a form :: note than the form is created in the template
	This function just validates it.
	"""

	name = request.GET.get('name', '')
	email = request.GET.get('email', '')
	message = request.GET.get('message', '')
			
	if (name or email or message):
		if name and email and message:
			# then all data have been entered
		
			try:
				subject = "[www.liquidquotes.com] New mail from %s " % email
				final_message = """[This is a message sent using the contact form on www.liquidquotes.com]
			
Sender: %s
Email: %s
---------------------------------
Message: %s
			
					"""	 % (name, email, message)
			
				send_mail(subject, final_message, email,
					['michele.pasin@gmail.com'], fail_silently=False)
				success = 'sent'
			except:
				success = 'error'
				pass
			
		else:
			# missing data in the form
			success = 'error'	
	else:
		success = None	
	
	fields = [name, email, message]
	
	context = {	  
			'success' : success,  'fields' : fields,			
				}	
	
	return context















									
							
							
							
