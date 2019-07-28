# ================
# LOCAL SETTINGS
# ================




DATABASES = {
	'default': {
		'NAME': '',
		'ENGINE': 'django.db.backends.mysql',
		'USER': '',
		'PASSWORD' : '' ,
		'HOST' : '127.0.0.1',
	}
}





# Make this unique and don't share it with anybody
SECRET_KEY = '----------------'


# set it if Apache is not handling python requests at the root level  
# PROD SERVER ==> "db/"
URL_PREFIX = ""







