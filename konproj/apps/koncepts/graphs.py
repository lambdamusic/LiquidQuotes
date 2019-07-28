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
# from koncepts.tag import get_tag_cloud
from settings import printdebug, BOOTSTRAP



def addBRspace(stringa, spacing=5):
    "Adds a \n char every N=spacing words"
    SIZE = spacing
    ss = stringa.split()
    return '\n'.join(' '.join(ss[pos:pos+SIZE]) for pos in xrange(0, len(ss), SIZE))




def getSourceQuotesGraph(doc):
    """
    viz using visjs
    """
    # koncept sources + their related koncepts
    _nodes	= []
    _edges	= []

    rootid = "s_"+ str(doc.id)
    INDEX1 = [rootid] #hack to keep track of what's in there already - the js libs fails otherwise
    top = {'id' : rootid, 'label' : addBRspace(doc.title), 'group' : 'group_root'}
    _nodes += [top]

    for q in doc.fragment_set.all():
        qid = "q_"+ str(q.id)
        if qid != rootid:
            if qid not in INDEX1:
                INDEX1 += [qid]
                _nodes += [{'id' : qid, 'label' : addBRspace(q.title), 'group' : 'group_quote'}]
            _edges += [{'from' : rootid, 'to' : qid, 'label' : "", 'color': 'grey'}]

    return _nodes, _edges






def getSimilarQuotesGraph(quote):
    """
    build the JSON data for the visjs library
    2015-12-27: just testing, results not that good
    """

    # koncept sources + their related koncepts
    nodes1	= []
    edges1	= []

    rootid = "q_"+ str(quote.id)
    INDEX_QUOTES = [rootid] #hack to keep track of what's in there already
    # the js libs fails otherwise
    INDEX_DOCS = []

    top = {'id' : rootid, 'label' : addBRspace(quote.title), 'group' : 'group_root'}
    nodes1 += [top]


    s_1 = quote.source
    if s_1:
        sid = "s_"+ str(s_1.id)
        INDEX_DOCS = [sid]
        nodes1 += [{'id' : sid, 'label' : addBRspace(s_1.title), 'group' : 'group_source'}]
        edges1 += [{'from' : sid, 'to' : rootid, 'label' : ""}]

    similar_quotes = quote.getSimilarQuotes(n=9, user=quote.created_by, onlypublic=False)

    for q in similar_quotes:
        qid = "q_"+ str(q.id)
        if qid != rootid:
            if qid not in INDEX_QUOTES:
                INDEX_QUOTES += [qid]
                nodes1 += [{'id' : qid, 'label' : addBRspace(q.title), 'group' : 'group_quote'}]
                edges1 += [{'from' : rootid, 'to' : qid, 'label' : "similar"}]

            s_2 = q.source
            if s_2:
                sid = "s_" + str(s_2.id)
                if sid not in INDEX_DOCS:
                    INDEX_DOCS += [sid]
                    nodes1 += [{'id': sid, 'label': addBRspace(s_2.title), 'group': 'group_source'}]
                edges1 += [{'from': sid, 'to': qid, 'label': ""}]

    # printdebug(INDEX_DOCS)
    # printdebug(INDEX_QUOTES)
    return nodes1, edges1





