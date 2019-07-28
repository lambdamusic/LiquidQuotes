
# bootstrap home test
# urlpatterns += patterns('koncepts.views',
#	url(r'^bootstrap/test$', 'bootstraptest', name='bootstraptest'),
#	)
# 


# Tip:
	# [^/]+ ==> match anything except / 
	# .*  ==> matches everything..




from django.conf.urls.defaults import *
from django.views.generic import RedirectView

from context_processors import which_labels
KONCEPT_LABEL = which_labels(None)['KONCEPT_LABEL'].lower() + "s"
SUBJECT_LABEL = which_labels(None)['SUBJECT_LABEL'].lower() + "s"
DOCUMENT_LABEL = which_labels(None)['DOCUMENT_LABEL'].lower() + "s"
SNIPPET_LABEL = which_labels(None)['SNIPPET_LABEL'].lower() + "s"
FOLDER_LABEL = which_labels(None)['FOLDER_LABEL'].lower()




urlpatterns = patterns('koncepts.views',
	url(r'^$', 'homepage', name='homepage'),
	)



# "/test/" pattern

urlpatterns += patterns('koncepts.test',
	url(r'^test/visjs$', 'test_visjs', name='test_visjs'),
	url(r'^test/jit$', 'test_jit', name='test_jit'),
	
	url(r'^test/konlist$', 'konlist', name='konlist'),
	url(r'^test/konlist-table$', 'konlist_table', name='konlist_table'),

	url(r'^test/taglist$', 'taglist', name='taglist'),

	url(r'^test/konlist-tree$', 'konlist_tree', name='konlist_tree'),
	url(r'^test/ajax_konlist_tree$', 'ajax_konlist_tree', name='ajax_konlist_tree_test'),
	url(r'^test/ajax_konlist_create$', 'ajax_konlist_create', name='ajax_konlist_create_test'),
	url(r'^test/ajax_konlist_delete$', 'ajax_konlist_delete', name='ajax_konlist_delete_test'),
	url(r'^test/ajax_konlist_move$', 'ajax_konlist_move', name='ajax_konlist_move_test'),

	url(r'^test/quotelist-table$', 'quotelist_table', name='quotelist_table'),
	url(r'^test/doclist$', 'doclist', name='doclist'),
	url(r'^test/tilesdocs$', 'tilesdocs', name='tilesdocs'),
	url(r'^test/masonry$', 'masonry', name='masonry'),
	
	url(r'^test/summernote$', 'summernote', name='summernote'),
	url(r'^test/blockquote$', 'blockquote', name='blockquote'),
	
	url(r'^test/sourcesummary$', 'sourceSummary', name='sourceSummary'),

	)




# "/site/" pattern

urlpatterns += patterns('',

	url(r'^site/toc$', 'koncepts.views.dispatcher', name='toc'),
	url(r'^site/faq$', 'koncepts.views.dispatcher', name='faq'),
	url(r'^site/about$', 'koncepts.views.dispatcher', name='about'),
	url(r'^site/help$', 'koncepts.views.dispatcher', name='help'),
	url(r'^site/contact$', 'koncepts.contact.contactSendEmail', name='doContact'), #ajax
	url(r'^site/$', RedirectView.as_view(url='/')),
	 
	)



# "/people/" pattern

urlpatterns += patterns('koncepts.people',
	 #2014-03-19: hidden it!
	# url(r'^people/(?P<username>\w+)/$', 'people_profile', name='people_profile'),
	url(r'^people/(?P<username>\w+)/$', RedirectView.as_view(url='/%(username)s')),
	url(r'^people/$', 'people_list', name='browse_people' ),
	 
	)




	
# "/pinco/" pattern	(aka the user) :: NEEDS TO BE LAST FOR URL MATCHING REASONS

urlpatterns += patterns('',

	url(r'^(?P<username>\w+)/dashboard/$', 'koncepts.people.person_dashboard', name='person_dashboard'), 
	url(r'^(?P<username>\w+)/public/$', 'koncepts.people.person_public_page', name='person_public_page'),
	url(r'^(?P<username>\w+)/inbox/$', 'koncepts.profile.inbox', name='inbox'),
	url(r'^(?P<username>\w+)/comments/$', 'koncepts.profile.comments', name='comments'),
	url(r'^(?P<username>\w+)/profile/$', 'koncepts.profile.profile', name='profile'),
	url(r'^(?P<username>\w+)/settings/$', 'koncepts.profile.settings', name='settings'),



	# QUOTES
	
	url(r'^(?P<username>\w+)/' + SNIPPET_LABEL + '/$', 'koncepts.search.search_quotes', name='search_user_quotes'), 
	url(r'^(?P<username>\w+)/' + SNIPPET_LABEL + '/(?P<quote_id>\d+)$', 'koncepts.quote.get_quote', name='get_quote'),	
	url(r'^(?P<username>\w+)/' + SNIPPET_LABEL + '/favorites/$', 'koncepts.search.search_quotes', {'favorites' : True} ,  name='search_user_favorites'), 
	url(r'^(?P<username>\w+)/' + SNIPPET_LABEL + '/clipboard/$', 'koncepts.search.search_quotes', {'clipboard' : True},  name='search_user_clipboard'), 
	


	# SUBJECTS
	
	url(r'^(?P<username>\w+)/' + SUBJECT_LABEL + '-detail/$', 'koncepts.subject.subject_detail', name='subject_detail'), 	
	url(r'^(?P<username>\w+)/' + SUBJECT_LABEL + '-list/$', 'koncepts.subject.subject_list', name='subject_list'), 	
	#  tree stuff
	url(r'^(?P<username>\w+)/' + SUBJECT_LABEL + '-tree/$', 'koncepts.subject.subject_tree', name='subjects_tree'), 	
	url(r'^(?P<username>\w+)/' + SUBJECT_LABEL + '-tree/ajax_subject_tree$', 'koncepts.subject.ajax_subject_tree', name='ajax_subjects_tree'),
	url(r'^(?P<username>\w+)/' + SUBJECT_LABEL + '-tree/ajax_subject_create$', 'koncepts.subject.ajax_subject_create', name='ajax_subjects_create'),
	url(r'^(?P<username>\w+)/' + SUBJECT_LABEL + '-tree/ajax_subject_delete$', 'koncepts.subject.ajax_subject_delete', name='ajax_subjects_delete'),
	url(r'^(?P<username>\w+)/' + SUBJECT_LABEL + '-tree/ajax_subject_move$', 'koncepts.subject.ajax_subject_move', name='ajax_subjects_move'),
	
	url(r'^(?P<username>\w+)/' + SUBJECT_LABEL + '/$', 'koncepts.subject.search_subject', name='search_user_subjects'), 
	
	
	# KONCEPTS -- disabled for now
	
	url(r'^(?P<username>\w+)/' + KONCEPT_LABEL + '/$', 'koncepts.search.search_koncept', name='search_user_koncepts'), 
	url(r'^(?P<username>\w+)/' + KONCEPT_LABEL + '/(?P<koncept_name>[^/]+)$', 'koncepts.koncept.get_koncept', name='get_koncept'),	



	# DOCUMENTS
	
	url(r'^(?P<username>\w+)/' + DOCUMENT_LABEL + '/$', 'koncepts.search.search_document', name='search_user_documents'), 
	url(r'^(?P<username>\w+)/' + DOCUMENT_LABEL + '/(?P<source_name>[^/]+)$', 'koncepts.document.get_document', name='get_document'),
	
		
	# FINALLY: 
	
	url(r'^(?P<username>\w+)/$', 'koncepts.views.person_home', name='person_home'),
	
	)



	# url(r'^(?P<username>\w+)/$', RedirectView.as_view(url='/')),








# "/actions/" pattern

urlpatterns += patterns('',

	# NEW & EDIT (note: users alway need to be logged in)
	url(r'^actions/new/quote/$', 'koncepts.new.new_quote', name='create_quote'),
	url(r'^actions/edit/quotetitle/$', 'koncepts.edit.edit_quote_title', name='edit_quote_title'),
	url(r'^actions/edit/quotesubjects/$', 'koncepts.edit.edit_quote_subjects', name='edit_quote_subjects'),
		
	url(r'^actions/new/addonthefly/$', 'koncepts.new.addonthefly', name='addonthefly'),
	url(r'^actions/edit/changeQuoteKoncept/', 'koncepts.edit.changeQuoteKoncept', name='changeQuoteKoncept'),  #ajax

	url(r'^actions/new/project/', 'koncepts.project.addProject', name='addProject'),  #ajax
	url(r'^actions/edit/project/', 'koncepts.project.editProject', name='editProject'),  #ajax

	url(r'^actions/edit/konceptdetails/(?P<kon_id>\d+)', 'koncepts.edit.edit_koncept_details', name='edit_koncept_details'),	 
	url(r'^actions/edit/konceptquoteorder/(?P<kon_id>\d+)', 'koncepts.edit.edit_koncept_quotes_order', name='edit_koncept_quotes_order'),	 
	url(r'^actions/edit/koncept/changeprivacy/$', 'koncepts.edit.make_fragment_private', name='make_fragment_private'),	#ID passed via GET/ajax 

	url(r'^actions/edit/quote/changeclipboard/$', 'koncepts.edit.make_fragment_clipboard', name='make_fragment_clipboard'),	#ID passed via GET/ajax 
	url(r'^actions/edit/quote/changefavorite/$', 'koncepts.edit.make_fragment_favorite', name='make_fragment_favorite'),	#ID passed via GET/ajax 	

	
	url(r'^actions/edit/document/(?P<doc_id>\d+)', 'koncepts.edit.edit_document', name='edit_document'), 
	url(r'^actions/edit/sourcequoteorder/(?P<doc_id>\d+)', 'koncepts.edit.edit_source_quotes_order', name='edit_source_quotes_order'),


	url(r'^actions/addkoncept/project/$', 'koncepts.project.addKoncept2Project', name='addkoncept_project'),   # ajax
	

	# DELETE objects urls :: user always need to be loggen in

	url(r'^actions/unlink/fragment/', 'koncepts.delete.unlink_fragment', name='unlink_fragment'),	
	url(r'^actions/delete/fragment/', 'koncepts.delete.delete_fragment', name='delete_fragment'),  
	url(r'^actions/delete/koncept/', 'koncepts.delete.delete_koncept', name='delete_koncept'),  
	url(r'^actions/delete/document/', 'koncepts.delete.delete_document', name='delete_document'),	  # temp wiring
	url(r'^actions/delete/project/', 'koncepts.project.deleteProject', name='deleteProject'),	# ajax


	# IMPORT patterns

	url(r'^actions/import/kindle$', 'koncepts.importKindle.importkindle', name='importkindle'),
	url(r'^actions/import/kindle/latest$', 'koncepts.importKindle.getLatestKindleImport', name='getLatestKindleImport'),

	# url(r'^actions/import/plaintext$', 'koncepts.importText.importtext', name='importtext'),

	url(r'^actions/import/selectdocument$', 'koncepts.importKindle.previewDocumentImport', name='previewDocumentImport'),	
	url(r'^actions/import/doimport$', 'koncepts.importKindle.do_import', name='do_import'),		
	
	# TOOLS temp here
	url(r'^tools/bookmarklet$', 'koncepts.tools.bookmarklet', name='bookmarklet'),
	
	# fallback redirects
	url(r'^actions/import/$', RedirectView.as_view(url='/')),
	url(r'^tools/$', RedirectView.as_view(url='/')),
	
	
	)




# "/autocomplete/" pattern  [maybe move into actions?]

urlpatterns += patterns('koncepts.autocomplete',

	url(r'^autocomplete/koncepts/$', 'autocomplete_koncepts', name='autocomplete_koncepts'),
	url(r'^autocomplete/documents/$', 'autocomplete_sources', name='autocomplete_sources'),
	url(r'^autocomplete/source_details/$', 'autocomplete_source_details', name='autocomplete_source_details'),
	url(r'^autocomplete/koncept_details/$', 'autocomplete_koncept_details', name='autocomplete_koncept_details'),
	url(r'^autocomplete/tags/$', 'autocomplete_tags', name='autocomplete_tags'),

	)








# "/browse/" pattern 2015-03-10: used?

urlpatterns += patterns('',

	url(r'^browse$', 'koncepts.koncept.get_random_koncept', name='get_random_koncept'),	   #TODO: construct
	url(r'^browse/koncepts$', 'koncepts.koncept.get_random_koncept', name='browse_koncepts'),	
	url(r'^browse/documents$', 'koncepts.koncept.get_random_koncept', name='browse_sources'),	
	url(r'^browse/projects$', 'koncepts.koncept.get_random_koncept', name='browse_projects'),	

	url(r'^browse/random$', 'koncepts.koncept.get_random_koncept', name='get_random_koncept'),	
	
	url(r'^browse/random/quote$', 'koncepts.quote.get_random_quote', name='get_random_quote'),
	 
	)
	






	
# "/api/" pattern	

urlpatterns += patterns('',

	# SEARCH eg for chrome widgets etc..

	url(r'^api/search/$', 'koncepts.api.apisearch', name='apisearch'),
	
	# EXPORT
	
	url(r'^api/export/csv$', 'koncepts.exportCSV.export_csv', name='export_csv'),
	url(r'^api/export/word$', 'koncepts.exportWord.export_word', name='export_word'),
	# url(r'^api/export/rtf$', 'koncepts.exportRTF.export_rtf', name='export_rtf'),
	url(r'^api/export/txt$', 'koncepts.exportTXT.export_txt', name='export_txt'),
	# url(r'^api/export/pdf$', 'koncepts.export.export_pdf', name='export_pdf'),
	
	)

















	
	



# "/tools/" pattern
#
# urlpatterns += patterns('',
#
# 	url(r'^tools/bookmarklet$', 'koncepts.tools.bookmarklet', name='bookmarklet'),
#
# 	url(r'^tools/import/plaintext$', 'koncepts.importKindle.importtext', name='importtext'),
# 	url(r'^tools/import/kindle$', 'koncepts.importKindle.importkindle', name='importkindle'),
# 	# url(r'^tools/import/kindle/process$', 'koncepts.importKindle.importkindle', name='importkindle_process'),
# 	url(r'^tools/import/selectdocument$', 'koncepts.importKindle.previewDocumentImport', name='previewDocumentImport'),
# 	url(r'^tools/import/doimport$', 'koncepts.importKindle.do_import', name='do_import'),
#
# 	url(r'^tools$', RedirectView.as_view(url='/tools/import/plaintext')),
# 	url(r'^tools/import$', RedirectView.as_view(url='/tools/import/plaintext')),
#
# 	)
#
#






