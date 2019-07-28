"""
URL patterns for the views included in ``django.contrib.auth``.

Including these URLs (via the ``include()`` directive) will set up the
following patterns based at whatever URL prefix they are included
under:

* User login at ``login/``.

* User logout at ``logout/``.

* The two-step password change at ``password/change/`` and
  ``password/change/done/``.

* The four-step password reset at ``password/reset/``,
  ``password/reset/confirm/``, ``password/reset/complete/`` and
  ``password/reset/done/``.

The default registration backend already has an ``include()`` for
these URLs, so under the default setup it is not necessary to manually
include these views. Other backends may or may not include them;
consult a specific backend's documentation for details.

"""

from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views

from registration.forms import KonceptsAuthenticationForm # username or password is ok

# mikele: hacked login view so to use the <KonceptsAuthenticationForm> 
# mikele: extended on Nov 2 2012 so to include password reset templates too!

urlpatterns = patterns('',
                       url(r'^login/$',
                           auth_views.login,
                           {'template_name': 'bstrap3.2.0/registration/login.html', 
						    'authentication_form' : KonceptsAuthenticationForm},
                           name='auth_login'),
                       url(r'^logout/$',  # redirect straight to homepage
                           auth_views.logout, {'next_page': '/'} , name='auth_logout'),
						   
                       url(r'^password/change/$',
                           auth_views.password_change,
							{'template_name': 'bstrap3.2.0/registration/password_change_form.html'},
                           name='auth_password_change'),
                       url(r'^password/change/done/$',
                           auth_views.password_change_done,
						 	{'template_name': 'bstrap3.2.0/registration/password_change_done.html'},
                           name='auth_password_change_done'),
						   
                       url(r'^password/reset/$',
                           auth_views.password_reset,
							{'template_name': 'bstrap3.2.0/registration/password_reset_form.html'},
                           name='auth_password_reset'),
                       url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           auth_views.password_reset_confirm,
							{'template_name': 'bstrap3.2.0/registration/password_reset_confirm.html'},
                           name='auth_password_reset_confirm'),
                       url(r'^password/reset/complete/$',
                           auth_views.password_reset_complete,
							{'template_name': 'bstrap3.2.0/registration/password_reset_complete.html'},
                           name='auth_password_reset_complete'),
                       url(r'^password/reset/done/$',
                           auth_views.password_reset_done,
						    {'template_name': 'bstrap3.2.0/registration/password_reset_done.html'},
                           name='auth_password_reset_done'),
						   
	                    url(r'^$',
                           auth_views.login,
                           {'template_name': 'bstrap3.2.0/registration/login.html'},
	                        name='home_registration'),   
)
