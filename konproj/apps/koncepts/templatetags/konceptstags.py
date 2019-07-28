from django import template

from django.conf import settings

from koncepts.models import *

register = template.Library()



# TESTING DIFFERENT SIZES BASED ON STARS 2016-05-24

import random
@register.filter
def test_size(l):
	"""
	"""
	return random.choice(['lead', "llead"])




# 2015-04-28: testing tiles




@register.filter
def get_tile_width(doc):
	"""
	"""
	frags = doc.fragment_set.count()
	
	if frags > 6:
		return 6
	else:
		return frags

@register.filter
def get_tile_style(doc):
	"""
	class="col-md-{{d1|get_tile_width}} X" style="height: auto;"
	
	3 styles: 
	> large docs More than 5 fragments
	> medium
	> small - only 1
	.B {background:blue; height:200px}
	.G {background:green; height:100px}
	.O {background:orange; height:100px}
	
	
	"""
	frags = doc.fragment_set.count()
	
	if frags <= 1:
		return """class="col-md-4 tilebox" style="height: 200px; background: lightgrey;" """
	elif frags <= 5:
		return """class="col-md-8 tilebox" style="height: 200px; background: green;" """
	else:
		return """class="col-md-8 tilebox" style="height: 400px; background: #C17A0C;" """

@register.filter
def get_h5_style(doc):
	"""
	"""
	frags = doc.fragment_set.count()
	
	if frags <= 1:
		return """ """
	elif frags <= 5:
		return """style="font-size: 22px;" """
	else:
		return """style="font-size: 34px;" """


@register.filter
def get_a_style(doc):
	"""
	"""
	frags = doc.fragment_set.count()
	
	if frags <= 1:
		return """ style="color: black;" """
	elif frags <= 5:
		return """ style="color: lightcyan;" """  # lightcyan
	else:
		return """ style="color: aliceblue;" """
		
		
# END OF TESTING
		






@register.filter
def paginator_showOne(n):
	"""Determines if the '1' page should be shown
	"""
	pageRange = 3 # this is set in myutils/paginator_helper
	if n - pageRange > 1:
		return True
	else:
		return False



@register.filter
def paginator_showLast(n, tot):
	"""Determines if the last page should be shown
	"""
	# print n, tot
	pageRange = 3 # this is set in myutils/paginator_helper
	if n + pageRange < tot:
		return True
	else:
		return False


		

@register.filter
def userpage_and_authenticated(request):
	"""
	Determines if we are on the userpage of an authenticated user
	Updated November 25, 2013: there's no 'user' bit in url anymore
	"""
	temp = request.path.split("/")
	if request.user.is_authenticated() and temp[1] == request.user.username:
		return True
	else:
		return False
		




@register.filter
def navbar_getclass(request, navitem):
	"""
	December 2, 2013:
	Determines the *active* or other class for the LI items in the top navbar, based on path
	"""
	ACTIVE_CLASSNAME = "active"
	temp = request.path.split("/")
	# print temp
	if navitem == "home" and len(temp) == 4 and not temp[3] and temp[1] not in settings.REGISTRATION_RESERVED:
		# have home highlighted for any user-specific view within the dashboard
		return ACTIVE_CLASSNAME
	if navitem in temp:
		return ACTIVE_CLASSNAME
	return ""




@register.filter
def dtabs_getclass(request, tabsname):
	"""Determines the *active* or other class for the LI items in dashboard tabs, based on path
	"""
	ACTIVE_CLASSNAME = "active"
	temp = request.path.split("/")
	if tabsname in temp:
		return ACTIVE_CLASSNAME
	return ""		
			

@register.filter
def findin_urlpath(request, name):
	"""
	"""
	temp = request.path
	if name in temp:
		return True
	return False	






@register.filter
def get_search_path(requestPath):
	"""Determines what path to use for the search (user or public)
		Typical path can be </users/mpasin/koncepts/silicon-roundabout>
		April 2, 2014: Decommision? 
	"""
	USERS_STRING = "/users/"
	if USERS_STRING in requestPath:
		r = requestPath.split("/")
		return "/users/%s/koncepts/" % r[2]
	else:
		# search at the top level
		return "/koncepts/"



@register.filter
def get_search_title(request, totcount):
	"""Determines what string to use in the search title phrase
		April 2, 2014: Decommision? 
	"""
	USERS_STRING = "/users/"
	if totcount == 0:
		extra = "Ops.. "
	else:
		extra = ""
	if USERS_STRING in request.path:
		r = request.path.split("/")
		path_username = r[2]
		if request.user.is_authenticated() and path_username == request.user.username: 
			return "%sYou have %d koncepts" % (extra, totcount)
		else:
			return "%s%s has %d koncepts" % (extra, path_username, totcount)
	else:
		return "%sThere are %d public koncepts" % (extra, totcount)



@register.filter
# truncate after a certain number of characters
def truncchar(value, arg):
	if len(value) < arg:
		return value
	else:
		return value[:arg] + '...'




@register.filter(name='homepage_sizing')
def homepage_sizing(n):
	"""
	For the koncepts cloud on the homepage
	"""
	try:
		if n <= 1:
			return 10
		else:
			return 10 + ((10 * (n - 1)) / 2) 
	except:
		return 10



@register.filter(name='tagcloud_sizing')
def tagcloud_sizing(n, base=7):
	"""
	For the tag cloud on several pages
	"""
	BASE = base
	MAX = 30
	try:
		if n <= BASE:
			return BASE
		else:
			t = BASE + ((BASE * (n - 1)) / 7)
			if t > MAX:
				return MAX
			else:
				return t 
	except:
		return BASE


@register.filter(name='tagcloud_linear')
def tagcloud_linear(n, base=10):
	"""
	For the tag cloud on some pages
	"""
	BASE = base
	MAX = 30
	try:
		t = BASE + n * 2 
		if t > MAX:
			return MAX
		else:
			return t
	except:
		return BASE


@register.filter(name='tagcloud_opacity')
def tagcloud_opacity(n):
	"""
	For the tag cloud on some pages - between 0 and 1
	"""
	if n <= 9:
		return n/10.0 + 0.3  # otherwise you don't see it
	elif n >= 10:
		return 1





# useful in expressing values from a M2M relation: returns all of them separated by ';'
@register.filter(name='printmany')
def printmany(lst, object_label = None, delimiter=","):
	e = ""
	if lst:
		n = len(lst)
		if not object_label:
			for x in range(n - 1):
				e += "%s%s " % (lst[x], delimiter)
			e += "%s" % (lst[n -1])
		else:
			for x in range(n - 1):
				label = getattr(lst[x], object_label) or getattr(lst[x], 'id')
				e += "%s%s " % (label, delimiter)
			label = getattr(lst[n - 1], object_label) or getattr(lst[n - 1], 'id') # returns the id if label missing
			e += "%s" % (getattr(lst[n -1], object_label))
	return e


# as above, but also creates the link from the get_absolute_url method
# NEEDS THE SAFE filter too! >>>>>>> objects.all|printmany_withabsoluteurl|safe
@register.filter(name='printmany_withabsoluteurl')
def printmany_withabsoluteurl(lst, object_label = None):
	e = ""
	if lst:
		n = len(lst)
		if object_label:
			for x in range(n - 1):
				label = getattr(lst[x], object_label) or getattr(lst[x], 'id')
				e += "<a href=\"%s\">%s</a>; " % (lst[x].get_absolute_url(), label)
			label = getattr(lst[n - 1], object_label) or getattr(lst[n - 1], 'id')	
			e += "<a href=\"%s\">%s</a>" % (lst[n - 1].get_absolute_url(), getattr(lst[n - 1], object_label))
		else:
			for x in range(n - 1):
				e += "<a href=\"%s\">%s</a>; " % (lst[x].get_absolute_url(), lst[x])
			e += "<a href=\"%s\">%s</a>" % (lst[n - 1].get_absolute_url(), lst[n - 1])
		# e += "%s" % (lst[n -1])
	return e






# 
# ===========
# Model Querying Helpers
# ===========
#


@register.filter
def koncept_publicIntFrags(kon):
	"""Determines if we are on the userpage of an authenticated user
	"""
	return kon.intfrag_set.filter(isprivate=False)
@register.filter
def koncept_privateIntFrags(kon):
	"""Determines if we are on the userpage of an authenticated user
	"""
	return kon.intfrag_set.all()
	
@register.filter
def koncept_userIntFrags(kon, user):
	"""Determines if we are on the userpage of an authenticated user
	"""
	return kon.intfrag_set.filter(created_by=user)	

#
# @register.filter(name='sample_fragment')
# def sample_fragment(kon):
#	"""
#	Get one fragment for a koncept.
#	"""
#	fragment = kon.sample_fragment(True)
#	return fragment or ""
#	# if fragment:
#	#	return fragment.text
#	# return ""
#
# @register.filter(name='sample_fragment_public')
# def sample_fragment_public(kon):
#	"""
#	Get one fragment for a koncept.
#	"""
#	fragment = kon.sample_fragment(False)
#	return fragment or ""



@register.filter(name='document_koncepts_public')
def document_koncepts_public(doc):
	"""
	Get all public koncepts from a document
	"""
	return doc.get_koncepts(include_private=False)

@register.filter(name='document_koncepts_private')
def document_koncepts_private(doc):
	"""
	Get all private koncepts from a document
	"""
	return doc.get_koncepts(include_private=True)


@register.filter(name='document_intfrags_public')
def document_intfrags_public(doc):
	"""
	Get all public intfrags from a document
	"""
	return doc.get_intfrags(include_private=False)

@register.filter(name='document_intfrags_private')
def document_intfrags_private(doc):
	"""
	Get all private intfrags from a document
	"""
	return doc.get_intfrags(include_private=True)
	


@register.filter(name='document_snippets_public')
def document_snippets_public(doc):
	"""
	Get all public snippets from a document
	"""
	return doc.get_snippets(include_private=False)

@register.filter(name='document_snippets_private')
def document_snippets_private(doc):
	"""
	Get all private snippets from a document
	"""
	return doc.get_snippets(include_private=True)
	
		
	
@register.filter(name='get_intcount_for_source')
def get_intcount_for_source(kon, source, user=None):
	"""
	Get the count of all the 
	"""
	return kon.getIntFragments_perSource(source, include_private=False, count=True)




@register.filter(name='count_ideas')
def count_ideas(intfrags):
	"""
	From a list of intfrags, just count the distinct koncepts
	"""
	
	out = []
	for x in intfrags:
		if x.koncept not in out:
			out += [x.koncept]
	return len(out) 
	

@register.filter(name='split_intfrag_list')
def split_intfrag_list(intfrags):
	"""
	For the document detail template: prepares the data so that they can be displayed in two columns
	"""
	first, second, intfrags = [], [], intfrags
	
	if len(intfrags) == 1:
		return [intfrags, []]
	half = len(intfrags) / 2 
	for x in xrange(len(intfrags)):
		if x >= half and intfrags[x].koncept != intfrags[x-1].koncept:
			second.append(intfrags[x])
		else:
			first.append(intfrags[x])
	return [first, second]


@register.filter(name='split_koncept_list')
def split_koncept_list(koncepts):
	"""
	For the person_koncepts detail template: prepares the data so that they can be displayed in two columns
	"""
	
	if len(koncepts) == 1:
		return [koncepts, []]
	else:
		half = len(koncepts) / 2
		return [koncepts[:half], koncepts[half:]]



@register.filter(name='highlightText')
def highlightText(text, match=""):
	"""
	Returns html with css class that allows highlighting text matching a search string
	
	2015-04-07: changed class name to '_s_h' to avoid recursive subs
				made the background color dynamic (default: background: rgb(255, 255, 150);)
	
	# @todo: need a case-insensitive replace function!!! 
	"""
	if match:

		if match[0] == "\"" and match[-1] == "\"":
			multi_match = [match[1:-1]]
		else:
			multi_match = [x.strip() for x in match.split(" ") if x]
		
		for each in multi_match:
			
			idx = multi_match.index(each)
			color_change = 255 - (20 * idx)
			
			this = each.lower()
			text = text.replace(this, "<span class='_s_h' style='background: rgb(255, %d, 150); color: black;'>%s</span>" % (color_change, this))
			this = each.capitalize()
			text = text.replace(this, "<span class='_s_h' style='background: rgb(255, %d, 150); color: black;'>%s</span>" % (color_change, this))
		return text
	else:
		return text



@register.filter(name='myMessageTags')
def myMessageTags(tags):
	""" hack to make the tags labels match newest bootstrap (3.2)"""
	if tags == "error":
		tags = "danger"
	return tags





@register.filter(name='snippetRelativeCount')
def snippetRelativeCount(n1, n2):
	""" """
	return n1 + n2




@register.filter(name='sortbywordcount')
def sortbywordcount(quotes_list):
	""" """
	return sorted(quotes_list, key=lambda x: len(x.text.split()))



@register.filter(name='slicewords')
def slicewords(text, count="1:"):
	""" slice some text by number of words 
		<count> = ":1" or "2:"
	"""
	res = text
	_text = text.split()
	if _text and ":" in count:
		_count = int(count.replace(":", "")) # extract number
		if len(_text) > _count:
			if count[0] == ":":
			# get words up to count
				res = " ".join(_text[:_count])
			else:
				res = " ".join(_text[_count:])
			# get words after count 
	return res



