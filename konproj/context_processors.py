##################
#  October 28, 2014
##################






import settings

from koncepts.importUtils import *

# # CONTEXT PROCESSORS: takes an HttpRequest object and returns a dictionary of variables to use in 
# # the template context. That's all it does!
# 
# # updates information about the recently searched/viewed objects 
# # 1. gets the data from session (each variable is a list of dicts containing the necessary info)
# # 2. updates the data based on info contained in 'request' object
# # 3. return the updated context that will be used in the templates
# 



def which_environment(request):
	return {
		'LOCAL_SERVER' : settings.LOCAL_SERVER, 
		'ADMIN_SERVER' : settings.ADMIN_SERVER, 
		'DEV_SERVER' : settings.DEV_SERVER, 
		'LIVE_SERVER': settings.LIVE_SERVER, 
		'TESTING_FEATURE_FLAG' : settings.TESTING_FEATURE_FLAG,
	}


def which_labels(request):
	return {
		'KONCEPT_LABEL' : "Collection", 
		'SUBJECT_LABEL' : "Tag", 
		'SNIPPET_LABEL' : "Quote", 
		'DOCUMENT_LABEL' : "Source", 
		'FOLDER_LABEL' : "Folder", 
		'TITLE_LABEL' : "Title", 
	}



def kindle_file_exists(request):
	if request.user and request.user.is_authenticated:
		if importFileExists(request.user.username, "kindle"):
			return {'previousKindleImport': True}
	return {'previousKindleImport': False}




# 
# 
# def add_session(request):
# 	record_history = request.session.get('record', None)
# 	memory = update_memory(request, record_history)
# 	if memory:
# 		request.session['record'] = memory[0]
# 		return {
# 				'record_history': memory[0] , 
# 				}
# 	else:
# 		return {
# 				'record_history': record_history , 
# 				}
# 
# 
# def update_memory(request, record_history):
# 	path = request.path
# 	if request.user and request.user.is_authenticated() and ..:
# 	
# 	#	RECORD PAGE
# 	if path.find('/db/record') >= 0:
# 		lista = path.split("/")
# 		try:
# 		# if True:
# 			number = int(lista[-2])	 # even though the number seems in last position, it's the penultimate
# 			rectype = lista[-3]
# 			try:
# 				if rectype == 'document':
# 					name = Document.objects.filter(id=number).values('title')[0]['title']
# 				elif rectype == 'event':
# 					name = Event.objects.filter(id=number).values('short_title')[0]['short_title']
# 				elif rectype == 'person':
# 					name = nicename(Person.objects.get(id=number)) 
# 				elif rectype == 'troupe':
# 					name = Troupe.objects.filter(id=number).values('name')[0]['name']
# 				elif rectype == 'venue':
# 					name = Venue.objects.filter(id=number).values('name')[0]['name']
# 				elif rectype == 'emlot-record':
# 					name = ""
# 			except:
# 				name = "[error retrieving name]"
# 			newdict = {'number' : number, 'type' : rectype, 'name' : name}
# 			if record_history:
# 				if newdict not in record_history:
# 					record_history.insert(0, newdict)
# 				if len(record_history) > 20:
# 					record_history.pop()
# 			else:
# 				record_history = [newdict]
# 		except:
# 			pass
# 		# printdebug("noise")
# 		# printdebug(record_history)
# 		return [ksearch_history, fsearch_history, record_history]			
# 	
# 	else:
# 		return None
# 		
# 		
		


