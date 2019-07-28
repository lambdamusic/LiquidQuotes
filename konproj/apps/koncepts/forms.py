from django import forms
from django.forms import ModelForm, Textarea, TextInput, RadioSelect
from django.forms.extras.widgets import SelectDateWidget

from koncepts.models import *
from settings import printdebug, BOOTSTRAP

from registration.models import TIMEZONE_CHOICES




##################
#  
#  forms
#
##################


class NewQuoteForm(forms.Form):
	"""
	Form that combines the quote and koncept creation
	"""

	text = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 70, 'rows': 15}))
	title = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 80,}))
	location = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 80,}))
	comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 70, 'rows': 15}))	
	isprivate = forms.BooleanField(label="Private", initial=True, required=False)
		
	konid = forms.IntegerField(required=False,)
	name = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 80,})) 
	konceptoverwrite = forms.BooleanField(label="Overwrite?", initial=False,  required=False, )
		
	tags = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 35,})) 
	# ismine = forms.BooleanField(required=False, label="Mine?")
	# isdictionary = forms.BooleanField(required=False, label="Dictionary entry?")
	# isbookmark = forms.BooleanField(required=False, label="Bookmark?")
	
	# section for new source

	sourceoverwrite = forms.BooleanField(required=False, label="Overwrite?",  initial=False, )
	sourcetitle = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 80,}))
	sourceurl = forms.URLField(max_length=200, required=False, widget=forms.TextInput(attrs={'size': 80,})) 
	sourceauthor = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'size': 80,}))
	sourcedesc = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 60, 'rows': 8}))
	sourcepubyear = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': 20,}))

	def clean_name(self):
		name = self.cleaned_data.get('name')

		if name.isdigit():
			raise forms.ValidationError("Sorry. Koncepts containing only numbers are not allowed.")
		return name







# the form : it includes fields for creating a new Source too...
# class NewKonceptForm(forms.Form):
# 	"""
# 	Form that combines the koncept and interpretation fields
# 	"""
#
# 	konid = forms.IntegerField(required=False,)
# 	name = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 80,}))
# 	text = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 70, 'rows': 15}))
# 	isprivate = forms.BooleanField(label="Private", initial=True,  required=False, )
#
# 	konceptoverwrite = forms.BooleanField(label="Overwrite?", initial=False,  required=False, )
# 	tags = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 35,}))
# 	# ismine = forms.BooleanField(required=False, label="Mine?")
# 	# isdictionary = forms.BooleanField(required=False, label="Dictionary entry?")
# 	# isbookmark = forms.BooleanField(required=False, label="Bookmark?")
#
# 	# section for new source
#
# 	sourceoverwrite = forms.BooleanField(required=False, label="Overwrite?",  initial=False, )
# 	sourcetitle = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 80,}))
# 	sourceurl = forms.URLField(max_length=200, required=False, widget=forms.TextInput(attrs={'size': 80,}))
# 	sourceauthor = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'size': 80,}))
# 	sourcedesc = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 60, 'rows': 8}))
# 	sourcepubyear = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': 20,}))
#
# 	def clean_name(self):
# 		name = self.cleaned_data.get('name')
#
# 		if name.isdigit():
# 			raise forms.ValidationError("Sorry. Koncepts containing only numbers are not allowed.")
# 		return name
#



class NewDocumentForm(forms.Form):
	"""
	Form that extracts the document specific fields only
	"""
	sourceoverwrite = forms.BooleanField(required=False, label="Overwrite?",  initial=False, )
	sourcetitle = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 80,}))
	sourceurl = forms.URLField(max_length=200, required=False, widget=forms.TextInput(attrs={'size': 80,})) 
	sourceauthor = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'size': 80,}))
	sourcepubyear = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'size': 20,}))
	sourcedesc = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 60, 'rows': 8}))







class ImportFileForm(forms.Form):
	file  = forms.FileField(required=False,)
	text = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 120, 'rows': 20}))
	# CHOICES = (('sumnontes', 'Sumnotes.net PDF export'),
	# 		   ('simplelist', 'Snippets list'),
	# 		   # ('autodetect','autodetect'),
	# 			)
	# filetype = forms.ChoiceField(choices=CHOICES,  initial='autodetect', widget=forms.RadioSelect(), required=True,)








class ImportKonceptForm(forms.Form):
	"""
	Form that combines the koncept and interpretation fields
	"""

	doimport = forms.BooleanField(required=False, label="Create?", initial=False)
	name = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 80,})) 
	frag = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 100, 'rows': 5}))
	source = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 90,}))
	location = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 40,}))
	# tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 80,}))
	# April 15, 2014: hidden field used only for warnings
	duplicates_info = forms.CharField(required=False, widget=forms.TextInput(attrs={'size': 90,}))








class ProfileForm(forms.Form):
	"""
	Form for the profile change page
	"""

	username = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 80,})) 
	email = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'size': 80,})) 

	first_name = forms.CharField(required=False, max_length=300, widget=forms.TextInput(attrs={'size': 80,})) 
	last_name = forms.CharField(required=False, max_length=300, widget=forms.TextInput(attrs={'size': 80,})) 

	timezone = forms.ChoiceField(required=False, widget=forms.Select, choices=TIMEZONE_CHOICES) 





class SettingsForm(forms.Form):
	"""
	Form for the settings change page
	"""

	privateKonceptDefault = forms.BooleanField(required=False, label="When a new Koncept is created, default to private", initial=False)
	privateUser = forms.BooleanField(required=False, label="I don't want to show up on the public users list", initial=False)










# https://docs.djangoproject.com/en/dev/topics/http/file-uploads/?from=olddocs
# class UploadFileForm(forms.Form):
# 	file  = forms.FileField(required=False,)
# 	text = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 120, 'rows': 20}))
# 	CHOICES = (('simplefile', 'Empty-line delimited list of koncepts'),					
# 			   ('kindle', 'Kindle highlights'), 
# 			   # ('autodetect','autodetect'),
# 				)
# 	filetype = forms.ChoiceField(choices=CHOICES,  initial='autodetect', widget=forms.RadioSelect(), required=True,)
# 






