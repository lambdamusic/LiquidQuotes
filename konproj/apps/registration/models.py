import datetime
import random
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count

from koncepts.models import Koncept, Document, IntFrag, Fragment, Subject


SHA1_RE = re.compile('^[a-f0-9]{40}$')


class RegistrationManager(models.Manager):
	"""
	Custom manager for the ``RegistrationProfile`` model.
	
	The methods defined here provide shortcuts for account creation
	and activation (including generation and emailing of activation
	keys), and for cleaning out expired inactive accounts.
	
	"""
	def activate_user(self, activation_key):
		"""
		Validate an activation key and activate the corresponding
		``User`` if valid.
		
		If the key is valid and has not expired, return the ``User``
		after activating.
		
		If the key is not valid or has expired, return ``False``.
		
		If the key is valid but the ``User`` is already active,
		return ``False``.
		
		To prevent reactivation of an account which has been
		deactivated by site administrators, the activation key is
		reset to the string constant ``RegistrationProfile.ACTIVATED``
		after successful activation.

		"""
		# Make sure the key we're trying conforms to the pattern of a
		# SHA1 hash; if it doesn't, no point trying to look it up in
		# the database.
		if SHA1_RE.search(activation_key):
			try:
				profile = self.get(activation_key=activation_key)
			except self.model.DoesNotExist:
				return False
			if not profile.activation_key_expired():
				user = profile.user
				user.is_active = True
				user.save()
				profile.activation_key = self.model.ACTIVATED
				profile.save()
				return user
		return False
	
	def create_inactive_user(self, username, email, password,
							 site, send_email=True):
		"""
		Create a new, inactive ``User``, generate a
		``RegistrationProfile`` and email its activation key to the
		``User``, returning the new ``User``.

		By default, an activation email will be sent to the new
		user. To disable this, pass ``send_email=False``.
		
		"""
		new_user = User.objects.create_user(username, email, password)
		new_user.is_active = False
		new_user.save()

		registration_profile = self.create_profile(new_user)

		if send_email:
			registration_profile.send_activation_email(site)

		return new_user
	create_inactive_user = transaction.commit_on_success(create_inactive_user)

	def create_profile(self, user):
		"""
		Create a ``RegistrationProfile`` for a given
		``User``, and return the ``RegistrationProfile``.
		
		The activation key for the ``RegistrationProfile`` will be a
		SHA1 hash, generated from a combination of the ``User``'s
		username and a random salt.
		
		"""
		salt = sha_constructor(str(random.random())).hexdigest()[:5]
		activation_key = sha_constructor(salt+user.username).hexdigest()
		return self.create(user=user,
						   activation_key=activation_key)
		
	def delete_expired_users(self):
		"""
		Remove expired instances of ``RegistrationProfile`` and their
		associated ``User``s.
		
		Accounts to be deleted are identified by searching for
		instances of ``RegistrationProfile`` with expired activation
		keys, and then checking to see if their associated ``User``
		instances have the field ``is_active`` set to ``False``; any
		``User`` who is both inactive and has an expired activation
		key will be deleted.
		
		It is recommended that this method be executed regularly as
		part of your routine site maintenance; this application
		provides a custom management command which will call this
		method, accessible as ``manage.py cleanupregistration``.
		
		Regularly clearing out accounts which have never been
		activated serves two useful purposes:
		
		1. It alleviates the ocasional need to reset a
		   ``RegistrationProfile`` and/or re-send an activation email
		   when a user does not receive or does not act upon the
		   initial activation email; since the account will be
		   deleted, the user will be able to simply re-register and
		   receive a new activation key.
		
		2. It prevents the possibility of a malicious user registering
		   one or more accounts and never activating them (thus
		   denying the use of those usernames to anyone else); since
		   those accounts will be deleted, the usernames will become
		   available for use again.
		
		If you have a troublesome ``User`` and wish to disable their
		account while keeping it in the database, simply delete the
		associated ``RegistrationProfile``; an inactive ``User`` which
		does not have an associated ``RegistrationProfile`` will not
		be deleted.
		
		"""
		for profile in self.all():
			if profile.activation_key_expired():
				user = profile.user
				if not user.is_active:
					user.delete()


class RegistrationProfile(models.Model):
	"""
	A simple profile which stores an activation key for use during
	user account registration.
	
	Generally, you will not want to interact directly with instances
	of this model; the provided manager includes methods
	for creating and activating new accounts, as well as for cleaning
	out accounts which have never been activated.
	
	While it is possible to use this model as the value of the
	``AUTH_PROFILE_MODULE`` setting, it's not recommended that you do
	so. This model's sole purpose is to store data temporarily during
	account registration and activation.
	
	"""
	ACTIVATED = u"ALREADY_ACTIVATED"
	
	user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
	activation_key = models.CharField(_('activation key'), max_length=40)
	
	objects = RegistrationManager()
	
	class Meta:
		verbose_name = _('registration profile')
		verbose_name_plural = _('registration profiles')
	
	def __unicode__(self):
		return u"Registration information for %s" % self.user
	
	def activation_key_expired(self):
		"""
		Determine whether this ``RegistrationProfile``'s activation
		key has expired, returning a boolean -- ``True`` if the key
		has expired.
		
		Key expiration is determined by a two-step process:
		
		1. If the user has already activated, the key will have been
		   reset to the string constant ``ACTIVATED``. Re-activating
		   is not permitted, and so this method returns ``True`` in
		   this case.

		2. Otherwise, the date the user signed up is incremented by
		   the number of days specified in the setting
		   ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
		   days after signup during which a user is allowed to
		   activate their account); if the result is less than or
		   equal to the current date, the key has expired and this
		   method returns ``True``.
		
		"""
		expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
		return self.activation_key == self.ACTIVATED or \
			   (self.user.date_joined + expiration_date <= datetime.datetime.now())
	activation_key_expired.boolean = True

	def send_activation_email(self, site):
		"""
		Send an activation email to the user associated with this
		``RegistrationProfile``.
		
		The activation email will make use of two templates:

		``bstrap3.2.0/registration/activation_email_subject.txt``
			This template will be used for the subject line of the
			email. Because it is used as the subject line of an email,
			this template's output **must** be only a single line of
			text; output longer than one line will be forcibly joined
			into only a single line.

		``bstrap3.2.0/registration/activation_email.txt``
			This template will be used for the body of the email.

		These templates will each receive the following context
		variables:

		``activation_key``
			The activation key for the new account.

		``expiration_days``
			The number of days remaining during which the account may
			be activated.

		``site``
			An object representing the site on which the user
			registered; depending on whether ``django.contrib.sites``
			is installed, this may be an instance of either
			``django.contrib.sites.models.Site`` (if the sites
			application is installed) or
			``django.contrib.sites.models.RequestSite`` (if
			not). Consult the documentation for the Django sites
			framework for details regarding these objects' interfaces.

		"""
		ctx_dict = { 'activation_key': self.activation_key,
					 'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
					 'site': site }
		subject = render_to_string('bstrap3.2.0/registration/activation_email_subject.txt',
								   ctx_dict)
		# Email subject *must not* contain newlines
		subject = ''.join(subject.splitlines())
		
		message = render_to_string('bstrap3.2.0/registration/activation_email.txt',
								   ctx_dict)
		
		self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)




# October 27, 2013: added based on http://blog.tivix.com/2012/01/06/extending-user-model-in-django/

from django.db.models.signals import post_save

TIMEZONE_CHOICES = (
	("-12.0", "(GMT -12:00) Eniwetok, Kwajalein"),
	("-11.0", "(GMT -11:00) Midway Island, Samoa"),
	("-10.0", "(GMT -10:00) Hawaii"),
	("-9.0", "(GMT -9:00) Alaska"),
	("-8.0", "(GMT -8:00) Pacific Time (US & Canada)"),
	("-7.0", "(GMT -7:00) Mountain Time (US & Canada)"),
	("-6.0", "(GMT -6:00) Central Time (US & Canada), Mexico City"),
	("-5.0", "(GMT -5:00) Eastern Time (US & Canada), Bogota, Lima"),
	("-4.0", "(GMT -4:00) Atlantic Time (Canada), Caracas, La Paz"),
	("-3.5", "(GMT -3:30) Newfoundland"),
	("-3.0", "(GMT -3:00) Brazil, Buenos Aires, Georgetown"),
	("-2.0", "(GMT -2:00) Mid-Atlantic"),
	("-1.0", "(GMT -1:00 hour) Azores, Cape Verde Islands"),
	("0.0", "(GMT) Western Europe Time, London, Lisbon, Casablanca"),
	("1.0", "(GMT +1:00 hour) Brussels, Copenhagen, Madrid, Paris"),
	("2.0", "(GMT +2:00) Kaliningrad, South Africa"),
	("3.0", "(GMT +3:00) Baghdad, Riyadh, Moscow, St. Petersburg"),
	("3.5", "(GMT +3:30) Tehran"),
	("4.0", "(GMT +4:00) Abu Dhabi, Muscat, Baku, Tbilisi"),
	("4.5", "(GMT +4:30) Kabul"),
	("5.0", "(GMT +5:00) Ekaterinburg, Islamabad, Karachi, Tashkent"),
	("5.5", "(GMT +5:30) Bombay, Calcutta, Madras, New Delhi"),
	("5.75", "(GMT +5:45) Kathmandu"),
	("6.0", "(GMT +6:00) Almaty, Dhaka, Colombo"),
	("7.0", "(GMT +7:00) Bangkok, Hanoi, Jakarta"),
	("8.0", "(GMT +8:00) Beijing, Perth, Singapore, Hong Kong"),
	("9.0", "(GMT +9:00) Tokyo, Seoul, Osaka, Sapporo, Yakutsk"),
	("9.5", "(GMT +9:30) Adelaide, Darwin"),
	("10.0", "(GMT +10:00) Eastern Australia, Guam, Vladivostok"),
	("11.0", "(GMT +11:00) Magadan, Solomon Islands, New Caledonia"),
	("12.0", "(GMT +12:00) Auckland, Wellington, Fiji, Kamchatka"), 
)





class UserProfile(models.Model): 
	user = models.OneToOneField(User)  
	#other fields here
	timezone = models.CharField(max_length=5, choices=TIMEZONE_CHOICES)
	defaultPrivate = models.BooleanField(default=False, verbose_name="User is private")
	# October 17, 2014: this was originally for koncepts, but then used for Fragments
	defaultPrivateKoncepts = models.BooleanField(default=False, verbose_name="Snippets by default are private")

	def __str__(self):	
		  return "%s's profile" % self.user	 
		  
	def pretty_name(self):
		""" Helper methog to return the Full name if available, otherwise the username"""
		# print self.user.first_name
		if (self.user.first_name and self.user.first_name.strip()) or (self.user.last_name and self.user.last_name.strip()):
			temp = "%s %s" % (self.user.first_name, self.user.last_name)
			return temp.strip()
		else:
			return self.user.username
			
	@models.permalink
	def get_absolute_url(self):
		return 'person_public_profile', [self.user.username]
		

	def get_koncepts(self, onlypublic=True, count=False, ordering="created"):
		""" 
		Get all koncepts for a given user 
		eg: Koncept.objects.filter(created_by__username="mpasin").order_by("-created_at")
		
		June 28, 2014: Ordering can be 'recent' or 'popular'
		"""		
		mydict = {'created_by': self.user }
		if onlypublic:
			mydict['intfrag__isprivate'] = False
		
		if count:
			return Koncept.objects.filter(**mydict).distinct().count()
		else:
			if ordering == "popular":
				return Koncept.objects.filter(**mydict).distinct().annotate(x=Count('intfrag')).order_by('-x', '-updated_at')				
			elif ordering == "updated":  # fall back to 'recent'
				return Koncept.objects.filter(**mydict).distinct().order_by("-updated_at")			
			else:  # fall back to 'recent'
				return Koncept.objects.filter(**mydict).distinct().order_by("-created_at")


	def get_koncepts_public(self):
		""" Wrapper for get_koncepts so that it can be used in templates """
		return self.get_koncepts(onlypublic=True)
	def get_koncepts_public_recent(self):
		""" Wrapper for get_koncepts so that it can be used in templates """
		return self.get_koncepts(onlypublic=True)[:5]	
	def get_koncepts_private(self):
		""" Wrapper for get_koncepts so that it can be used in templates """
		return self.get_koncepts(onlypublic=False)		

	def get_documents(self, onlypublic=True, count=False, ordering="created"):
		""" 
		Get all Documents for a given user 
		"""		
		mydict = {'created_by': self.user }
		if onlypublic:
			mydict['fragment__isprivate'] = False

		if count:
			return Document.objects.filter(**mydict).distinct().count()
		else:
			if ordering == "popular":
				return Document.objects.filter(**mydict).annotate(x=Count('fragment__intfrag')).order_by('-x', "-updated_at")
			elif ordering == "updated": 
				return Document.objects.filter(**mydict).distinct().order_by("-updated_at")
			else:  # fall back to 'recent'
				return Document.objects.filter(**mydict).distinct().order_by("-created_at")


	def get_fragments(self, onlypublic=True, count=False, ordering="created"):
		""" 
		Get all Fragments for a given user 
		"""		
		mydict = {'created_by': self.user }
		if onlypublic:
			mydict['isprivate'] = False

		if count:
			return Fragment.objects.filter(**mydict).distinct().count()
		else:
			if ordering == "popular": # NOT USED
				return Fragment.objects.filter(**mydict).distinct().order_by("-updated_at")
			elif ordering == "updated":
				return Fragment.objects.filter(**mydict).distinct().order_by("-updated_at")
			else:  # fall back to 'recent'
				return Fragment.objects.filter(**mydict).distinct().order_by("-created_at")
	
	def get_fragments_private(self):
		""" Wrapper for get_fragments so that it can be used in templates """
		return self.get_fragments(onlypublic=False)
					

	def get_intfrags(self, onlypublic=True, count=False):
		""" 
		Get all IntFrags for a given user (note: not the Fragments themselves)
		"""		
		mydict = {'created_by': self.user }
		if onlypublic:
			mydict['isprivate'] = False

		if count:
			return IntFrag.objects.filter(**mydict).count()
		else:
			return IntFrag.objects.filter(**mydict).order_by("-created_at")
			

	def get_tags(self, onlypublic=False, count=False):
		""" 
		Get all Tags for a given user
		2015-02-15: updated 
		2015-03-17: updated
		2016-07-31: moved to Subject
		"""				
		return Tag.subjectsListPerUser(self.user, onlyPublic=onlypublic, totcount=count)

			
	def get_tags_cloud(self, onlypublic=False, limit=1):
		""" 
		Tag cloud data
		2015-03-17: updated - now this is just a wrapper on the Tag method
		2016-07-31: moved to Subject
		"""		
		
		return Tag.subjectsListPerUser(self.user, onlyPublic=onlypublic, count_fragments=True, count_limit=limit)

				
								


	# @models.permalink
	# def get_dashboard_url(self):
	#	return 'dashboard', [self.user.username]
		
def create_user_profile(sender, instance, created, **kwargs):  
	if created:	 
	   profile, created = UserProfile.objects.get_or_create(user=instance)	

post_save.connect(create_user_profile, sender=User) 

User.profile = property(lambda u: u.get_profile() )


# if you have preexisting users:
# >>> for u in User.objects.all():
# ...	  profile, created = UserProfile.objects.get_or_create(user=u)
# ... 


   
