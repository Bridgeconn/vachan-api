from fastapi import FastAPI, Query, Path, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
from typing import Optional, List
from enum import Enum
import logging, csv, urllib, os


app = FastAPI()

class NormalResponse(BaseModel):
	message : str

class VachanApiException(Exception):
    def __init__(self, name: str, detail: str, status_code: int):
        self.name = name
        self.detail = detail
        self.status_code = status_code

@app.exception_handler(VachanApiException)
async def vachanapi_exception_handler(request: Request, exc: VachanApiException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"{exc.name} : {exc.detail}"},
    )


@app.get('/', response_model=NormalResponse, status_code=200)
def test():
	'''tests if app is running and the DB connection'''
	# connection = get_db()
	return {"message": "App is up and running"}



##### Content types #####
class ContentType(BaseModel):
	contentId : int
	contentType : str

@app.get('/v2/contents', response_model=List[ContentType], status_code=200)
def get_contents():
	'''fetches all the contents types supported and their details '''
	result = []
	return result   

@app.post('/v2/contents', response_model=NormalResponse, status_code=201)
def add_contents(content_name: str  = Body(...)):
	''' Creates a new content type. 
	Additional operations required: 
		1. Add corresponding table creation functions to Database.
		2. Define input, output resources and all required APIs to handle this content'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {'message': "Content type %s created successfully."%content_name }

## Notes ####
# PUT and DELETE methods are not defined for this resource

# DB changes needed with this:
#	1. if there is a password column in this table, move that to the metadata column of 
#	 sources or versions table which ever is appropriate to the content in question
#################

##### languages #####
langCodePattern =constr(regex="^\w\w\w$")
class Direction(str, Enum):
	right_to_left = 'right-to-left'
	left_to_right = 'left-to-right'

class Language(BaseModel):
	language : str 
	code : langCodePattern 
	localScriptName : str = None
	script : str = None
	scriptDirection : Direction = None

class LanguageEdit (BaseModel):
	languageId: int
	language : str = None
	code : langCodePattern = None
	localScriptName : str = None
	script : str = None
	scriptDirection : Direction = None	

@app.get('/v2/languages', response_model=List[Language], status_code=200)
def get_language(language_code : langCodePattern = None):
		'''fetches all the languages supported in the DB, their code and other details.
		if query parameter, langauge_code is provided, returns details of that language if pressent
		and 404, if not found'''
		result = []	
		try:
			pass
		except Exception as e:
			raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
		return result

@app.post('/v2/languages', response_model=NormalResponse, status_code=201)
def add_language(lang_obj : Language = Body(...)):
	''' Create a new language'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Language {lang_obj.language} created successfully"}

@app.put('/v2/languages', response_model=NormalResponse, status_code=201)
def edit_language(lang_obj: LanguageEdit = Body(...)):
	''' Changes one or more fields of language'''
	logging.info(lang_obj)
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message" : f"Updated language field(s)"}

## NOTE
# DELETE method not implemeneted for this resource
# ################################


##### Version #####

versionPattern = constr(regex="^[A-Z]+$")
class Version(BaseModel):
	versionAbbreviation : versionPattern
	versionName : str
	revision : str = "1"
	metadata : dict = None

class VersionEdit(BaseModel):
	versionId: int
	versionAbbreviation : versionPattern = None
	versionName : str = None
	revision : str = None
	metadata : dict = None


@app.get("/v2/versions", response_model=List[Version], status_code=200)
def get_version(version_abbr : versionPattern = None):
	'''Fetches all versions and their details.
	If param version_abbr is present, returns details of that version if pressent
	and 404, if not found'''
	result = []	
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	return result

@app.post('/v2/versions', response_model=NormalResponse, status_code=201)
def add_version(version_obj : Version = Body(...)):
	''' Create a new language'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Version {version_obj.versionAbbreviation} created successfully"}

@app.put('/v2/versions', response_model=NormalResponse, status_code=201)
def edit_version(version_obj: VersionEdit = Body(...)):
	''' Changes one or more fields of language'''
	logging.info(version_obj)
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message" : f"Updated version field(s)"}

## NOTE
# DELETE method not implemeneted for this resource
# ################################


##### Source #####
tableNamePattern = constr(regex="^\w\w\w_[A-Z]+_\w+_[a-z]+$")

class Source(BaseModel):
	tableName : tableNamePattern
	contentType : str
	language : langCodePattern
	version : versionPattern
	revision: str = "1"
	year: int
	license: str = "ISC"
	metadata: dict = None
	active: bool = True



class SourceEdit(BaseModel):
	sourceId : int
	contentType : str = None
	language : langCodePattern = None
	version : versionPattern = None
	revision: str = None
	year: int = None
	license: str = None
	metadata: dict = None
	active: bool = None

@app.get("/v2/sources", response_model=List[Source], status_code=200)
def get_source(contentType: str = None, versionAbbreviation: versionPattern = None, languageCode: langCodePattern =None, active: bool = True):
	'''Fetches all sources and their details.
	If one or more optional params are present, returns a filtered result if pressent
	and 404, if not found'''
	result = []	
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	return result

@app.post('/v2/sources', response_model=NormalResponse, status_code=201)
def add_source(source_obj : Source = Body(...)):
	''' Create a new source'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Source {source_obj.version} {source_obj.contentType} created successfully"}

@app.put('/v2/sources', response_model=NormalResponse, status_code=201)
def edit_version(source_obj: SourceEdit = Body(...)):
	''' Changes one or more fields of language'''
	logging.info(source_obj)
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message" : f"Updated source field(s)"}


# Point to discuss
# * A separate DELETE method is not defined. 
#   But soft delete can be performed by using the PUT method, and setting active to "False"
# * uses language code, content name, version name etc, instead of their ID values like in previous implementation

# #################

# #### Bible #######
# class Bible(Resource):
#     def get(self, source_id):
# 		# fetches the details of the specified bible
# 		# like, verision, revision, language, books present
#         pass

#     def get(self, source_id, book_code, output_type):
#     	# input: output_types can be usfm, json or text.
#     	# if text, returns cleaned contents in .._bible_cleaned table. 
#     	# otherwise, from corresponding column of .._bible table
# 		# fetches contents of the entire book
# 		# 
#         pass


#     def get(self, source_id, book_code, chapter, output_type):
#     	# input: output_types can be usfm, json or text.
#     	# if output_type is usfm,then split the usfm contents by '\c',
#     	#    check the chapter number of each slice and return the appropriate slice.
#     	#	 include the usfm head section also with the content if chapter is 1
#         pass

#     def get(self, ref_id_start, ref_id_end):
#     	# input: ref_id s can be used smartly to specify any kind of range. It need not be a valid ref_id 
#     	# 		for example to get all verses of chapter 3 of book 5 we can use 
#     	# 			ref_id_start = 5003000, ref_id_end= 5004000
#     	# This APi always returns cleaned text from the .._bible_cleaned table. 
#     	#     if foot-note or cross-ref is present for a verse, returns that too
#     	#		[{'ref_id':'',
#     	#			'verse':"",
#     	#			'cross-ref':'',
#     	#			'foot-note':''}, {}, ...]
#    		pass


#     def post(self):
#     	# input: a list of bible books to be added(all post, put and delete methods accept list of items for consistancy)
#     	#		 [{'sourceId': "", 
# 		#			'usfm': "",
# 		#			"json":""}, {}, ...]
#     	# Adds the contents to .._bible table and .._bible_cleaned table, if contents not already present for the books uploaded
#     	pass

#     def put(self):
#     	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
#     	#		[{'souceId':
#     	#		'usfm': "new value",
#     	#		'json':"", }, {}, ...]
#     	# unlike in other put methos, both columns(usfm & json) and values are mandatory in this, 
#     	# as they are inter-dependant values
#     	pass


# api.add_resource(Bible, '/bible', endpoint = 'bible')
# api.add_resource(Bible, '/bible/book/<int:source_id>/<text:book_code>/<text:output_type>', endpoint = 'bible/book')
# api.add_resource(Bible, '/bible/book/chapter/<int:source_id>/<text:book_code>/<int:chapter>/<text:output_type>', endpoint = 'bible/book/chapter')
# api.add_resource(Bible, '/bible/verse/<int:source_id>/<int:ref_id_start>/<int:ref_id_end>', endpoint = 'bible/verse')

# ### points to discuss, ############
# # 	1. do we need provision to delete each uploaded  book ?
# #       we do have 'put' if you need to update it
# #	2. Do we need a /bible get API to list all bibles(/sources/<text:content_type> does that now) ?

# #############################

# ##### Bible Books #####

# class BibleBook(Resource):
#     def get(self):
# 		# fetches all the bible book names(Eng) and codes 
#         pass

#     def get(self, language_code):
# 		# fetches all the bible book details in the specified language
#         pass


#     def post(self):
#     	# input: a list of bible book name details in any of languages to be created(all post, put and delete methods accept list of items for consistancy)
#     	#		 [{'bookId': "",
#     	#			'languageId': "".
#     	#			'abbr': "", 
# 		#			'shortName': ""
# 		#			'longName': ""}, {}, ...]
#     	# Note: only bible_book_names table can be updated. Not the bible books look up

#     def put(self):
#     	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
#     	#		[{'versionId':
#     	#		'<column name>': "new value"}, {}, ...]

# api.add_resource(BibleBook, '/biblebook', endpoint = 'biblebook')
# api.add_resource(BibleBook, '/biblebook/<text:language_code>', endpoint = 'biblebook')

# ##### DB chande suggested #######

# # change the columns name from 
# #	1. 'short' to 'short_name', 
# #	2. 'long' to 'long_name' and 
# #	3. 'abbr' to 'abbreviation' 

# ##################################


# ##### Commentry #####

# class Commentary(Resource):
#     def get(self, source_id):
# 		# fetches the details of the specified commentary
# 		# like, verision, revision, language, books present
#         pass

#     def get(self, source_id, book_code):
# 		# fetches commentary of the entire book
#         pass


#     def get(self, source_id, book_code, chapter):
# 		# fetches commentary of the selected chapter of the book
#         pass

#     def get(self, ref_id_start, ref_id_end):
#     	# input: ref_id s can be used smartly to specify any kind of range. It need not be a valid ref_id 
#     	# 		for example to get all commnataries of chapter 3 of book 5 we can use 
#     	# 			ref_id_start = 5003000, ref_id_end= 5004000
#    		pass

#     def post(self):
#     	# input: a list of commentries to be created(all post, put and delete methods accept list of items for consistancy)
#     	#		 [{'sourceId': "",
#     	#			'bookId': "".
#     	#			'chapter': "", 
# 		#			'verseNumber': "", 
# 		#			"commentary":""}, {}, ...]
#     	# create a new row in the DB

#     def put(self):
#     	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
#     	#		[{'sourceId':
#     	#		'book': "", "chapter": "", "verse": "", 'commentary': "new value"}, {}, ...]
#     	#		All keys in the input json are mandatory as th book-chapter-verse is the unique identifier of the row

# api.add_resource(Commentary, '/commentary', endpoint = '/commentary')
# api.add_resource(Bible, '/commentary/<int:source_id>/<int:ref_id_start>/<int:ref_id_end>', endpoint = '/commentary')
# api.add_resource(Bible, '/commentary/book/<int:source_id>/<text:book_code>', endpoint = '/commentary/book')
# api.add_resource(Bible, '/commentary/book/chapter/<int:source_id>/<text:book_code>/<int:chapter>', endpoint = '/commentary/book/chapter')

# ###### DB changes suggested ##############
# #	1. have a consitant pattern in table names
# #			at present, some table ends with 'notes'(hin_irv_notes) and another with 'commentary' (eng_mhcc commentary) 
# #			have a common last word like the bible tables
# #		language_code + version + revision(if present) + contentType can be considered for all content table names
# ############################################


# ########### Dictionary ###################
# class Dictionary(Resource):
#     def get(self, source_id):
# 		# fetches the details of the specified dictionary
# 		# like, verision, revision, language
#         pass

#     def get(self, source_id, word_pattern):
# 		# input: word_pattern can be the full or partial value of the word column
# 		#		for the entire contents of the dictionary an _ can be passed for word_pattern
# 		# the API should be written in a way, so that different column names can be handled, 
# 		#	in case, different dictionary tables have different fields 
#         pass

#     def post(self):
#     	# input: a list of commentries to be created(all post, put and delete methods accept list of items for consistancy)
#     	#		 [{'sourceId': "",
#     	#			fieldOne: }, {}, ...]
#     	# create a dictionary table with schema as per the input values(if not already created) and add values to it

#     def put(self):
#     	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
#     	#		[{'sourceId':"",
#     	#		'keyword':"",
#     	#		'<column name>': "new value"}, {}, ...]

# api.add_resource(Dictionary, '/dictionary', endpoint = '/infographics')
# api.add_resource(Dictionary, '/dictionary/<int:source_id>', endpoint = '/infographics')
# api.add_resource(Dictionary, '/dictionary/<int:source_id>/<text:word_pattern>', endpoint = '/infographics')

# #	1. have a consitant pattern in table names by adding dictionary to the end 
# #		language_code + version + revision(if present) + contentType can be considered for all content table names
# ###########################################



# ########### Infographic ###################

# class Infographics(Resource):
#     def get(self, source_id):
# 		# fetches the details of the specified infographic
# 		# like, verision, revision, language, books present
#         pass

#     def get(self, source_id, book_code):
# 		# fetches infographics of the selected book
#         pass

#     def post(self):
#     	# input: a list of commentries to be created(all post, put and delete methods accept list of items for consistancy)
#     	#		 [{'sourceId': "",
#     	#			'bookId': "",
# 		#			"infographics":""}, {}, ...]
#     	# create a new version in the DB

#     def put(self):
#     	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
#     	#		[{'sourceId':
#     	#		'bookId': "", 
#     	#		'infographics': "new value"}, {}, ...]
#     	#		All fields in the input json are mandatory 

# api.add_resource(Infographics, '/infographics', endpoint = '/infographics')
# api.add_resource(Infographics, '/infographics/<int:source_id>', endpoint = '/infographics')
# api.add_resource(Infographics, '/infographics/<int:source_id>/<text:book_code>', endpoint = '/infographics')


# ###########################################


# ########### Audio bible ###################
# class AudioBible(Resource):
#     def get(self, bible_source_id):
# 		# fetches the details of the audio bible
# 		# available for the specified bible
#         pass

#     def get(self, bible_source_id, book_code):
# 		# fetches details of the audio bible
# 		# available for the specified bible and book
#         pass

#     def post(self):
#     	# input: a list of audio bible details to be created(all post, put and delete methods accept list of items for consistancy)
#     	#		 [{'sourceId': "",
#     	#			'name': "",
# 		#			"url":"",...}, {}, ...]
#     	# create a new version in the DB

#     def put(self):
#     	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
#     	#		[{'auidoId':
#     	#		'<column name>': "new value"}, {}, ...]

# api.add_resource(AudioBible, '/audiobible', endpoint = '/audiobible')
# api.add_resource(AudioBible, '/audiobible/<int:bible_source_id>', endpoint = '/audiobible')
# api.add_resource(AudioBible, '/audiobible/<int:bible_source_id>/<text:book_code>', endpoint = '/audiobible')

# ### DB change ####
# # field books should accept only valid book codes(or list of book_codes)

# ###########################################


# ########### bible videos ###################
# class AudioBible(Resource):
#     def get(self, id):
# 		# fetches the details of the bible video
#         pass

#     def get(self, language_code):
# 		# fetches details of the bible videos available in that language
#         pass

#     def get(self, language_code, book_code):
# 		# fetches details of the bible videos available in that language and book
#         pass

#     def post(self):
#     	# input: a list of video bible details to be created(all post, put and delete methods accept list of items for consistancy)
#     	#		 [{'title':"",
#     	#			'book': "",
# 		#			"languageCode":"",...}, {}, ...]
#     	# create a new entry in the DB

#     def put(self):
#     	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
#     	#		[{'videoId':
#     	#		'<column name>': "new value"}, {}, ...]

# api.add_resource(AudioBible, '/audiobible', endpoint = '/audiobible')
# api.add_resource(AudioBible, '/audiobible/<int:bible_source_id>', endpoint = '/audiobible')
# api.add_resource(AudioBible, '/audiobible/<int:bible_source_id>/<text:book_code>', endpoint = '/audiobible')


# ### DB change ####
# # field books should accept only valid book codes(or list of book_codes)

# ###########################################