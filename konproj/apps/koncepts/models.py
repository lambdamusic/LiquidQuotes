from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.conf import settings
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse

import string
import difflib
from settings import printdebug, BOOTSTRAP

from django.db.models import Q, Count
import operator

import mptt

from myutils.adminextra.autocomplete_tree_admin import AutocompleteTreeEditor
from myutils.myutils import url_domain, truncate_words, blank_or_string, removeArticles

# import myutils.modelextra.mymodels as mymodels
import koncepts.abstract_models as abstract


# http://stackoverflow.com/questions/875771/how-does-one-encode-and-decode-a-string-with-python-for-use-in-a-url
# http://stackoverflow.com/questions/5557849/is-there-a-unicode-ready-substitute-i-can-use-for-urllib-quote-and-urllib-unquot
# ALso we could have used: https://docs.djangoproject.com/en/dev/ref/unicode/#uri-and-iri-handling
import urllib

EXTRA_SAVING_ACTIONS = True




######################
### UTILS
######################


def nice_titles(s):
    """good for generating titles - for human consumption"""
    return string.capwords(s)

def upperfirst(x):
    return x[0].upper() + x[1:]

# http://stackoverflow.com/questions/1324067/how-do-i-get-str-translate-to-work-with-unicode-strings
def translate_non_alphanumerics(to_translate, translate_to=u''):
    not_letters_or_digits = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
    return to_translate.translate(translate_table)


def url_encode(u):
    return urllib.quote(u.strip().lower().replace(" ", "-").encode('utf8'))

# def url_encode_search(u): # same as above, but nor white space replacing
# 	return urllib.quote(u.strip().lower().encode('utf8'))

def nice_url_name(s):
    """ create strings for urls """

    out = translate_non_alphanumerics(unicode(s))
    return url_encode(out)

def get_firstletter(s):
    """ returns a first letter useful for indexing """
    if s:
        if (s[0] in string.punctuation) or (s[0] in string.digits):
            return "*"
        else:
            return s[0].lower()
    else:
        return ""




######################
### AUTHORITY LISTS
######################

from koncepts.models_authlists import *








######################
### MAIN MODELS
######################



class Fragment(abstract.KonceptEnhancedModel):
    """(Fragment enhanced model - timestamps and creation fields inherited)
    An Fragment is the object that represent a fragment of text eg a note or some text from a website
    AKA Quote or Snippet

    """
    text = models.TextField(verbose_name="text", null=True, blank=True,)
    source = models.ForeignKey('Document', null=True, blank=True, verbose_name="Source (if available)",)

    title = models.CharField(max_length=250, verbose_name="title", null=True, blank=True,)
    comment = models.TextField(verbose_name="comment", null=True, blank=True,)
    location = models.CharField(max_length=100, blank=True, verbose_name="Location of fragment withing the source")

    orderno = models.IntegerField(blank=True, null=True, verbose_name="Order number", help_text="The order of the fragment within its source (if available - defaults to 1)")
    favorite = models.BooleanField(default=False, verbose_name="is mine?")
    clipboard = models.BooleanField(default=False, verbose_name="clipboard")

    # M2m
    # tags = models.ManyToManyField('Tag', null=True, blank=True, verbose_name="tags",)
    subjects = models.ManyToManyField('Subject', null=True, blank=True, verbose_name="subjects",)

    # --not used--
    language = models.ForeignKey('Languages', null=True, blank=True, verbose_name="language",)
    ismine = models.BooleanField(default=False, verbose_name="is mine?")
    isdictionary = models.BooleanField(default=False, verbose_name="Is it a dictionary entry?")
    isbookmark = models.BooleanField(default=False, verbose_name="Is it a bookmark of a url?")
    # for now fragments dont have urls - but in any case....
    # --not used-- Ends

    name_url = models.CharField(max_length=250, blank=True, verbose_name="purified name for url - either entered or generated")

    class Admin(admin.ModelAdmin):
        list_display = ('id', 'title', 'source', 'orderno', 'isprivate', 'updated_at')
        search_fields = ['id', 'text', 'source', 'title']
        list_filter = ('updated_at',  'created_by', 'isprivate')
        raw_id_fields = ("source",)
        fieldsets = [
            ('Administration',
                {'fields':
                    ['editedrecord', 'review', 'internal_notes', ('created_at', 'created_by'),
                      ('updated_at', 'updated_by'), 'isprivate',
                     ],
                'classes': ['collapse']
                }),
            ('',
                {'fields':
                    ['text', 'title', 'comment' ,'source', 'language', 'ismine', 'isdictionary', 'isbookmark', 'name_url'],
                }),
            ]

        def save_model(self, request, obj, form, change):
            """adds the user information when the rec is saved"""
            if getattr(obj, 'created_by', None) is None:
                  obj.created_by = request.user
            obj.updated_by = request.user
            obj.save()


    def get_admin_url(self):
        from django.core import urlresolvers
        return urlresolvers.reverse('admin:koncepts_fragment_change', args=(self.id,))
    get_admin_url.allow_tags = True


    @models.permalink
    def get_absolute_url(self):
        return 'get_quote', [self.created_by.username, self.id]


    def save(self, *args, **kwargs):
        """
        A high orderno number is added by default
        Ordering can be fixed using the Document.cleanOrdering() method
        """
        if EXTRA_SAVING_ACTIONS:
            super(Fragment, self).save(*args, **kwargs)
            if not self.orderno:
                self.orderno = 999 # put last - will be changed later
            if not self.title:
                self.title = truncate_words(self.text, 5)
            self.title = upperfirst(self.title)
        super(Fragment, self).save(*args, **kwargs)


    def get_koncept(self):
        """ helper to retrieve the koncept associated to a fragment
            NOTE: We assume there's only one interpretation per fragment
        """
        if self.intfrag_set.all():
            return self.intfrag_set.all()[0].koncept
        else:
            return None

    def get_interpretation(self):
        """helper to retrieve the first interpretation associated to a snippet
            NOTE: We assume there's only one interpretation per fragment
        """
        if self.intfrag_set.all():
            return self.intfrag_set.all()[0]
        else:
            return None


    def get_nextQuote(self, only_public=True, anyuser=False, sameKoncept=False, sameDocument=False):
        """Returns the next quote based on creation chronology"""
        query = {}
        if not anyuser:
            query['created_by'] =  self.created_by
        if only_public:
            query['isprivate'] = False

        # 3 cases:
        if sameKoncept:
            if self.get_interpretation():
                query['intfrag__koncept'] = self.get_koncept()
                _query = query.copy()
                _query['intfrag__orderno__gt'] = self.get_interpretation().orderno
                test = Fragment.objects.filter(**_query).order_by("intfrag__orderno")
            else:
                test = None
        if sameDocument:
            query['source'] = self.source
            _query = query.copy()  # put in komodo prev results
            _query['id__gt'] = self.id
            test = Fragment.objects.filter(**_query).order_by("pk") #.exclude(id=self.id)
        if not sameKoncept and not sameDocument:
            _query = query.copy()
            _query['id__gt'] = self.id
            test = Fragment.objects.filter(**_query).order_by("pk")
        # finally
        if test:
            return test[0]
        else: # return first element [= wrap around]
            test = Fragment.objects.filter(**query).order_by("pk")
            if test and test.count() > 1:
                return test[0]
            else:
                return None



    def get_prevQuote(self, only_public=True, anyuser=False, sameKoncept=False, sameDocument=False):
        """Returns the next quote based on creation chronology"""
        query = {}
        if not anyuser:
            query['created_by'] =  self.created_by
        if only_public:
            query['isprivate'] = False

        # 3 cases:
        if sameKoncept:
            if self.get_interpretation():
                query['intfrag__koncept'] = self.get_koncept()
                query['intfrag__orderno__lt'] = self.get_interpretation().orderno
                test = Fragment.objects.filter(**query).order_by("-intfrag__orderno")
            else:
                test = None
        if sameDocument:
            query['source'] = self.source
            query['id__lt'] = self.id
            test = Fragment.objects.filter(**query).order_by("-pk")
        if not sameKoncept and not sameDocument:
            query['id__lt'] = self.id
            test = Fragment.objects.filter(**query).order_by("-pk")
        # fianlly
        if test:
            return test[0]
        else:
            return None


    def getQuotesWithSameSubjects(self, n=99, user=None, onlypublic=True, sameSource=False):
        """
        return a list of quotes that share the same tags (name)
        NOTE: tags are actually <subjects>!!

        :param n: how many
        :param user: instance of user
        :param onlypublic: boolean
        :return: a list of quotes

        @todo: return as a dictionary that keeps track of which tag per quote
        """
        output = []
        qset = Fragment.objects.filter()
        if user:
            qset = qset.filter(created_by=user)
        if onlypublic:
            qset = qset.filter(isprivate=False)
        if not sameSource:
            qset = qset.exclude(source=self.source)
        subjects = self.subjects.all()
        exclude_id = [self.id]
        for t1 in subjects:
            res = list(qset.exclude(pk__in=exclude_id).filter(subjects=t1))
            if res:
                output += (res)
                if len(output) > n:
                    return output[:n]
                exclude_id += [x.id for x in res]
        return output


    def getSimilarQuotes(self, n=3, user=None, onlypublic=True):
        """
        Util that does some string matching to suggest similar quotes.
        If the user is None, only public quotes are returned.
        """

        def similar(seq1, seq2):
            return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.4


        output = []

        qset = Fragment.objects.filter()
        if user:
            qset = qset.filter(created_by=user)
        if onlypublic:
            qset = qset.filter(isprivate=False)

        # get a queryset that (roughly) matches the nouns in the title
        predicates = [('title__icontains', x) for x in removeArticles(self.title).split()]

        # printdebug(predicates)
        if predicates:
            qset = qset.filter(reduce(operator.or_, [Q(x) for x in predicates]))

            # iterate over it and extract the best matches
            for x in qset:
                # print "*" * 10, x
                if x.id != self.id and similar(removeArticles(self.title), removeArticles(x.title)):
                    if x not in output:
                        output += [x]
                        if len(output) == n:
                            break

            # add quotes related via tags?
            #
            # for el in self.getRelatedKonceptsViaSources()[:5]:
            # 	if el not in output:
            # 		output = [el] + output

        # printdebug(output)
        return output


    def getMoreFromSameSource(self, only_public=True, max=10):
        """return a list of more quotes from same doc - wrapping around and 
        starting from the current quote index"""

        query = {}
        if only_public:
            query['isprivate'] = False

        query['source'] = self.source

        if self.source.fragment_set.count() > 1:
            _query = query.copy()  # put in komodo prev results
            _query['id__gt'] = self.id
            test = Fragment.objects.filter(**_query).order_by("pk") #.exclude(id=self.id)
            
            # finally
            if test and test.count() >= max:
                return list(test)[:max]
            else: # return first element [= wrap around]
                query['id__lt'] = self.id
                wrap_around = Fragment.objects.filter(**query).order_by("pk")
                if test.count() > 1 or wrap_around.count() > 1:
                    return list(test) + list(wrap_around)[:max-test.count()]
                else:
                    return None
        else:
            return None





    class Meta:
        verbose_name_plural="Fragments"
        verbose_name = "Fragments"
        ordering = ["orderno"]

    def __unicode__(self):
        if self.source:
            return "[from %s..] \"%s\"" % (force_unicode(self.source.title[:20]), force_unicode(self.text[:100]))
        else:
            return "[no source] \"%s\"" % (force_unicode(self.text[:100]),)

    table_group = 'Main models'





class Document(abstract.KonceptEnhancedModel):
    """
    Document - enhanced model - timestamps and creation fields inherited)

    January 13, 2014:
    Documents are user-specific, and unique among a single user too.

    """

    title = models.CharField(max_length=300, verbose_name="title")
    author = models.CharField(blank=True, max_length=200, verbose_name="author")
    pubyear = models.IntegerField(blank=True, null=True, verbose_name="publication year", help_text="")
    url = models.URLField(blank=True, verify_exists=False, max_length=300)
    description = models.TextField(blank=True, verbose_name="description (put everything in here for now)")

    fulltext = models.TextField(blank=True, verbose_name="fulltext - in some cases we may want to add it")

    name_url = models.CharField(max_length=250, blank=True, verbose_name="purified name for url - either entered or generated")

    searchindex = models.TextField(blank=True, verbose_name="field used for search")

    class Admin(admin.ModelAdmin):
        list_display = ('id', 'title', 'author', 'isprivate', 'updated_at')
        search_fields = ['id', 'title', 'author']
        list_filter = ('updated_at',  'created_by', 'isprivate')
        fieldsets = [
            ('Administration',
                {'fields':
                    ['editedrecord', 'review', 'internal_notes', ('created_at', 'created_by'),
                      ('updated_at', 'updated_by'), 'isprivate',
                     ],
                'classes': ['collapse']
                }),
            ('',
                {'fields':
                    ['title', 'author', 'description', 'url', 'pubyear', 'fulltext'],
                }),
            ]

        def save_model(self, request, obj, form, change):
            """adds the user information when the rec is saved"""
            if getattr(obj, 'created_by', None) is None:
                  obj.created_by = request.user
            obj.updated_by = request.user
            obj.save()


    def get_admin_url(self):
        from django.core import urlresolvers
        # TODO: substitute and downcase the path!
        return urlresolvers.reverse('admin:koncepts_document_change', args=(self.id,))
    get_admin_url.allow_tags = True


    @models.permalink
    def get_absolute_url(self):
        return 'get_document', [self.created_by.username, self.name_url]

    # def get_absolute_url(self):
    # 	path = reverse('search_user_quotes',  args=[self.created_by.username])
    # 	return path + "?d=%d" % self.id

    def save(self, *args, **kwargs):
        if EXTRA_SAVING_ACTIONS:
            super(Document, self).save(*args, **kwargs)
            self.title = nice_titles(self.title)
            self.searchindex = self.buildSearchIndex()
            if not self.name_url:
                # documents can have duplicate with same title, so we use the ID in the URL
                self.name_url = nice_url_name(str(self.id) + " " + self.title[:200])
        super(Document, self).save(*args, **kwargs)


    def get_koncepts(self, include_private=True):
        """
            January 13, 2014:
            Retrieves all unique Koncepts linked to a document. Should be user-specific.

            Note:
                to get fragments, it's enough to do <document.fragment_set.all()>
        """

        if include_private:
            koncepts = Koncept.objects.filter(intfrag__fragment__source=self).distinct()
        else:
            koncepts = Koncept.objects.filter(intfrag__fragment__source=self, intfrag__fragment__isprivate=False).distinct()
        return koncepts


    def get_intfrags(self, include_private=True):
        """
            April 2, 2014:
            Retrieves all Intfrags linked to a document. Should be user-specific.
        """

        if include_private:
            intfrags = IntFrag.objects.filter(fragment__source=self)
        else:
            intfrags = IntFrag.objects.filter(fragment__source=self, fragment__isprivate=False)
        return intfrags


    def get_snippets(self, include_private=True):
        """
            August 29, 2014:
            Retrieves all Snippets linked to a document. Should be user-specific.
        """

        if include_private:
            snippets = Fragment.objects.filter(source=self)
        else:
            snippets = Fragment.objects.filter(source=self, isprivate=False)
        return snippets


    def mergeWithDocument(self, d2):
        """
        method that attaches all references to D2 to this document (self), and then eliminates D2
        """
        for fragment in d2.fragment_set.all():
            fragment.source = self
            fragment.save()
            printdebug("Moved %s from %s to %s" % (fragment, d2, self ))
        d2.delete()


    def getRelatedDocuments(self, include_private=True, useSimilarity=False, user=None):
        """
        Get a list of all the other documents that have related koncepts
        """
        res = []
        for k in self.get_koncepts():
            res += k.getSources(include_private)
        res = list(set(res))
        if self in res:
            res.remove(self)
        else:
            pass

        if useSimilarity and len(res) < 2:

            res2 = []
            for k in self.get_koncepts():
                ksimilar = k.getSimilarKoncepts(n=2, user=user)
                for k2 in ksimilar:
                    res2 += k2.getSources(include_private)
            res2 = list(set(res2+res))
            if self in res2:
                res2.remove(self)
            res = res2

        return res


    def get_nextDocument(self, only_public=True, anyuser=False):
        """Returns the next document based on creation chronology"""
        query = {'created_at__gt': self.created_at}
        if not anyuser:
            query['created_by'] =  self.created_by
        if only_public:
            query['fragment__isprivate'] = False
        test = Document.objects.filter(**query).order_by("created_at")
        if test:
            return test[0]
        else:
            return None


    def get_url_domain(self):
        if self.url:
            return url_domain(self.url)
        else:
            return ""

    def cleanOrdering(self):
        """
        Gets all related fragments and checks that
        a) they have an orderno and
        b) it is sequential and starts from 1
        """
        counter = 0
        for f in self.fragment_set.all().order_by('orderno', 'created_at'):
            printdebug("Fragment %d orderno %s in source %d" % (f.id, str(f.orderno), self.id))
            counter += 1
            if not f.orderno or f.orderno != counter:
                f.orderno = counter
                f.save()
                printdebug("== changed Fragment %d orderno %s" % (f.id, str(f.orderno)))

    def buildSearchIndex(self):
        "generates a string collation of all the fields we want to search for"
        temp = "%s %s %s" % (self.title, self.author, self.description)
        return temp.lower()



    class Meta:
        verbose_name_plural="Document"
        verbose_name = "Document"
        ordering = ["title"]

    def __unicode__(self):
        if self.author:
            return "\"%s\", by %s" % (force_unicode(self.title), self.author)
        else:
            return "\"%s\"" % force_unicode(self.title)

    table_group = 'Main models'







# ---------------------------------


# 2015-08-11: NEW


# ---------------------------------


class Subject(abstract.KonceptEnhancedModel):
    """(Subject enhanced authority list + mptt tree model
        Timestamps and creation fields inherited + name and description)

    2015-08-11: this replaced the Tag model, allowing also hierarchical data

    """
    name = models.CharField(max_length=250)
    name_url = models.CharField(max_length=250, blank=True, verbose_name="purified name for url - either entered or generated")
    description = models.TextField(blank=True)
    first_letter = models.CharField(max_length=1, verbose_name="initial letter")


    parent =  models.ForeignKey('self', null=True, blank=True, verbose_name="parent",
            related_name='children')
    helper_topancestor = models.CharField(max_length=765, null=True, blank=True, verbose_name="root ancestor - utility field",)
    helper_name = models.CharField(max_length=765, null=True, blank=True, verbose_name="helper name used for diplay purposes",)



    class Admin(admin.ModelAdmin):
        list_display = ( 'name', 'id', 'parent', 'editedrecord', 'review','updated_by', 'updated_at',)
        list_display_links = ('id',)
        list_filter = ['updated_at', 'updated_by', 'editedrecord', 'review', 'helper_topancestor']
        search_fields = ['id', 'name']
        related_search_fields = {	'parent': ('name',),   }
        fieldsets = [
            ('Administration',
                {'fields':
                    ['editedrecord', 'review', 'internal_notes', ('created_at', 'created_by'),
                      ('updated_at', 'updated_by')
                     ],
                'classes': ['collapse']
                }),
            ('',
                {'fields':
                    ['name', 'description', 'parent', ],
                }),
            ]
        #class Media:
            #js = ("js/admin_fixes/fix_fields_size.js",)

        def save_model(self, request, obj, form, change):
            """adds the user information when the rec is saved"""
            if getattr(obj, 'created_by', None) is None:
                  obj.created_by = request.user
            obj.updated_by = request.user
            obj.save()



    def __nameandparent__(self):
        exit = ""
        if self.parent:
            return "%s (%s)" % (blank_or_string(self.name), blank_or_string(self.parent.name))
        else:
            return blank_or_string(self.name)

    def show_ancestors_tree(self):
        exit = ", ".join([blank_or_string(el.name) for el in self.get_ancestors().reverse()])
        if exit:
            exit = "%s (%s)" % (blank_or_string(self.name), exit)
        else:
            exit = blank_or_string(self.name)
        return exit

    def get_admin_url(self):
        from django.core import urlresolvers
        # TODO: substitute and downcase the path!
        return urlresolvers.reverse('admin:koncepts_subject_change', args=(self.id,))
    get_admin_url.allow_tags = True

    # @models.permalink
    def get_absolute_url(self):
        """2015-08-24: for the moment return the search quotes page"""
        path = reverse('search_user_quotes',  args=[self.created_by.username])
        return path + "?subject=%d" % self.id
        # return path + "?subject=%s" % self.name_url

    def save(self, *args, **kwargs):
        if EXTRA_SAVING_ACTIONS:
            super(Subject, self).save(*args, **kwargs)
            temp = self.get_root().name
            self.util_topancestor = temp
            self.name = nice_titles(self.name)
            self.first_letter = get_firstletter(self.name)
            self.name_url = nice_url_name(self.name)
        super(Subject, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ 2015-08-25: Overriding the delete method so that it takes care of the hierarchy
            Also: the related fragment relationships are handled as needed.
        """
        _list = self.get_descendants(include_self=True)
        for s in _list:
            printdebug("Checking fragments for %s " % s.name)
            for f in s.fragment_set.all():
                f.subjects.remove(s)
                printdebug("Removing %s from fragment %d" % (s.name, f.id))
        printdebug("Deleting.... %s " % s.name)
        super(Subject, self).delete(*args, **kwargs)


    @classmethod
    def subjectsListPerUser(self, user, onlyPublic=False, totcount=False, count_fragments=False, count_limit=1):
        """
        Retrieves all subjects of a user
        Note: there is also a shortcut method in UserProfile.get_tags [not for subjects!]
        2015-03-17: updated
        2015-08-25: adapted from older tag method
        """
        mydict = {'created_by': user }

        if onlyPublic:
            mydict['fragment__isprivate'] = False
            if totcount:
                return Subject.objects.filter(**mydict).distinct().count()

            elif count_fragments:

                return Subject.objects.filter(**mydict).annotate(count=Count('fragment')).filter(count__gte=count_limit)

            else: # just return the tags
                return Subject.objects.filter(**mydict).distinct()

        else:

            if totcount:
                return Subject.objects.filter(**mydict).distinct().count()

            elif count_fragments:
                return Subject.objects.filter(**mydict).annotate(count=Count('fragment')).filter(count__gte=count_limit)

            else: # just return the tags
                return Subject.objects.filter(**mydict).distinct()


    @classmethod
    def cleanUpUserSubjects(self, user, test_set=[]):
        """
        Removes all unused subjects for a user
        > test_set = attempt to clean up only a subset of tags (eg after an update operation)
        > if a tag has children, the user has to delete it manually
        """
        if not test_set: # default to all tags
            test_set = Subject.objects.filter(created_by=user)

        for s in test_set:
            if not s.fragment_set.all() and not s.children.all():
                printdebug("Cleaning up subject %s" % s)
                s.delete()



    class Meta:
        verbose_name_plural="Subject"
        verbose_name = "Subject"
        ordering = ['tree_id', 'lft', 'name', ]

    def __unicode__(self):
        return self.name # show_ancestors_tree()


mptt.register( Subject,)








class Koncept(abstract.KonceptEnhancedModel):
    """(Koncept enhanced model - timestamps and creation fields inherited)

    AKA Collection

    Note (December 11, 2013):
    - A Koncept is specific to a user
    - Name is unique within a user. No two Koncepts with same name can be created.
        - this req could be relaxed in the future, *currently ENFORCED at DB level*!
        - note: django admin doesn't handle this well eg when adding duplicates for testing you get a 500

    """
    name = models.CharField(max_length=250, verbose_name="name")
    name_url = models.CharField(max_length=250, blank=True, verbose_name="purified name for url - either entered or generated")

    description = models.TextField(blank=True, verbose_name="description")

    first_letter = models.CharField(max_length=1, verbose_name="initial letter")

    class Admin(admin.ModelAdmin):
        list_display = ('id', 'name', 'isprivate', 'updated_at')
        search_fields = ['id', 'name',]
        list_filter = ('updated_at',  'created_by', 'isprivate')
        fieldsets = [
            ('Administration',
                {'fields':
                    ['editedrecord', 'review', 'internal_notes', ('created_at', 'created_by'),
                      ('updated_at', 'updated_by'), 'isprivate',
                     ],
                'classes': ['collapse']
                }),
            ('',
                {'fields':
                    ['name', 'name_url', 'description'],
                }),
            ]

        def save_model(self, request, obj, form, change):
            """adds the user information when the rec is saved
                note: created_by/updated_by can be set only via admin!
            """
            if getattr(obj, 'created_by', None) is None:
                  obj.created_by = request.user
            obj.updated_by = request.user
            obj.save()


    def get_admin_url(self):
        from django.core import urlresolvers
        return urlresolvers.reverse('admin:koncepts_koncept_change', args=(self.id,))
    get_admin_url.allow_tags = True


    @models.permalink
    def get_absolute_url(self):
        return 'get_koncept', [self.created_by.username, str(self.id) + "-" + self.name_url]


    def save(self, *args, **kwargs):
        if EXTRA_SAVING_ACTIONS:
            super(Koncept, self).save(*args, **kwargs)
            self.name = nice_titles(self.name)
            self.first_letter = get_firstletter(self.name)
            if True:
                self.name_url = nice_url_name(self.name)
        super(Koncept, self).save(*args, **kwargs)




    def get_fragments(self, include_private=True):
        """
            February 11, 2015
            Returns all fragments for a koncept
        """

        try:
            if include_private:
                intfrags = self.intfrag_set.all()
            else:
                intfrags = self.intfrag_set.filter(fragment__isprivate=False)
            return [i.fragment for i in intfrags]
        except:
            return None


    def sample_fragment(self, include_private=False):
        """
            December 11, 2013
            Returns a fragment instance that can be used as a sample.
        """

        try:
            if include_private:
                intfrag = self.intfrag_set.all()[0]
            else:
                intfrag = self.intfrag_set.filter(fragment__isprivate=False)[0]
            return intfrag.fragment
        except:
            return None

    def sampleFragmentPrivate(self):
        """
            2014-11-28: Returns the first PRIVATE or PUBLIC fragment instance
        """

        try:
            intfrag = self.intfrag_set.all()[0]
            return intfrag.fragment
        except:
            return ""

    def sampleFragmentPublic(self):
        """
            2014-11-28: Returns the first PUBLIC fragment instance
        """

        try:
            intfrag = self.intfrag_set.filter(fragment__isprivate=False)[0]
            return intfrag.fragment
        except:
            return ""


    def get_next(self, only_public=True, anyuser=False):
        """Returns the next koncept based on creation chronology
            2015-01-12: bootstrapped, no options at all, defaults to public only
        """
        # query = {}
        # if not anyuser:
        #	query['created_by'] =  self.created_by
        # if only_public:
        #	query['isprivate'] = False
        if only_public:
            return self.get_next_by_created_at(isprivate=False, created_by=self.created_by)
        else:
            return self.get_next_by_created_at(created_by=self.created_by)



    def public_or_private(self):
        """
        Shortcut to determine whether the interpretations associagted to a koncept are
        all public, private or a mix of the two
        1 = private
        2 = public
        3 = mixed
        """
        private, public = False, False
        for i in self.intfrag_set.all():
            if i.fragment.isprivate:
                private = True
            else:
                public = True
        if private == True and public == False:
            return 1
        if private == False and public == True:
            return 2
        if private == True and public == True:
            return 3


    def getIntFragments_perSource(self, source, include_private=False, count=False):
        """
            Returns all fragment instances for a specific source
        """
        mydict = {'fragment__source': source }
        if not include_private:
            mydict['fragment__isprivate'] = False
        if count:
            return self.intfrag_set.filter(**mydict).count()
        else:
            return self.intfrag_set.filter(**mydict)



    def getSources(self, include_private=True, count=False, countFragments=False):
        """
        Returns all sources for a koncept
        > countFragments: allows to count how many fragments exist per source: {s1 : 2, s2 : 3, s3 : 1}
        @todo: include_private not implemented
        """
        mydict = {'fragment__intfrag__koncept': self }
        if not include_private:
            mydict['fragment__isprivate'] = False
        if count:
            return Document.objects.filter(**mydict).distinct().count()
        elif countFragments:
            # instead of distinct() we do the counting ourselves
            allsources = list(Document.objects.filter(**mydict))
            return dict((i,allsources.count(i)) for i in allsources)
        else:
            return Document.objects.filter(**mydict).distinct()
    def getSourcesPublic(self):
        return self.getSources(include_private=False)
    def getSourcesPrivate(self):
        return self.getSources()

    def hasEmptySources(self):
        """ Checks if a koncept is linked to fragments that have no
            associated document defined eg a simple note
        """
        return self.intfrag_set.filter(fragment__source=None).count()


    def getstats_public(self):
        "returns some counts eg for public display"
        d = {}
        d['sources'] = self.getSources(include_private=False, count=True)
        d['quotes'] = self.intfrag_set.filter(fragment__isprivate=False).count()
        return d

    def getstats_private(self):
        d = {}
        d['sources'] = self.getSources(include_private=True, count=True)
        d['quotes'] = self.intfrag_set.count()
        return d

    def getRelatedKonceptsViaSources(self, include_private=True):
        """
        Get a list of all the other koncepts that have the same source
        """
        res = []
        for s in self.getSources():
            res += s.get_koncepts(include_private)
        res = list(set(res))
        if self in res:
            res.remove(self)
            return res
        else:
            return res


    def mergeWithKoncept(self, k2):
        """
        method that attaches all references to K2 to this koncept (self), and eliminates K2
        """
        for intfrag in k2.intfrag_set.all():
            intfrag.koncept = self
            intfrag.save()
            printdebug("Moved %s from %s to %s" % (intfrag, k2, self ))
        # in the future we'll have to handle also projects, intKoncepts etc..
        k2.delete()


    def getSimilarKoncepts(self, n=3, user=None, onlypublic=True):
        """
        Util that does some string matching to suggest similar koncepts.
        If the user is None, only public koncepts are returned.
        """

        def similar(seq1, seq2):
            return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.3

        def removeArticles(text):
            articles = ['and', 'a', 'the', 'an', 'of', 'for', 'to', 'in', 'by', 'at', 'with']
            newText = ''
            for word in text.lower().split(' '):
                if word not in articles:
                    newText += word+' '
            return newText[:-1]

        output = []

        qset = Koncept.objects.filter()
        if user:
            qset = qset.filter(created_by=user)
        if onlypublic:
            qset = qset.filter(intfrag__fragment__isprivate=False)

        # get a queryset that (roughly) matches the nouns in the Koncept name
        predicates = [('name__icontains', x) for x in removeArticles(self.name).split()]

        qset = qset.filter(reduce(operator.or_, [Q(x) for x in predicates]))

        # iterate over it and extract the best matches
        for x in qset:
            # print "*" * 10, x
            if x.id != self.id and similar(removeArticles(self.name), removeArticles(x.name)):
                if x not in output:
                    output += [x]
                    if len(output) == n:
                        break

        # add koncepts from related sources

        for el in self.getRelatedKonceptsViaSources()[:5]:
            if el not in output:
                output = [el] + output

        return output


    def cleanIntFragOrdering(self):
        """
        Gets all intfrags and checked that
        a) they have an orderno and
        b) it is sequential and starts from 1
        """
        counter = 0
        for intfrag in self.intfrag_set.all().order_by('orderno', 'created_at'):
            printdebug("Intfrag %d orderno %s" % (intfrag.id, str(intfrag.orderno)))
            counter += 1
            if not intfrag.orderno or intfrag.orderno != counter:
                intfrag.orderno = counter
                intfrag.save()
                printdebug("== changed Intfrag %d orderno %s" % (intfrag.id, str(intfrag.orderno)))


    class Meta:
        verbose_name_plural="Koncepts"
        verbose_name = "Koncept"
        ordering = ["name"]
        unique_together = (("name", "created_by"),)

    def __unicode__(self):
        return "%s" % force_unicode(self.name)

    table_group = 'Main models'






######################

### INTEPRETATIONS - ie Fragment m2m Koncept

######################






class IntFrag(abstract.KonceptEnhancedModel):
    """(IntFrag enhanced model - timestamps and creation fields inherited)

    An IntFrag is the object that connects one koncepts and one fragment

    """
    koncept = models.ForeignKey('Koncept', verbose_name="Koncept",)
    fragment = models.ForeignKey('Fragment', verbose_name="Fragment",)

    project = models.ForeignKey('Project', null=True, blank=True, verbose_name="Project (blank=default workspace)",)
    # tags = models.ManyToManyField('Tag', null=True, blank=True, verbose_name="tags",)

    orderno = models.IntegerField(blank=True, null=True, verbose_name="Order number", help_text="The order of the fragment in the thread")

    class Admin(admin.ModelAdmin):
        list_display = ('id',  'koncept', 'fragment', 'orderno', 'project', 'updated_at')
        search_fields = ['id', 'koncept', 'fragment',]
        list_filter = ('updated_at',  'created_by', 'isprivate')
        # filter_horizontal = ('tags',)
        raw_id_fields = ("koncept", 'fragment')
        fieldsets = [
            ('Administration',
                {'fields':
                    ['editedrecord', 'review', 'internal_notes', ('created_at', 'created_by'),
                      ('updated_at', 'updated_by'), 'isprivate',
                     ],
                'classes': ['collapse']
                }),
            ('',
                {'fields':
                    ['koncept',	 'fragment', 'orderno',	 'project',],
                }),
            ]

        def save_model(self, request, obj, form, change):
            """adds the user information when the rec is saved"""
            if getattr(obj, 'created_by', None) is None:
                  obj.created_by = request.user
            obj.updated_by = request.user
            obj.save()


    def get_admin_url(self):
        from django.core import urlresolvers
        # TODO: substitute and downcase the path!
        return urlresolvers.reverse('admin:koncepts_intepretfragment_change', args=(self.id,))
    get_admin_url.allow_tags = True





    @models.permalink
    def get_absolute_url(self):
        # TODO: substitute and downcase the path!
        return ('intepretfragment_detail', [str(self.id)])

    def save(self, *args, **kwargs):
        """
        if no order number is provided, 9999 is added (so to go at the end) and then the
        'cleanIntFragOrdering' action is launched
        """
        if EXTRA_SAVING_ACTIONS:
            super(IntFrag, self).save(*args, **kwargs)
            if not self.orderno:
                self.orderno = 9999
        super(IntFrag, self).save(*args, **kwargs)
        if self.orderno == 9999:
            self.koncept.cleanIntFragOrdering()


    class Meta:
        verbose_name_plural="IntFrag"
        verbose_name = "IntFrag"
        ordering = ["orderno"]

    def __unicode__(self):
        return "[%s] => [%s] =in proj= [%s]" % (force_unicode(self.koncept), force_unicode(self.fragment), self.project)

    table_group = 'Main models'














######################

### NOT USED ..............

######################












class Project(abstract.KonceptEnhancedModel):
    """(Project enhanced model - timestamps and creation fields inherited)

    2015-11-17: NOT USED

    The idea of a project is that I can separate out koncepts, fragments and interpretations into various spaces.
    For now I've added the model, but haven't thought much about the UI.
    Eventually we'll add collaborative features based on this model (eg users that can see/modify items in a project)

    January 2, 2015:
        added m2m links to koncepts and fragments
        name limited to 5 words max

    """

    name = models.CharField(max_length=200, verbose_name="name")
    description = models.TextField(blank=True, verbose_name="description")

    koncepts = models.ManyToManyField('Koncept', null=True, blank=True, verbose_name="koncepts",)
    fragments = models.ManyToManyField('Fragment', null=True, blank=True, verbose_name="fragments",)

    name_url = models.CharField(max_length=250, blank=True, verbose_name="purified name for url - either entered or generated")


    class Admin(admin.ModelAdmin):
        list_display = ('id', 'name', 'isprivate', 'updated_at')
        list_display_links = ('id', 'name')
        search_fields = ['id']
        list_filter = ('updated_at',  'created_by', 'isprivate')
        #filter_horizontal = (,)
        #related_search_fields = { 'fieldname': ('searchattr_name',)}
        #inlines = (inlineModel1, inlineModel2)
        fieldsets = [
            ('Administration',
                {'fields':
                    ['editedrecord', 'review', 'internal_notes', ('created_at', 'created_by'),
                      ('updated_at', 'updated_by'), 'isprivate',
                     ],
                'classes': ['collapse']
                }),
            ('',
                {'fields':
                    ['name', 'description', 'name_url'],
                }),
            ]
        #class Media:
            #js = ("js/admin_fixes/fix_fields_size.js",)

        def save_model(self, request, obj, form, change):
            """adds the user information when the rec is saved"""
            if getattr(obj, 'created_by', None) is None:
                  obj.created_by = request.user
            obj.updated_by = request.user
            obj.save()


    def get_admin_url(self):
        from django.core import urlresolvers
        # TODO: substitute and downcase the path!
        return urlresolvers.reverse('admin:ontodocs_project_change', args=(self.id,))
    get_admin_url.allow_tags = True


    @models.permalink
    def get_absolute_url(self):
        # TODO: 2015-02-24: needs to be updated (unused)
        return ('search_user_koncepts', [self.created_by.username])

        # return 'get_koncept', [self.created_by.username, str(self.id) + "-" + self.name_url]

    def save(self, force_insert=False, force_update=False):
        if EXTRA_SAVING_ACTIONS:
            super(Project, self).save(force_insert, force_update)
            self.name = " ".join(self.name.strip().split()[:5]) # MAX words
            if len(self.name) > 30:
                self.name = self.name[:30]
            # self.name = nice_titles(self.name) # capitalization
            RESERVED_COLLECTIONS = ['all', 'last-week', 'last-month', 'orphans']
            if self.name in RESERVED_COLLECTIONS:
                self.name = "my-" +	 self.name
            self.name_url = nice_url_name(self.name)
        super(Project, self).save(force_insert, force_update)

    class Meta:
        verbose_name_plural="Project"
        verbose_name = "Project"
        ordering = ["id"]

    def __unicode__(self):
        return "Project %s" % self.name

    table_group = '1. Main models'






# August 24, 2015: superseded by subject, which is also hiearchical

# July 31, 2016: finally removed (Subject is the new tag!)


# class Tag(mymodels.EnhancedAuthorityList):
#     """(Context enhanced authority list model
#         Timestamps and creation fields inherited + name and description)
#     """

#     name_url = models.CharField(max_length=250, blank=True, verbose_name="purified name for url - either entered or generated")
#     totcount = models.IntegerField(blank=True, null=True, verbose_name="Total number of tagged fragments")

#     class Admin(admin.ModelAdmin):
#         list_display = ('id', 'name', 'updated_at')
#         search_fields = ['id', 'name',]
#         list_filter = ('updated_at', )
#         fieldsets = [
#             ('Administration',
#                 {'fields':
#                     ['editedrecord', 'review', 'internal_notes', ('created_at', 'created_by'),
#                       ('updated_at', 'updated_by')
#                      ],
#                 'classes': ['collapse']
#                 }),
#             ('',
#                 {'fields':
#                     ['name', 'name_url', 'description', ],
#                 }),
#             ]

#         def save_model(self, request, obj, form, change):
#             """adds the user information when the rec is saved"""
#             if getattr(obj, 'created_by', None) is None:
#                   obj.created_by = request.user
#             obj.updated_by = request.user
#             obj.save()


#     def get_admin_url(self):
#         from django.core import urlresolvers
#         # TODO: substitute and downcase the path!
#         return urlresolvers.reverse('admin:koncepts_tag_change', args=(self.id,))
#     get_admin_url.allow_tags = True


#     @models.permalink
#     def get_absolute_url(self):
#         """Note: this the generic page for a tag.
#         The user-specific one can be reached in the template like this:
#             {% url search_user_quotes request.user %}?tag={{t.name}}
#         """
#         # January 17, 2014: @todo: this generic view doesn't exist yet
#         return 'get_tag', [self.name_url]

#     def save(self, *args, **kwargs):
#         if EXTRA_SAVING_ACTIONS:
#             super(Tag, self).save(*args, **kwargs)
#             if not self.name_url:
#                 self.name_url = nice_url_name(self.name)
#         super(Tag, self).save(*args, **kwargs)


#     class Meta:
#         verbose_name_plural="Tags"
#         verbose_name = "Tag"
#         ordering = ["name"]

#     def __unicode__(self):
#         return "%s" % self.name


#     @classmethod
#     def tagsListPerUser(self, user, onlyPublic=False, totcount=False, count_fragments=False, count_limit=1):
#         """
#         Retrieves all tags of a user
#         Note: there is also a shortcut method in UserProfile.get_tags
#         2015-03-17: updated
#         """
#         mydict = {'created_by': user }

#         if onlyPublic:
#             mydict['fragment__isprivate'] = False
#             if totcount:
#                 return Tag.objects.filter(**mydict).distinct().count()

#             elif count_fragments:

#                 return Tag.objects.filter(**mydict).annotate(count=Count('fragment')).filter(count__gte=count_limit)

#             else: # just return the tags
#                 return Tag.objects.filter(**mydict).distinct()

#         else:

#             if totcount:
#                 return Tag.objects.filter(**mydict).distinct().count()

#             elif count_fragments:
#                 return Tag.objects.filter(**mydict).annotate(count=Count('fragment')).filter(count__gte=count_limit)

#             else: # just return the tags
#                 return Tag.objects.filter(**mydict).distinct()


#     @classmethod
#     def cleanUpUserTags(self, user, test_set=[]):
#         """
#         Removes all unused tags for a user
#         > test_set = attempt to clean up only a subset of tags (eg after an update operation)
#         """
#         if not test_set: # default to all tags
#             test_set = Tag.objects.filter(created_by=user)

#         for t in test_set:
#             if not t.fragment_set.all():
#                 printdebug("Deleting Tag %s" % t)
#                 t.delete()


#     table_group = 'Main models'













class IntKon(abstract.KonceptEnhancedModel):
    """(IntKon enhanced model - timestamps and creation fields inherited)

    EXPERIMENTAL - NOT USED

    An IntKon is the object that connects two koncepts with a relationship
    Eg: k1 is subconcept of k2 ; k3 is 'rel' to k4.

    """
    term1 = models.ForeignKey('Koncept', verbose_name="First Koncept interpreted", related_name="term1_of")
    term2 = models.ForeignKey('Koncept', verbose_name="Second Koncept interpreted", related_name="term2_of")

    description = models.TextField(blank=True, verbose_name="description")

    relation = models.ForeignKey('RelationKon', null=True, blank=True, verbose_name="relation from K1 to K2",)
    hasPart = models.BooleanField(default=False, verbose_name="Kon1 has part Kon2?", help_text="Shortcut field for subclass relationships")

    project = models.ForeignKey('Project', null=True, blank=True, verbose_name="Project (blank=default workspace)",)

    orderno = models.IntegerField(blank=True, null=True, verbose_name="Order number", help_text="An ordering - if needed")

    class Admin(admin.ModelAdmin):
        list_display = ('id',  'term1', 'term2', 'hasPart', 'relation', 'orderno', 'project', 'updated_at')
        search_fields = ['id', 'term1', 'term2',]
        list_filter = ('updated_at',  'created_by', 'isprivate')
        # filter_horizontal = ('context',)
        raw_id_fields = ("term1", 'term2')
        fieldsets = [
            ('Administration',
                {'fields':
                    ['editedrecord', 'review', 'internal_notes', ('created_at', 'created_by'),
                      ('updated_at', 'updated_by'), 'isprivate',
                     ],
                'classes': ['collapse']
                }),
            ('Terms interpreted',
                {'fields':
                    [('term1',	'term2'),  'project', ],
                }),
            ('Relation',
                {'fields':
                    ['relation', 'hasPart', 'description', 'orderno' ],
                'classes': ['collapse']
                }),
            ]

        def save_model(self, request, obj, form, change):
            """adds the user information when the rec is saved"""
            if getattr(obj, 'created_by', None) is None:
                  obj.created_by = request.user
            obj.updated_by = request.user
            obj.save()


    def get_admin_url(self):
        from django.core import urlresolvers
        # TODO: substitute and downcase the path!
        return urlresolvers.reverse('admin:koncepts_intepretkoncept_change', args=(self.id,))
    get_admin_url.allow_tags = True


    @models.permalink
    def get_absolute_url(self):
        # TODO: substitute and downcase the path!
        return ('intepretkoncept_detail', [str(self.id)])

    def save(self, *args, **kwargs):
        if EXTRA_SAVING_ACTIONS:
            # super(IntKon, self).save(*args, **kwargs)
            pass
        super(IntKon, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural="IntKon"
        verbose_name = "IntKon"
        ordering = ["id"]

    def __unicode__(self):
        if self.relation:
            return "[%s] %s [%s]" % (self.term1, self.relation, self.term2)
        else:
            return "[%s] %s [%s]" % (self.term1, self.hasPart, self.term2)

    table_group = 'Main models'
















