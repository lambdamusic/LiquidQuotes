from django.conf.urls.defaults import *
from registration.views import register

from captcha_registration.forms import RecaptchaRegistrationForm

urlpatterns = patterns('',
    url(r'^register/$', register,
        {'backend':'registration.backends.default.DefaultBackend', 
		'form_class': RecaptchaRegistrationForm},
        name='registration.views.register'),
    (r'', include('registration.urls')),
)