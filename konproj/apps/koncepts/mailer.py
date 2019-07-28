#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	send email to lists
#

(InteractiveConsole)

>>> from koncepts.mailer import *
>>> email2015_04_02()  <== TEST
Emailing michele.pasin@gmail.com
Emailing michele.pasin@nature.com
>>> email2015_04_02(False)  <==  REAL THING!      
Emailing mik@mac.com
... etc.....

##################


"""

from settings import printdebug, BOOTSTRAP

import sys
			
from django.contrib.auth.models import User
from django.core import mail
#
#
# April 2, 2015:
# a) create a function with data for a specific email
# b) load it and send it via the shell
#



# @todo: add user name to personalize the message more!



def genericEmailAnnouncement(subject = "", body="", sender="", distribution_list=None, ):
	"""	
	provides a bunch of default values for testing purposes
	==> sends a test email to myself
	
	"""

	if not subject:
		subject = "See what's new with LiquidQuotes.com"
	
	if not body:
		body = 'Here is another message'
		
	if not sender:
		sender = "Liquid Quotes <admin@liquidquotes.com>"
		
	if not distribution_list:
		distribution_list = ['michele.pasin@gmail.com']


	connection = mail.get_connection()
	connection.open()
	
	for emailAddress in distribution_list:

		print >> sys.stderr, "Emailing %s" % emailAddress

		try:	
			email1 = mail.EmailMessage(subject, body, sender, 		                          [emailAddress], connection=connection)
			email1.send()
		except:
			print "Error with %s" % emailAddress
  

		
		




def email2015_04_02(test=True):
	"""
	2015-04-02: email to announce new version of LiquidQuotes
	"""
	subject = "See what's new with LiquidQuotes.com"
	sender = "Research Quotes <admin@liquidquotes.com>"

	if test:
		distribution_list= ['michele.pasin@gmail.com', 'michele.pasin@nature.com']
	else:
		distribution_list = [x.email for x in User.objects.all()]	

	message = """Hi there! 
	
Ready for the holidays? 

Thanks again for signing up with LiquidQuotes.com - we would like to take the opportunity to announce that in the last weeks a number of new features have been completed, and some existing ones improved. 
	
> Downloads: 
------------------
Now you can easily export your quotes into Word or Excel, e.g. in case you want to keep working with another software application while writing a paper ..see more at http://blog.LiquidQuotes.com/2015/03/18/download-your-quotes/
	
> Dashboard:
------------------
Log in and you'll be taken straight to a personalized dashboard summing up your recent activity on the site ..see more at http://blog.LiquidQuotes.com/2015/03/18/new-dashboard-page/
	
> Kindle Highlights:
--------------------------
Importing Kindle highlights is now even simpler! The interface is slimmer and the import mechanism much more solid ..see more at http://blog.LiquidQuotes.com/2015/03/31/how-to-import-kindle-highlights/
	
	
Want more? Keep an eye on http://blog.LiquidQuotes.com/ to see what else has been happening!  

Hope to see yoy back soon,  
	
--Michele @ www.LiquidQuotes.com
	
	"""

	# FINALLY: send email
	genericEmailAnnouncement(subject, message, sender, distribution_list)



















#
# def contactSendEmail(request):
# 	"""
# 	Receives the email data via ajax and sends an email
# 	/libs/agency/contact_me.js is the front end code talking to this function
#
# 	Returns a 404 or 200
# 	"""
#
# 	name = request.GET.get('name', '')
# 	email = request.GET.get('email', '')
# 	message = request.GET.get('message', '')
# 	topic = request.GET.get('topic', '')
#
# 	if name and email and message:
# 		# then all data have been entered
#
# 		try:
# 			subject = "[www.LiquidQuotes.com] New mail from %s " % email
# 			final_message = """[This is a message sent using the contact form on www.LiquidQuotes.com]
#
# Sender: %s
# Email: %s
# Topic: %s
# ---------------------------------
# Message: %s
#
# 				"""	 % (name, email, topic, message)
#
# 			send_mail(subject, final_message, email,
# 				['michele.pasin@gmail.com'], fail_silently=False)
# 			success = True
# 		except Exception, e:
# 			printdebug("contactSendEmail > ", str(e))
# 			success = False
# 			pass
#
# 	else:
# 		# missing data in the form
# 		success = False
#
#
# 	print success
#
# 	if success:
# 		return HttpResponse("Success")
# 	else:
# 		raise Http404
#
#
#
#
	
	
	
	
	





									
							
							
							
