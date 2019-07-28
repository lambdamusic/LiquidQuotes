#!/usr/bin/env python
# encoding: utf-8

"""


##################
# 
#	views for /quote/	 - created on 2014-10-17
#
##################


"""

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.utils.html import strip_tags, escape
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils import simplejson
from django.core.urlresolvers import reverse

from django.db.models import Q
import operator

from myutils.myutils import paginator_helper

from koncepts.models import *
from koncepts.graphs import *

# from koncepts.tag import get_tag_cloud
from settings import printdebug, BOOTSTRAP






def get_random_quote(request):

    """
    View that returns a redirect to a random quote
    """

    searchdict = {}

    # compose search dictionary
    if request.user.is_authenticated():
        searchdict['created_by'] = request.user
    else:
        searchdict['isprivate'] = False

    try:
        f = Fragment.objects.filter(**searchdict).order_by('?')[0]
        return HttpResponseRedirect('%s' % f.get_absolute_url())
    except:
        return HttpResponseRedirect('/')




def get_quote(request, username, quote_id):
    """
    View that manages the single-quote request.

    """

    q1 = None
    searchdict = {}
    view_var = request.GET.get('v', None)

    person = get_object_or_404(User, username=username)

    context = {'person' : person} # initialize context

    if request.user and request.user.is_authenticated() and person.username == request.user.username:
        context['mykoncepts'] = True
    else:
        context['mykoncepts'] = False

    # compose search dictionary: private koncept-intepretations are seen only by logged in users

    if context['mykoncepts']:
        searchdict['created_by'] = request.user
        searchdict['id'] = quote_id
        usertags = [s.name for s in Subject.subjectsListPerUser(request.user)]
        if usertags:
            context['usertags'] = usertags
    else:
        searchdict['created_by'] = person
        searchdict['id'] = quote_id
        searchdict['isprivate'] = False

    # do the search
    try:
        q1 = Fragment.objects.filter(**searchdict)[0]
    except:
        raise Http404

    if context['mykoncepts']:
        onlyPublic = False
    else:
        onlyPublic = True

    totQuotesDocument = 0
    nextQuoteSource = None
    totQuotesKoncept = 0
    nextQuoteGeneric = None
    prevQuoteGeneric = None

    if False:
        nextQuoteKoncept = q1.get_nextQuote(only_public=onlyPublic, anyuser=False, sameKoncept=True, sameDocument=False)
        prevQuoteKoncept = q1.get_prevQuote(only_public=onlyPublic, anyuser=False, sameKoncept=True, sameDocument=False)

    kon = q1.get_koncept()

    if kon:
        if onlyPublic:
            totQuotesKoncept = kon.intfrag_set.filter(fragment__isprivate=False).count()
        else:
            totQuotesKoncept = kon.intfrag_set.count()

    if q1.source:
        totQuotesDocument = q1.source.get_snippets(include_private=not(onlyPublic)).count()
        if totQuotesDocument > 1:
            nextQuoteSource = q1.get_nextQuote(only_public=onlyPublic, anyuser=False, sameKoncept=False, sameDocument=True)


    nextQuoteGeneric = q1.get_nextQuote(only_public=onlyPublic, anyuser=False, sameKoncept=False, sameDocument=False)
    prevQuoteGeneric = q1.get_prevQuote(only_public=onlyPublic, anyuser=False, sameKoncept=False, sameDocument=False)


    context.update({
                'q1' : q1,
                'page_flag' : 'quote_detail',
                # 'nextQuoteKoncept' : nextQuoteKoncept,
                # 'prevQuoteKoncept' : prevQuoteKoncept,
                'nextQuoteSource' : nextQuoteSource,

                'nextQuoteGeneric' : nextQuoteGeneric,
                'prevQuoteGeneric' : prevQuoteGeneric,

                'totQuotesKoncept' : totQuotesKoncept,
                'totQuotesDocument' : totQuotesDocument,

            })


    if True: # 2015-12-27: just testing the graph
        nodes, edges = getSimilarQuotesGraph(q1)
        context.update({
             'nodes': simplejson.dumps(nodes),
             'edges': simplejson.dumps(edges),
        })


    if True:
        quotesSameSource = q1.getMoreFromSameSource(only_public=onlyPublic, max=7)
        similarQuotesTags = q1.getQuotesWithSameSubjects(n=7, onlypublic=onlyPublic, sameSource=False)
        context.update({
             'quotesSameSource': quotesSameSource,
             'similarQuotesTags': similarQuotesTags
        })

    return render_to_response(BOOTSTRAP + 'pages/quote_detail.html',
                            context,
                            context_instance=RequestContext(request))












