#!/usr/bin/env python
# encoding: utf-8

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.utils.encoding import force_unicode

from django.conf import settings
from django.db import connection, models
from time import strftime
import time

from django.contrib.auth.models import User

# from concepts.models import *
from koncepts.models import *

from settings import printdebug


##################

# 2012-12-16

# transferring he old app into the new one

##################



# EG:
# bash-3.2$ python manage.py transfer 1

class Command(BaseCommand):
	args = '<person, source, factoid etc. >'
	help = 'run the fixes that make the STG db ready for LIVE'


	def handle(self, *args, **options): 
		"""
		args - args 
		options - configurable command line options
		"""


		# feedback:
		print "\n\n++ = ++ = ++ = ++ = ++ = ++ = ++ = ++\n%s\nSTARTING :"  % strftime("%Y-%m-%d %H:%M:%S")	
		print "MAYBE BEFORE RUNNING THIS YOU MIGHT WANT TO DISABLE SOME EXTRA-SAVING ACTIONS......"
		print "++ = ++ = ++ = ++ = ++ = ++ = ++ = ++\n"



		if args:
			for a in args:
				printdebug("Argument provided: ==%s==" % str(a))


		#  now do the actions: 
		# 1) # ....
		
		if '1' in args:
			
			mpasin = User.objects.get(username="mpasin")
			
			
			# ITERATE ONE INTERPRETATION AT A TIME
			
			# for i in Interpretation.objects.all()[:100]:	
			for i in Interpretation.objects.all():	
				
				
				# TERMS => KONCEPTS
				
				koncept, created = Koncept.objects.get_or_create(name=i.term1.name, created_by=mpasin, updated_by=mpasin,)
				koncept.save() # in order to apply the on-save method!
				print "*KONCEPT* : ", koncept, "-- created=", created
				print "===url==>  ", koncept.name_url
		
				# SOURCES => DOCUMENTS
		
				if i.sourcefk:
					document, created = Document.objects.get_or_create(title=i.sourcefk.title, author=i.sourcefk.author, description=i.sourcefk.description, pubyear=i.sourcefk.pubyear, url=i.sourcefk.url, created_by=mpasin, updated_by=mpasin,)
					document.save()
					print "DOCUMENT :", document, "--", created
					print "===url==>  ", document.name_url
				else:
					document = None
					print "===Document not available==="
			
				# CONTEXTS => TAGS

				tags_list = []
				if i.context.all():
					for c in i.context.all():
						tag, created = Tag.objects.get_or_create(name=c.name, description=c.description, created_by=mpasin, updated_by=mpasin,)
						tag.save()
						print "#TAG: ", tag, "--", created
						print "===url==>  ", tag.name_url
						tags_list += [tag]
		
		
				# INTERPRETATIONS ==> FRAGMENT + INTFRAG
		
				# SENSE => FRAGMENT
				if i.term1.language:
					language, created = Languages.objects.get_or_create(name=i.term1.language.name, created_by=mpasin, updated_by=mpasin,)
				else:
					language = None
				
				fragment, created = Fragment.objects.get_or_create(text=i.sense, source=document, ismine=i.ismine, isdictionary=i.isdictionary, language=language, created_by=mpasin, updated_by=mpasin,)
				print "FRAGMENT : ", fragment, "-- created=", created
		
				# INT => INTFRAG		
		
				intfrag, created = IntFrag.objects.get_or_create(koncept=koncept, fragment=fragment, created_by=mpasin, updated_by=mpasin,)
				for t in tags_list:
					intfrag.tags.add(t)
				print "==INTFRAG== : ", intfrag, "-- created=", created
		
		



		# 2015-02-13: evolve tags model
		# python manage.py transfer 2
		if '2' in args:

			for x in IntFrag.objects.all():
				if x.tags.all() and x.fragment:
					x.fragment.tags.clear()
					for t in x.tags.all():
						print "==FRAG== : ", x.fragment.id, "-- tag=", t
						x.fragment.tags.add(t)
						
				
		# 2015-08-11: bootstrap subject model
		# python manage.py transfer 3
		if '3' in args:
			if False:
				Subject.objects.all().delete()
				
			for x in Koncept.objects.all():
				print "reading koncept %d" % x.id
				try:
					s = Subject.objects.filter(name=x.name, created_by=x.created_by)[0]
					print "....found existing", x.name
				except:					
					s = Subject()
					s.name = x.name
					s.name_url = x.name_url
					s.description = x.description
					s.created_by = x.created_by
					s.updated_by = x.updated_by
					s.created_at = x.updated_at
					s.updated_at = x.updated_at
					s.save()
				for frag in x.get_fragments():
					frag.subjects.add(s)
			
			for x in Tag.objects.all():
				print "reading tag %d" % x.id
				try:
					s = Subject.objects.filter(name=x.name, created_by=x.created_by)[0]
					print "....found existing", x.name
				except:
					s = Subject()
					s.name = x.name
					s.name_url = x.name_url
					s.description = x.description
					s.created_by = x.created_by
					s.updated_by = x.updated_by
					s.created_at = x.updated_at
					s.updated_at = x.updated_at				
					s.save()
				for frag in x.fragment_set.all():
					frag.subjects.add(s)
				
				
								
				
								
			
		printdebug("************\nCOMPLETED\n************")



