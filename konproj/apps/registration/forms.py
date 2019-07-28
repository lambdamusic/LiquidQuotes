"""
Forms and validation code for user registration.

"""


from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate


from django.conf import settings

# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = { 'class': 'required' }




# October 8, 2013: hacking the standard login form so to let you log in with email too

class KonceptsAuthenticationForm(forms.Form):
	"""
	Base class for authenticating users. Extend this to get a form that accepts
	username/password logins.
	"""
	username = forms.CharField(label=_("Username"), max_length=30)
	password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

	def __init__(self, request=None, *args, **kwargs):
		"""
		If request is passed in, the form will validate that cookies are
		enabled. Note that the request (a HttpRequest object) must have set a
		cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
		running this validation.
		"""
		self.request = request
		self.user_cache = None
		super(KonceptsAuthenticationForm, self).__init__(*args, **kwargs)

	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		
		# if it may be an email address, try loggin in with it
		if username and "@" in username and "." in username:
			try:
				username = User.objects.get(email=username.lower())
			except User.DoesNotExist:
				pass
		
		if username and password:
			self.user_cache = authenticate(username=username, password=password)
			if self.user_cache is None:
				raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
			elif not self.user_cache.is_active:
				raise forms.ValidationError(_("This account is inactive."))
		self.check_for_test_cookie()
		return self.cleaned_data

	def check_for_test_cookie(self):
		if self.request and not self.request.session.test_cookie_worked():
			raise forms.ValidationError(
				_("Your Web browser doesn't appear to have cookies enabled. "
				  "Cookies are required for logging in."))

	def get_user_id(self):
		if self.user_cache:
			return self.user_cache.id
		return None

	def get_user(self):
		return self.user_cache











# October 6, 2013: hacking the registration form

class KonceptsRegistrationForm(forms.Form):
	"""
	Form for registering a new user account.
	
	Validates 
	- that the requested username is not already in use
	- requires the password to be entered twice to catch typos.
	- contains an invitation code

	
	"""
	username = forms.RegexField(regex=r'^\w+$',
								max_length=30,
								widget=forms.TextInput(attrs=attrs_dict),
								label=_("Username"),
								error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })
	email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
															   maxlength=75)),
							 label=_("Email address"))
							 
	firstname = forms.CharField(required=False, widget=forms.Textarea(), label=_("First Name"))						 
	lastname = forms.CharField(required=False, widget=forms.Textarea(), label=_("Last Name"))						 
							 
	password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
								label=_("Password"))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
								label=_("Password (again)"))


	tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
							 label=_(u'I have read and agree to the Terms of Service'),
							 error_messages={ 'required': _("You must agree to the terms to register") })

	# for beta

	invitationcode = forms.CharField(required=False, widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
								label=_("Invitation Code"))


	
	def clean_username(self):
		"""
		Validate that the username is alphanumeric and is not already
		in use.
		
		"""
		
		if self.cleaned_data['username'] in settings.REGISTRATION_RESERVED:
			raise forms.ValidationError(_("A user with that username already exists."))
		
		try:
			username = self.cleaned_data['username'].lower()
			user = User.objects.get(username__iexact=username)
		except User.DoesNotExist:
			return username
		raise forms.ValidationError(_("A user with that username already exists."))

	def clean_email(self):
		"""
		Validate that the supplied email address is unique for the
		site.
		
		"""
		if User.objects.filter(email__iexact=self.cleaned_data['email']):
			raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
		return self.cleaned_data['email']


	def clean_password1(self):
		"""
		Validate that the first password has at least 6 chars
		
		"""
		if 'password1' in self.cleaned_data:
			if len(self.cleaned_data['password1']) < 6:
				raise forms.ValidationError(_("Please enter a password with at least 6 characters."))
		return self.cleaned_data['password1']
		
		
	def clean_password2(self):
		"""
		Validate that the two passwords are the same
		
		"""
		if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
			if self.cleaned_data['password1'] != self.cleaned_data['password2']:
				raise forms.ValidationError(_("The two password fields didn't match."))
		return self.cleaned_data['password2']


	def clean_invitationcode(self):
		"""
		Validate that the invitation code is correct
		
		"""
		if 'invitationcode' in self.cleaned_data:
			pass   # April 11, 2014: disabled
			# if self.cleaned_data['invitationcode'] != "bemyguest": 
			#	raise forms.ValidationError(_("The invitation code isn't valid.")) 

		return self.cleaned_data['invitationcode']
				
















# ---------------------------------

# standard code

# ---------------------------------



class RegistrationForm(forms.Form):
	"""
	Form for registering a new user account.
	
	Validates that the requested username is not already in use, and
	requires the password to be entered twice to catch typos.
	
	Subclasses should feel free to add any additional validation they
	need, but should avoid defining a ``save()`` method -- the actual
	saving of collected user data is delegated to the active
	registration backend.
	
	"""
	username = forms.RegexField(regex=r'^\w+$',
								max_length=30,
								widget=forms.TextInput(attrs=attrs_dict),
								label=_("Username"),
								error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })
	email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
															   maxlength=75)),
							 label=_("Email address"))
	invitationcode = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
								label=_("Invitation Code"))
	password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
								label=_("Password"))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
								label=_("Password (again)"))

							 
								 
	def clean_username(self):
		"""
		Validate that the username is alphanumeric and is not already
		in use.
		
		"""
		try:
			user = User.objects.get(username__iexact=self.cleaned_data['username'])
		except User.DoesNotExist:
			return self.cleaned_data['username']
		raise forms.ValidationError(_("A user with that username already exists."))


		
	def clean(self):
		"""
		Verifiy that the values entered into the two password fields
		match. Note that an error here will end up in
		``non_field_errors()`` because it doesn't apply to a single
		field.
		
		"""
		if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
			if self.cleaned_data['password1'] != self.cleaned_data['password2']:
				raise forms.ValidationError(_("The two password fields didn't match."))
		if 'invitationcode' in self.cleaned_data:
			if self.cleaned_data['invitationcode'] != "bemyguest":
				raise forms.ValidationError(_("The invitation code isn't valid.")) 
		return self.cleaned_data


class RegistrationFormTermsOfService(RegistrationForm):
	"""
	Subclass of ``RegistrationForm`` which adds a required checkbox
	for agreeing to a site's Terms of Service.
	
	"""
	tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
							 label=_(u'I have read and agree to the Terms of Service'),
							 error_messages={ 'required': _("You must agree to the terms to register") })


class RegistrationFormUniqueEmail(RegistrationForm):
	"""
	Subclass of ``RegistrationForm`` which enforces uniqueness of
	email addresses.
	
	"""
	def clean_email(self):
		"""
		Validate that the supplied email address is unique for the
		site.
		
		"""
		if User.objects.filter(email__iexact=self.cleaned_data['email']):
			raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
		return self.cleaned_data['email']


class RegistrationFormNoFreeEmail(RegistrationForm):
	"""
	Subclass of ``RegistrationForm`` which disallows registration with
	email addresses from popular free webmail services; moderately
	useful for preventing automated spam registrations.
	
	To change the list of banned domains, subclass this form and
	override the attribute ``bad_domains``.
	
	"""
	bad_domains = ['aim.com', 'aol.com', 'email.com', 'gmail.com',
				   'googlemail.com', 'hotmail.com', 'hushmail.com',
				   'msn.com', 'mail.ru', 'mailinator.com', 'live.com',
				   'yahoo.com']
	
	def clean_email(self):
		"""
		Check the supplied email address against a list of known free
		webmail domains.
		
		"""
		email_domain = self.cleaned_data['email'].split('@')[1]
		if email_domain in self.bad_domains:
			raise forms.ValidationError(_("Registration using free email addresses is prohibited. Please supply a different email address."))
		return self.cleaned_data['email']
