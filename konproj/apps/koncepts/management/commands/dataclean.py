
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

from koncepts.models import *

from settings import printdebug


##################

# 2012-12-16

# various utils

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
			
			# mpasin = User.objects.get(username="mpasin")
			
			print "\n......Showing Documents with same title\n"

			for x in Document.objects.all():
				if Document.objects.exclude(id=x.id).filter(title=x.title, ):
					print x.id, x.title


			# NOTE: this must be run manually by setting the caller below
			# essentially cause I don't know how to pass more than one args to the python func

			def mergedocs(idkeep):
				"""
				gets doc ID; retrieves similar docs and merges into it 
				"""
				dkeep = Document.objects.get(pk=idkeep)
				others = Document.objects.exclude(id=idkeep).filter(title=dkeep.title)
				for el in others:
					for frag in el.fragment_set.all():
						frag.source = dkeep
						print "...transferring", frag.id, frag
						frag.save()
					print "deleting", el.id, el
					el.delete()

			# mergedocs(130)



		if '2' in args:
			
			# mpasin = User.objects.get(username="mpasin")
			
			print "\n......Showing Documents with no interpretations attached\n"

			for x in Document.objects.filter(fragment__intfrag=None):
				print x.id, x.title		

		if '21' in args:
			
			# mpasin = User.objects.get(username="mpasin")
			
			print "\n......Deleting Documents with no interpretations attached\n"

			for x in Document.objects.filter(fragment__intfrag=None):
				print x.id, x.title 
				try:
					x.fragment.delete()
					x.delete()
				except:
					x.delete()	


					
		# March 21, 2014: fill in the orderno field for IntFrags 
		# python manage.py dataclean 3
		if '3' in args:

			for x in Koncept.objects.all():
				x.cleanIntFragOrdering()	
				
				
		# 2014-10-17: cascade privacy from intfrags to snippets
		# python manage.py dataclean 4
		if '4' in args:

			for x in Fragment.objects.all():
				intfrags = x.intfrag_set.all()
				if len(intfrags) < 1:
					print "Fragment %d is an orphan => setting it as private" % x.id
					privacy = True
				if len(intfrags) > 1:
					print "Fragment %d has more than one intepretation => taking the first one" % x.id
					privacy = intfrags[0].isprivate
				if len(intfrags) == 1:
					privacy = intfrags[0].isprivate
				
				x.isprivate = privacy	
				x.save()					
	
	
		# 2014-12-30: bootstrap titles and clean koncepts with <2 quotes
		# python manage.py dataclean 5
		if '5' in args:

			for x in Fragment.objects.all():
				k1 = x.get_koncept()
				if k1: 
					x.title = k1.name
					print "Fragment %d is being saved => title=%s" % (x.id, x.title)
					x.save()			
					
					if True:			
						# delete koncept/intfrag if it has <2 quotes
						if k1.intfrag_set.count() < 2:
							for intfrag in k1.intfrag_set.all():
								fragment, tags = intfrag.fragment, list(intfrag.tags.all())	 
								print "Koncept %d is being deleted => title=%s" % (k1.id, k1.name)
								intfrag.delete()
								k1.delete()
								# remove orphan tags too
								for t in tags:
									if not t.intfrag_set.all():
										printdebug("Cleaning tag %s" % t)
										t.delete()

		# 2015-02-13: bootstrap order field in sources
		# python manage.py dataclean 6
		if '6' in args:

			for d in Document.objects.all():
				counter = 0
				for f in d.fragment_set.all().order_by('created_at'):
					counter += 1
					f.orderno = counter 
					f.save()
					print "==FRAG== : ", f.id, "-- order=", counter


		# 2015-02-14: check if any tags are reused across users and recreates them
		# python manage.py dataclean 7
		if '7' in args:
			
			for i in IntFrag.objects.all():
				if i.tags.all():
					for x in i.tags.all():
						if x.created_by != i.created_by:
							print x, "=== Owned by ===", x.created_by, "==== but infrag is ===", i.created_by		
							new = Tag.objects.get_or_create(name=x.name, created_by=i.created_by)[0]
							i.tags.remove(x)
							i.tags.add(new)

							
		# 2015-02-14: remove tags from old location on intfrags
		# python manage.py dataclean 8
		if '8' in args:
		
			for i in IntFrag.objects.all():
				if i.tags.all():
					print "=== Clearing intfrag ===", i.id 
					i.tags.clear()					


		# 2015-02-14: delete tags with no fragments
		# python manage.py dataclean 9
		if '9' in args:
		
			for x in Tag.objects.all():
				if not x.fragment_set.all(): 
					print "=== Deleting tag ===", x
					x.delete()


		# 2015-05-04: remove collections with only 1 fragments
		# python manage.py dataclean 9
		if '10' in args:
		
			for x in Fragment.objects.filter(created_by__id=1):
				k1 = x.get_koncept()
				if k1: 
					# delete koncept/intfrag if it has <2 quotes
					if k1.intfrag_set.count() < 2:
						for intfrag in k1.intfrag_set.all():
							fragment = intfrag.fragment 
							print "Koncept %d is being deleted => title=%s" % (k1.id, k1.name)
							
							if x.title:
								if x.title[:(len(x.title)-3)] in x.text:
									x.title = k1.name
									print "Fragment %d is being saved => title=%s" % (x.id, x.title)
							x.save()
										
							
							intfrag.delete()
							k1.delete()

		# 2015-11-17: remove all tags (now in 'subject')
		# python manage.py dataclean 11
		if '11' in args:
			for f in Fragment.objects.all():
				if f.tags.all():
					print "=== Cleaning tags from fragment ===", f 
					f.tags.clear()
			for x in Tag.objects.all():
				print "=== Deleting tag ===", x
				x.delete()
					
						
																						
		printdebug("\n************\nCOMPLETED\n************")



