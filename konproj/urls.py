from django.conf.urls.defaults import *
from django.conf import settings
prefix = settings.URL_PREFIX

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView

urlpatterns = patterns('',)	 # init


#  November 20, 2013
# 
# We have three server types for now:
# 
# 1) admin: shows only the admin, and live database (for stats)
# 
# 2) local: shows everything, local database
# 
# 3) live: shows only the site, and live database
# 
# 


if settings.ADMIN_SERVER:
	
	# online admin: no other controllers are defined
	
	from django.contrib import admin
	admin.autodiscover()	
	urlpatterns += patterns('', 
		# standard admin urls	
		(r'^', include(admin.site.urls) ),	
		# April 8, 2014: hack to prevent 404 and 500 pages from throwing errors
		url(r'^homepage$', RedirectView.as_view(url='/'), name='homepage'),	 
		url(r'^contact$', RedirectView.as_view(url='/'), name='contact'),	 
		)

else:

	
	
	if settings.LOCAL_SERVER: 
		
		# load admin on LOCAL too, but on a sub-url path
		
		from django.contrib import admin
		admin.autodiscover()
		# from myutils.adminextra import custom_admin_views
		# from concepts.databrowse_load import *

		urlpatterns += patterns('', 
			# Customized views for the application admin home					   
			# (r'^'+prefix+'admin/(concepts/)$', custom_admin_views.concepts), 
			# (r'^'+prefix+'admin/contributions/$', poms_custom_admin_views.contributions),
		
			# standard admin urls		 
			(r'^'+prefix+'admin/', include(admin.site.urls) ),			 
			# url(r'^'+prefix+'databrowse/(.*)', databrowse.site.root, name='databrowsehome'),

			)



	# standard urls for LOCAL & LIVE
	
	urlpatterns += patterns('',

		# Registration app
	
		(r'^registration/', include('registration.backends.default.urls')),					
		
		# Koncepts app
	
		url(r'^', include('koncepts.urls')),
	
	)




if settings.LOCAL_SERVER:	 # ===> static files on local machine
	urlpatterns += staticfiles_urlpatterns()	
	urlpatterns += patterns('', 
		(r'^media/uploads/(?P<path>.*)$', 'django.views.static.serve', 
			{'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
		)
		



