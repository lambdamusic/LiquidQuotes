from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.conf import settings
import urllib

import myutils.modelextra.mymodels as mymodels
import myutils.modelextra.myfields as myfields
from django.contrib.auth.models import User

# import mptt
# from myutils.adminextra.autocomplete_tree_admin import AutocompleteTreeEditor

EXTRA_SAVING_ACTIONS = True

from koncepts.models import nice_url_name, nice_titles




class RelationKon(mymodels.EnhancedAuthorityList):
	"""(Relation enhanced authority list model 
		Timestamps and creation fields inherited + name and description)
	"""
	


	class Admin(admin.ModelAdmin):
		list_display = ('id', 'name', 'description', 'updated_at')
		list_display_links = ('id',)
		search_fields = ['name']
		list_filter = ('created_at', 'updated_at', 'created_by', 'editedrecord', 'review',)
		#filter_horizontal = (,) 
		#related_search_fields = { 'fieldname': ('searchattr_name',)}
		#inlines = (inlineModel1, inlineModel2)
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
					['name', 'description', ],	 
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
		return urlresolvers.reverse('admin:koncepts_relationkon_change', args=(self.id,))
	get_admin_url.allow_tags = True


	@models.permalink
	def get_absolute_url(self):
		# TODO: substitute and downcase the path!
		return ('relationkon_detail', [str(self.id)])
			
	def save(self, force_insert=False, force_update=False):
		if EXTRA_SAVING_ACTIONS:
			# super(RelationKon, self).save(force_insert, force_update)
			pass
		super(RelationKon, self).save(force_insert, force_update) 

			
	class Meta:
		verbose_name_plural="RelationKon"
		verbose_name = "RelationKon"
		
	def __unicode__(self):
		return "%s" % self.name
	
	table_group = '2. Authority Lists'








class Languages(mymodels.EnhancedAuthorityList):
	"""(Languages enhanced authority list model 
		Timestamps and creation fields inherited + name and description)
	"""



	class Admin(admin.ModelAdmin):
		list_display = ('id', 'name', 'updated_at')
		search_fields = ['id', 'name',]
		list_filter = ('updated_at', )
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
					['name', 'description', ],	 
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
		return urlresolvers.reverse('admin:koncepts_Languages_change', args=(self.id,))
	get_admin_url.allow_tags = True


	@models.permalink
	def get_absolute_url(self):
		# TODO: substitute and downcase the path!
		return ('Languages_detail', [str(self.id)])

	def save(self, *args, **kwargs):
		if EXTRA_SAVING_ACTIONS:
			# super(Languages, self).save(*args, **kwargs)
			pass
		super(Languages, self).save(*args, **kwargs) 


	class Meta:
		verbose_name_plural="Languages"
		verbose_name = "Language"
		ordering = ["name"]

	def __unicode__(self):
		return "%s" % self.name

	table_group = 'Authority Lists'





# modifier before the weekday
FAQ_categories = [
	('a', 'Using the Site'),
	('b', 'General Issues'),
	('c', 'Sharing and Copyright'),
]



class FAQitem(mymodels.EnhancedAuthorityList):
	"""(FAQitem enhanced authority list model 
		Timestamps and creation fields inherited + name and description)
	"""
	orderno = models.IntegerField(blank=True, null=True, verbose_name="Order number", help_text="The order of FAQ item")
	category = models.CharField(blank=True, max_length=3, choices=FAQ_categories,	
			verbose_name="Category",)
		
	class Admin(admin.ModelAdmin):
		list_display = ('id', 'name', 'orderno', 'category', 'updated_at')
		search_fields = ['id', 'name',]
		list_filter = ('updated_at', 'category')
		list_editable = ['name', 'orderno', 'category',]
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
					['name', 'description', 'orderno', 'category' ],	 
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
		return urlresolvers.reverse('admin:koncepts_FAQitem_change', args=(self.id,))
	get_admin_url.allow_tags = True



	def save(self, *args, **kwargs):
		if EXTRA_SAVING_ACTIONS:
			# super(Languages, self).save(*args, **kwargs)
			pass
		super(FAQitem, self).save(*args, **kwargs) 


	class Meta:
		verbose_name_plural="FAQitems"
		verbose_name = "FAQitem"
		ordering = [ "category", "orderno", ]

	def __unicode__(self):
		return "%s" % self.name

	table_group = 'Authority Lists'








# 
# ===========
# April 13, 2014 : imported models :: REMOVED FOR NOW
# ===========


# 
# 
# class ImportedSource(models.Model):
# 	"""
# 	Model to store temporarily stuff being imported in bulk
# 	User-based, but it gets deleted at regular times
# 	"""
# 	created_at = myfields.CreationDateTimeField(_('created'), 
# 				help_text="Do not modify. The time this record was firstly created.", editable=False)
# 	created_by = models.ForeignKey(User, blank=True, null=True, related_name="created_%(class)s", 
# 		editable = True, )
# 	title = models.CharField(max_length=300, verbose_name="title")
# 	url = models.URLField(blank=True, verify_exists=False, max_length=300)
# 	isprivate = models.BooleanField(default=False, verbose_name="is private", blank=True,)	
# 		
# 
# 	def save(self, *args, **kwargs):
# 		if EXTRA_SAVING_ACTIONS:
# 			# super(Languages, self).save(*args, **kwargs)
# 			pass
# 		super(ImportedSource, self).save(*args, **kwargs) 
# 
# 
# 	class Meta:
# 		verbose_name_plural="ImportedSources"
# 		verbose_name = "ImportedSource"
# 		ordering = [ "created_at", "created_by", ]
# 
# 	def __unicode__(self):
# 		return "%s" % self.title
# 
# 
# 
# class ImportedKoncept(models.Model):
# 	"""
# 	Model to store temporarily stuff being imported in bulk
# 	User-based, but it gets deleted at regular times
# 	"""
# 	created_at = myfields.CreationDateTimeField(_('created'), 
# 				help_text="Do not modify. The time this record was firstly created.", editable=False)
# 	created_by = models.ForeignKey(User, blank=True, null=True, related_name="created_%(class)s", 
# 		editable = True, )
# 	title = models.CharField(max_length=300, verbose_name="title")
# 	text = models.TextField(verbose_name="text", null=True, blank=True,) 
# 	source = models.ForeignKey('ImportedSource', null=True, blank=True, verbose_name="Source (if available)",)		
# 	isprivate = models.BooleanField(default=False, verbose_name="is private", blank=True,)	
# 	
# 	def save(self, *args, **kwargs):
# 		if EXTRA_SAVING_ACTIONS:
# 			# super(Languages, self).save(*args, **kwargs)
# 			pass
# 		super(ImportedKoncept, self).save(*args, **kwargs) 
# 
# 
# 	class Meta:
# 		verbose_name_plural="ImportedKoncepts"
# 		verbose_name = "ImportedKoncept"
# 		ordering = [ "created_at", "created_by", ]
# 
# 	def __unicode__(self):
# 		return "%s" % self.title
# 
# 





