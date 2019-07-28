
# Koncepts project


COMMITMENT LOGS
-----------------------------------------


March 26, 2014
- tried adding 'on this page' section to sidebar
- moved tabs to top


March 24, 2014
- added publicprivate_button.html and corner position of button
	- TEST: 2 approaches: in block quote and in source well.. which one?

March 21, 2014
- new draft of buttons/icons on concept detail
- document detail view
- boot box confirmations for delete operations
- added fake tab with + button for more fragments
**UPDATED STG DB**
**UPDATED STG SITE**
- added Koncept method cleanIntFragOrdering to models.py 
	- every time new intFrag is created, the filed should increment
	- when deleted, it should decrement etc....
- write script to add ordeno to all intfrag
	- added manager python manage.py dataclean 3
	@TODO: update live DB


March 20, 2014
- cleaned up get_koncept in koncept.py
- added ordeno field in DB to IntKon and IntFrag 
	- @todo: update STG DB with script : DONE
- added 'mykoncepts' template variable: if loggedIn&myPage
- refined concept detail page
	- added pencil for editing 
	- added templates for doc preview
	- fixed modal window and made dynamic
	- first draft at ordering buttons underneath fragment 
- fixed bug with document view	


March 19, 2014
- added get_koncepts_public to UserProfile
- added more keywords to forbidden usernames
- people page: cleaned up, add breadcrumbs
- people-specific page: hidden (using concepts wall for now)
- added user/wall and user/koncepts and user/documents 
- removed unnecessary links from dashboard menu 


March 16, 2014
- minor fixes to koncept detail page
- added ALL tab to koncept detail page
- changed breadcrumbs css
- added stub for pinterest-like user page
 

March 14, 2014
- updated the Related documents section
- added breadcrumbs
- added sticky behaviour for breadcrumbs
- added tabs navigation in concept detail
**UPDATED STG SITE**


March 11, 2014
- dbchecked all the new/edit routines
	- errors, fields missing etc..
- tested autocomplete_search.html
	- issue with matching names and 1-click actions
- refactored buttons_koncept.html, buttons_document.html
- eliminated Overwrite source globally behaviour
	- @todo: need to test more
- added recent concepts to addOnTheFly view/template
**UPDATED STG SITE**
**UPDATED ADMIN SITE**


March 10, 2014
- refined new concept form (errors, warnings using bstrap)
- added url/view for finding concepts by ID
- added validation for concept name (no numbers only!)
	- also in modal update
- edit koncept/interpretation action + template
- separated newDocumentForm from newKonceptForm 
- added mergeWithDocument method 
- added Document edit/merge operations
- refined 404, 500, 401 templates
- added 2 columns to document detail template
	- added tag to split list of intfrags
- added url handler for get_document_from_id
- add new Koncept from source action
	- fixed bug due to not using 'readonly' in form


March 9, 2014
- modified navbar a little
- added tip and fill-in to edit Koncept title modal
- fixed disabled state for input button on increaseKoncept operation


March 8, 2014
- addOnTheFly: added flag to make cancel button close window
- edit koncept title: added ajax modal edit form, for multiple interpretations
- added merge operation for concepts, models.py
- added new-fragment-from-Koncept form changes  
 
 
March 7, 2014
- tried out trello: https://trello.com/b/9lvEloVl/koncepts
- added js to make tabs open via mouse over
- added little 'edit' text to concept detail


March 4, 2014
- refined the addOnFly popup
- created partial template for koncept-new-form
- tested various popups via modal windows
**UPDATED STG SITE**

March 3, 2014
- added bootbox.js for concept name change
	- doesn't seem to work with typeahead!!! 

February 26, 2014
- created new add-koncept template
	- recent koncept/docs selection tool
- removed pagination widget from top of page
- moved tags model spec to models.py


February 21, 2014
- added global delete for sources
- added delete for orphan sources after deleting koncepts/interpretations
- BUG: I merged 'taxo' with 'taxonomy' and the deleted one fragment, but two of them got away!!!  
	- tried by could not reproduce

February 19, 2014
- duplicated koncept_detail_b4TEST.html, added a 2 cols layout

February 12, 2014
- tested breadcrumbs, alerts after delete

February 10, 2014
- added koncept-source-fragment model methods
- concept view pills refinement
- modal for reading fragment
**UPDATED STG SITE**

February 6, 2014
- documents pills for concept detail template and view
- delete behavior for fragments
- delete behavior for concepts
**UPDATED STG SITE**

January 31, 2014
- added search for both concept and source: @todo test
- added better layout for concept detail template
- added source x concept method in models
- added sources selector in concept detail

January 17, 2014
- fixed bug with created_by/updated_by
	- usually these were set via admin-save_model method
	- here we don't have admin, so they have to be set manually
		- at least, the created_by! 
- added uniqueness constraint on LIVE DB
- ran DataClean: found 2 docs with same title 'Ontology'
	- left as is for now...
**UPDATED STG DB**
**UPDATED STG SITE**
- tested new img for concept


January 14, 2014
- refined editing workflow
- updated buttons on document-detail view
- refactored new.py, extracted form processing code 
- refactored edit.py
- added new from template (concept or source)
- added make-private behaviour for concepts
**UPDATED STG SITE**



January 13, 2014
- added preview link after autocomplete for source&koncept
- made it work with addOnTheFly too
**UPDATED STG SITE**
- edit: added koncept/source info preview


January 11, 2014
- added autocomplete for all fields of a source in new koncept
	- sources fields can be modified too
	- added preview link when selection happens


December 11, 2013
- started refactoring new.py and related templates
- enforced uniqueness of koncept+user at DB level
- modified navBar links a little
- changed Koncept model



December 4, 2013
- played around with other strap css designs
- switched to using bootstrap-min.css (in local - not tested online)
	- PS: the carousel uses its own version of css!


December 2, 2013
- updated top nag bar and made dynamic
- added contact page +form
- added new images to carousel
- added static pages: about etc..


November 26, 2013
- added bookmarklet dynamically on tools page
- rewired the /import page into the /tools one


November 20, 2013
- revised admin loading workflow; added settings.ADMIN_SERVER
- activated a new admin app on web faction
	- http://dietrokoncepts.magicrebirth.webfactional.com/
	- admin visible but debug=False
- added people-detail and people-list views/templates
- added reserved keywords to Registration via settings.py
- rewired all URLs based on new design
- updated site
	- ran into too-many-files-open web faction error; TODO investigate
	- https://code.google.com/p/modwsgi/wiki/IntegrationWithDjango
	- http://community.webfaction.com/questions/4670/django-mod_wsgi-reduce-memory-usage



October 31, 2013
- added terms&conditions page
- added site-wide pages structure (about, help, toc, etc..)


October 30, 2013
- IDEA: check timeline css http://almende.github.io/chap-links-library/js/timeline/examples/example05_format_custom_html.html
- IDEA: graph http://almende.github.io/chap-links-library/js/network/examples/example14_multiline_text.html


October 30, 2013
- fixed bug in name/surname update via the form
- added timezone support
- completed registration/profile stuff
- updated live site


October 27, 2013
- added User Profiles as part of Registration app
- updated preexisting profiles via console:
# >>> for u in User.objects.all():
# ...     profile, created = UserProfile.objects.get_or_create(user=u)
# ... 


October 25, 2013
- started looking at password change from within application
	- fixed form and reused normal password change

October 11, 2013
started looking at privacy policy:
http://answers.onstartups.com/questions/15217/is-there-a-terms-of-service-tos-template-that-i-can-use-for-my-saas-product-p


October 9, 2013
- fixed password reset workflow/templates
- fixed bug with admin and crsf security

October 8, 2013
- started updating registration
	- added login via email 
	- fixed login/register templates
	- fixed password_reset_form.html


October 4, 2013
- added concepts timeline on dashboard
	- http://almende.github.io/chap-links-library/timeline.html
- added history view, interesting timelines
	- https://github.com/wnyc/Timeline
	- https://github.com/christian-fei/Timeline.css [one I'm using]
	- http://tympanus.net/Blueprints/VerticalTimeline/


September 23, 2013
- updated addonthefly and related view-calls


September 19, 2013
- fixed dashboard page
- added tag cloud
- added base colors for docs/tags
- fixed header/link to network view


September 9, 2013
- design for koncept page
- IDEA: add http://www.jquery4u.com/bootstraps/metro-bootstraps/ for network view?
- IDEA: popover for source? http://getbootstrap.com/2.3.2/javascript.html#popovers
- IDEA: add chat/email capability: https://www.zopim.com/pricing


August 15, 2013
- import functionality
- added edit/new for koncepts
- fixed query autocomplete with bootstrap
- added stars rating
	- Star Rating:
		- http://wbotelhos.com/raty/
	Bootstrap compatible:
		- http://fortawesome.github.io/Font-Awesome/get-started/
		- http://css-tricks.com/star-ratings/
- IDEA: Tags + bootstrap
	https://github.com/maxwells/bootstrap-tags
- document detail page
- tried to add bigger icons: http://marcoceppi.github.io/bootstrap-glyphicons/

August 14, 2013
- Tried adding other icons but they were messing up the other ones...
in base.html:
- continued cleaning up the concept detail page

August 12, 2013
- cleaned up a little the icons on koncept-detail page

August 1, 2013
- started documents list view
- added koncept network view

July 31, 2013
- started building koncept-detail view
- added stub pages for inbox comments etc...
- added dashboard menu links-active routine
- added search on top bar
- reformatted pagination routines

July 28, 2013
- worked on log in using bootstrap
- fixed basic version of log in (registration NOT supported yet)
- added dashboard view
- 

2013-07-17
- added images to carousel page
- tried a few themes from bootswatch: 
	- good: spacelab | simplex | default_css |

2013-05-21
- added test view with bootstrap: a) fixed navbar and b) homepage carousel

2013-05-16
Fixed bug in creating koncepts cloud (size didn't reflect public/private koncepts)


===========
old commits (koncepts1)
===========


2013-05-13
-----------------------------------------
- completed import functionality
	- added source text + tags
	- added autocompletes (source, tags, etc... )
	- checked backend functions
	- added support for intermediary transformation into standard dict
- fixed add on the fly template
- fixed redirect error in delete.py


2013-05-12
-----------------------------------------
- refined and rationalized the import view 


2013-05-08
-----------------------------------------
- updated from live DB and updated live site
- fine-tuned the querying and display of private vs public stuff on koncepts list
- added separate template for koncepts_cloud
- Added /home url handler and <action="?next={{ next|default:"/home" }}"> to login.html template


2013-05-07
-----------------------------------------
- changed varchar url in Documents: up to 300 chars now (also in sql)
- fixed title-generation tag


2013-05-06
-----------------------------------------
- added d3 network view
- Removed Quick Links from footer - realigned divs
- moved cloud view to koncepts list, made it paginatable


2013-05-01
-----------------------------------------
- added templates for inheritance in dashboard modules
- added dashboard
- moved registration templates in apps


2013-04-29
-----------------------------------------
- added userpage_and_authenticated templatetag: portions of koncept_detail template are loaded selectively
- added menubar_getclass templatetag, dynamic 'active' tag for menubar
- added menutop bar / separated out template component for didyouknowthat


2013-04-28
-----------------------------------------
- extended get-koncept view so that it caters for public/private etc..
- added title-generation tag for koncepts list
- added search behaviour for public/private views
- pluralized all top levels url names
- added search under /koncepts/ and users/../koncepts/


2013-04-28
-----------------------------------------
- changed ispublic into isprivate
- added koncept_metadata.html component
- added tagcloud sizing to source-page summary
- defined *makeAllPrivateForUser* class method on abstract koncept class
- integrated registration templates with main css styling (base.html)
- tested admin; added filters for 'created_by' and 'isprivate'
- modified urls for /koncept/source/tag/ so that the user is considered too
- added beta ribbon via http://www.quickribbon.com/
- added email server on webfaction and set it up on settings.py




2013-3-24
-----------------------------------------
- fixed bug when editing/duplicating existing koncepts
- added mechanism to update document across koncepts in koncept edit view
- added simple data cleansing mechanisms
	- removed some document duplicates



2013-3-26
-----------------------------------------
- finished integration of new look&feel
	- added views for new/edit
- refactoring of old code
- started building a view to import kindle data
	-integrated kindle file parsing lib
	-added checkboxes to decide what to import..
	- refined UI
- built command for importing old data into new models
	- imported stuff in local DB



2012-12-16
-----------------------------------------
- refined models 
- added KonceptEnhancedModel (+ ispublic)
- started working on importing old data into new models



2012-4-16
-----------------------------------------
- temp disabled the 'dynamic_header_size'
- changed some sizes on the change-term page
- created new app with new models
	- Terms => Koncept
	- Source => Fragment
	- Interpretation => InterpretatKoncept and InterpFragment
	- Project etc..


2012-03-17
-----------------------------------------
- added a separate css for the homepage
- added recent koncepts to homepage
- moved around templates positions a bit
- css: changed size of terms list
- upgraded to staticfiles


2012-01-23
-----------------------------------------
- added autocomplete
- add pagination on terms/sources/contexts views
- added the captcha application
- added email registration support



2012-01-05
-----------------------------------------
- added the add-on-the-fly functionality with popup
- Concepts: in source view, show authors and urls...
- when deleting interpretations: added confirmation screen
- created a subdomain on magicrebirth-webfact.... and moved the app there
	- keep the installation on /demos without users, for display purposes!
- Concepts: refined the look&feel of the list of terms of the homepage..


2011-12-31
-----------------------------------------
- concepts: terms/sources/contexts add ordering
	- by modified date / creation date / alpha
- the contexts used as options in a form should be only the ones created by that user!
	- added an __init__ method to the Interpretation form
- on the terms/sources pages the blue box can just contain stats relevant to this view!	
- got a short list of languages, and preload them with the application
- concepts: add location on title page
- added user management
	- works with all modes of operation
	- for the moment, users can see only their own stuff!
- add the ability of adding more tags with commas!
- put terms names in capital letters
- add an 'add new interpretation' at the bottom of term-detail view
	- Also, make term name RED and bigger...
- move the actionlinks in the bar
	- eg in the  Term page the Add new interpretation for this Term	  Delete term  Edit term links should be better positioned; ideally inside the bar at the top! similar for sources etc..
	So we'll make a separation actions specfiic to the page main topic, and the other ones...
- the 'add new' link could be always at the top left
	- it's useful in all situations

2011-12-27
-----------------------------------------
* set up the basic project structure
* copy over concepts from 'demos_web'
* added the b_project structure


