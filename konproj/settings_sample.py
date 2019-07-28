""" 
Based on B_project settings.

originally coded by michele pasin on 2011-10-11
++++
A ``local_settings`` module must be made available to define sensitive
and highly installation-specific settings.

"""

VERSION = 2.0



import os
import sys
import django
from time import strftime


# the site root is one level up from where settings.py is
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__)).rsplit('/', 1)[0]

sys.path.append(os.path.join(SITE_ROOT, "konproj/apps"))
sys.path.append(os.path.join(SITE_ROOT, "konproj/libs"))


ADMINS = (
	('you', 'you@mail.com'),
)
MANAGERS = ADMINS 

TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True




if "/local/code/" in SITE_ROOT:
	LOCAL_SERVER, ADMIN_SERVER, DEV_SERVER, LIVE_SERVER = True, False, False, False
elif "/koncepts_admin" in SITE_ROOT:
	LOCAL_SERVER, ADMIN_SERVER,  DEV_SERVER,  LIVE_SERVER = False, True, False, False
elif "/devkoncepts2" in SITE_ROOT:
	LOCAL_SERVER, ADMIN_SERVER,  DEV_SERVER,  LIVE_SERVER = False, False, True, False
else:
	LOCAL_SERVER, ADMIN_SERVER,  DEV_SERVER,  LIVE_SERVER = False, False, False, True

if not (LOCAL_SERVER or ADMIN_SERVER or DEV_SERVER or LIVE_SERVER):
	raise Exception("Could not determine which location you're in! \nLOCAL_SERVER or LIVE_SERVER?")



if LOCAL_SERVER:
	DEBUG = True
	TEMPLATE_DEBUG = DEBUG
	TESTING_FEATURE_FLAG = True
	MEDIA_URL = '/media/upload/'
	STATIC_URL = '/media/static/'
	ADMIN_MEDIA_PREFIX = '/media/static/admin/'
	MPTTEXTRA_ADMIN_MEDIA = '/media/static/legacy/feincms'
	SUBPATH = ""
	BOOTSTRAP = "bstrap3.2.0/"  # "bstrap3.2.0/" or  "bstrap2.3.2/"
	MEDIA_ROOT = os.path.join(SITE_ROOT, 'upload')
	STATICFILES_DIRS = (
	   os.path.join(SITE_ROOT, 'konproj/static'),
	)
	# path used with "python manage.py collectstatic"
	STATIC_ROOT = os.path.join(SITE_ROOT, 'apache/static')

elif ADMIN_SERVER:
	DEBUG = False
	TEMPLATE_DEBUG = DEBUG
	TESTING_FEATURE_FLAG = False
	BOOTSTRAP = "bstrap3.2.0/"
	MEDIA_URL = 'http://www.liquidquotes.com/upload/koncepts2/'
	STATIC_URL = 'http://www.liquidquotes.com/media/koncepts2/'
	ADMIN_MEDIA_PREFIX = 'http://www.liquidquotes.com/media/koncepts2/admin/'
	MPTTEXTRA_ADMIN_MEDIA = 'http://www.liquidquotes.com/media/koncepts2/legacy/feincms'
			
	MEDIA_ROOT = '/home/webapps/upload/'
	STATICFILES_DIRS = (
	   os.path.join(SITE_ROOT, 'konproj/static'),
	)	
elif DEV_SERVER: 
	DEBUG = True
	TEMPLATE_DEBUG = DEBUG
	TESTING_FEATURE_FLAG = True
	BOOTSTRAP = "bstrap3.2.0/"
	MEDIA_URL = 'http://dev.liquidquotes.com/upload/koncepts2/'
	STATIC_URL = 'http://dev.liquidquotes.com/media/koncepts2/'
	ADMIN_MEDIA_PREFIX = 'http://dev.liquidquotes.com/media/koncepts2/admin/'
	MPTTEXTRA_ADMIN_MEDIA = 'http://dev.liquidquotes.com/media/koncepts2/legacy/feincms'
			
	MEDIA_ROOT = '/home/webapps/upload/'
	STATICFILES_DIRS = (
	   os.path.join(SITE_ROOT, 'konproj/static'),
	)		
else:
	DEBUG = False
	TEMPLATE_DEBUG = DEBUG
	TESTING_FEATURE_FLAG = False
	BOOTSTRAP = "bstrap3.2.0/"
	MEDIA_URL = 'http://www.liquidquotes.com/upload/koncepts2/'
	STATIC_URL = 'http://www.liquidquotes.com/media/koncepts2/'
	ADMIN_MEDIA_PREFIX = 'http://www.liquidquotes.com/media/koncepts2/admin/'
	MPTTEXTRA_ADMIN_MEDIA = 'http://www.liquidquotes.com/media/koncepts2/legacy/feincms'
			
	MEDIA_ROOT = '/home/webapps/upload/'
	STATICFILES_DIRS = (
	   os.path.join(SITE_ROOT, 'konproj/static'),
	)
	





TEMPLATE_DIRS = (
	os.path.join(SITE_ROOT, 'konproj/templates-global'),
	os.path.join(SITE_ROOT, 'konproj/apps/koncepts/templatetags'),
)



# 
# # settings for FEINCMS media used by the admin-mptt tree visualizer...
# MPTTEXTRA_ADMIN_MEDIA = '/dj_app_media/legacy/feincms'
# 



TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media" , 
	'django.contrib.messages.context_processors.messages',
	"django.core.context_processors.request", 
	"django.core.context_processors.static", 
	"context_processors.which_environment",
	"context_processors.which_labels",
	"context_processors.kindle_file_exists",
)

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader'
)


MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.middleware.csrf.CsrfResponseMiddleware',
)






ROOT_URLCONF = 'konproj.urls'


# October 27, 2013
AUTH_PROFILE_MODULE = 'registration.UserProfile'



INSTALLED_APPS = (	
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.humanize',
	'django.contrib.messages',
	
	'django.contrib.databrowse' , 
	'django.contrib.staticfiles',
	 	
	# 'mptt',	 
	# 'picklefield',
	'django_extensions',	
	# 'concepts',   # old version
	'koncepts',   # the wonderful app you're going to develop

	'registration',
	'django.contrib.admin',  #2013-07-28: moved here to avoid conflict with password reset templates
	

)






try:
	if LOCAL_SERVER:
		from local_settings import *
	elif DEV_SERVER:
		from local_devsettings import *
	else:
		from local_livesettings import *
except ImportError:
	pass






# 
# simple function that appends a debug string to another string (or file)
# 
def printdebug(stringa):
	""" helper function: print to the command line output only if not running WSGI (othersiwe it'd cause an error)
	......(wish we had MACROs!) """
	if stringa == 'noise':
		stringa = "\n%s\n" % ("*&*^" * 100)
	if LOCAL_SERVER:
		print ">>[%s]debug>>: %s"  % (strftime("%Y-%m-%d %H:%M:%S"), stringa)





# ********
# RESERVED KEYWORDS
# ********


# these can't be used for usernames!
REGISTRATION_RESERVED = ['site', 'people', 'actions', 'browse', 'registration', 'admin', 'projects', 'help', 'you', 'kommon', 'common', 'static', 'media', 'tour', 'users', 'ideas', 'topics', 'documents', 'concepts', 'api']				



LOGIN_URL = "/registration/login/"



RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''



ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: "/people/%s/" % u.username,
}







# eMail Settings

ACCOUNT_ACTIVATION_DAYS = 3
if LOCAL_SERVER:
	# # ---- python -m smtpd -n -c DebuggingServer localhost:1025
	# EMAIL_HOST = 'localhost'
	# EMAIL_PORT = 1025
	# EMAIL_HOST_USER = ''
	# EMAIL_HOST_PASSWORD = ''
	# EMAIL_USE_TLS = False
	# DEFAULT_FROM_EMAIL = 'admin@LiquidQuotes.com'
	# SERVER_EMAIL = 'admin@LiquidQuotes.com'

	EMAIL_HOST = ''
	EMAIL_HOST_USER = ''
	EMAIL_HOST_PASSWORD = ''
	DEFAULT_FROM_EMAIL = 'admin@LiquidQuotes.com'
	SERVER_EMAIL = 'admin@LiquidQuotes.com'
	EMAIL_PORT = "587"
	EMAIL_USE_TLS = True


else:		
	
	EMAIL_HOST = 'smtp.com'
	EMAIL_HOST_USER = ''
	EMAIL_HOST_PASSWORD = ''
	DEFAULT_FROM_EMAIL = 'admin@LiquidQuotes.com'
	SERVER_EMAIL = 'admin@LiquidQuotes.com'
	EMAIL_PORT = "587"
	EMAIL_USE_TLS = True


