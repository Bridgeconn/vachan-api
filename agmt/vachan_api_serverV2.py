from fastapi import FastAPI, Query, Path, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr, AnyUrl
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

@app.get('/v2/contents', response_model=List[ContentType], status_code=200, tags=["Contents Types"])
def get_contents():
	'''fetches all the contents types supported and their details '''
	result = []
	return result   

@app.post('/v2/contents', response_model=NormalResponse, status_code=201, tags=["Contents Types"])
def add_contents(content_name: str  = Body(...)):
	''' Creates a new content type. 
	Additional operations required: 
		1. Add corresponding table creation functions to Database.
		2. Define input, output resources and all required APIs to handle this content'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
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

@app.get('/v2/languages', response_model=List[Language], status_code=200, tags=["Languages"])
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

@app.post('/v2/languages', response_model=NormalResponse, status_code=201, tags=["Languages"])
def add_language(lang_obj : Language = Body(...)):
	''' Create a new language'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Language {lang_obj.language} created successfully"}

@app.put('/v2/languages', response_model=NormalResponse, status_code=201, tags=["Languages"])
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


@app.get("/v2/versions", response_model=List[Version], status_code=200, tags=["Versions"])
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

@app.post('/v2/versions', response_model=NormalResponse, status_code=201, tags=["Versions"])
def add_version(version_obj : Version = Body(...)):
	''' Create a new language'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Version {version_obj.versionAbbreviation} created successfully"}

@app.put('/v2/versions', response_model=NormalResponse, status_code=201, tags=["Versions"])
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
	sourceName : tableNamePattern
	contentType : str
	language : langCodePattern
	version : versionPattern
	revision: str = "1"
	year: int
	license: str = "ISC"
	metadata: dict = None
	active: bool = True



class SourceEdit(BaseModel):
	sourceName : int
	contentType : str = None
	language : langCodePattern = None
	version : versionPattern = None
	revision: str = None
	year: int = None
	license: str = None
	metadata: dict = None
	active: bool = None

@app.get("/v2/sources", response_model=List[Source], status_code=200, tags=["Sources"])
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

@app.post('/v2/sources', response_model=NormalResponse, status_code=201, tags=["Sources"])
def add_source(source_obj : Source = Body(...)):
	''' Creates a new source entry in sources table. Also creates all associtated tables for the contenty type,
	except for bible_videos. Bible videos are all stored in one table. '''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Source {source_obj.version} {source_obj.contentType} created successfully"}

@app.put('/v2/sources', response_model=NormalResponse, status_code=201, tags=["Sources"])
def edit_source(source_obj: SourceEdit = Body(...)):
	''' Changes one or more fields of source '''
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

############ Bible Books ##########
BookCodePattern = constr(regex="^[a-z1-9][a-z][a-z]$")

class BibleBook(BaseModel):
	bookId : int
	bookName : str
	bookCode : BookCodePattern

@app.get('/v2/biblebooks', response_model=List[BibleBook], status_code=200, tags=["Bible Books"])
def get_bible_book(bookId: int = None, bookCode: BookCodePattern = None):
	''' returns the list of book ids, codes and names.
	If any of the query params are provided the details of corresponding book
	will be returned'''
	result = []	
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	return result

## NOTE
# This is a predefined table. So it is read-only and no PUT, POST or DELETE methods re defined for it


# # #### Bible #######
class AudioBible(BaseModel):
	audioId: int
	name: str
	url: AnyUrl
	books: dict
	format: str
	status: bool

class AudioBibleUpload(BaseModel):
	name: str
	url: AnyUrl
	books: dict
	format: str
	status: bool


class AudioBibleEdit(BaseModel):
	audioId: int
	name: str = None
	url: str = None
	books: dict = None
	format: str = None
	status: bool = None

class BibleBookContent(BaseModel):
	bookCode : BookCodePattern
	structure : dict 
	USFM: str = None
	JSON: dict = None
	audio: AudioBible = None

class BibleBookUpload(BaseModel):
	USFM: str 
	JSON: dict

class Reference(BaseModel):
	# bible : Source = None
	bookId: int = None
	bookcode: BookCodePattern
	chapter: int
	verseNumber: int
	verseNumberEnd: int = None

class BibleVerse(BaseModel):
	reference : Reference
	verseText: str
	footNote : str = None
	crossReference : str = None

class BookContentType(str, Enum):
	USFM = 'usfm'
	JSON = 'json'
	audio = 'audio'
	all = 'all'


@app.post('/v2/bibles/{sourceName}/books', response_model=NormalResponse, status_code=201, tags=["Bibles"])
def add_bible_book(sourceName: tableNamePattern, bibleBookObj : BibleBookUpload = Body(...)):
	'''Uploads a bible book. It update 3 tables: ..._bible, .._bible_cleaned, ..._bible_tokens'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Bible book uploaded successfully"}


@app.put('/v2/bibles/{sourceName}/books', response_model=NormalResponse, status_code=201, tags=["Bibles"])
def edit_bible_book(sourceName: tableNamePattern, bibleBookObj: BibleBookUpload = Body(...)):
	''' Changes both usfm and json fileds of bible book. 
	The contents of the respective bible_clean and bible_tokens tables' contents 
	should be deleted and new data added. 
	two fields are mandatory as usfm and json are interdependant'''
	logging.info(bibleBookObj)
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message" : f"Updated bible book and associated tables"}


@app.get('/v2/bibles/{sourceName}/books', response_model=List[BibleBookContent], status_code=200, tags=["Bibles"])
def get_available_bible_books(sourceName: tableNamePattern, bookCode: BookCodePattern = None, contentType: BookContentType = None):
	'''Fetches all the books available(has been uploaded) in the specified bible
	* returns all available books and their chapter-verse structure: without bookCode and contentType
	* returns above details of one book: if bookCode is specified
	* returns the JSON, USFM and/or Audio contents also: if contentType is given'''
	result = []	
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	return result


@app.get("/v2/bibles/{sourceName}/verses", response_model=List[BibleVerse], status_code=200, tags=["Bibles"])
def get_bible_verse(sourceName: tableNamePattern, bookCode: BookCodePattern = None, chapter: int = None, verse: int = None, lastVerse: int = None, searchPhrase: str = None):
	''' Fetches the cleaned contents of bible, within a verse range, if specified.
	This API could be used for fetching, 
	 * all verses of a source : with out giving any query params.
	 * all verses of a book: with only book_code
	 * all verses of a chapter: with book_code and chapter 
	 * one verse: with bookCode, chapter and verse(without lastVerse).
	 * any range of verses within a chapter: using verse and lastVerse appropriately
	 * search for a query phrase in a bible and get matching verses: using searchPhrase'''
	result = []	
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	return result

# ##### NOTES for Discussion
# 1. we use source_id in the input to identify the specific bible. 
#    It could be replaced with the table name, which is in a more human understandable pattern
# 2. The API to list all bibles is not provided with a /v2/bible... endpoint, but is available in /v2/sources?contentType=bible
# 3. AT present the _bible_tokens table is populated upon uploading a new bible book to the DB. 
#     As this table is used only in AgMT App, this table need to be populated after a request for tokens/creation of project with this source_id from the AgMT App
# 4. No DELETE API for this resource. To delete(soft) the whole bible, the source's active status can be set to False.
#      An uploaded bible book can be altered by uploading a new one(PUT), but it cannoted be deleted 



# ########### Audio bible ###################

@app.post('/v2/bibles/{sourceName}/audios', response_model=NormalResponse, status_code=201, tags=["Bibles"])
def add_audio_bible(sourceName: tableNamePattern, audios:List[AudioBibleUpload] = Body(...)):
	'''Uploads a list of Audio Bible URLs and other associated info about them.'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Audio bible details uploaded successfully"}

@app.put('/v2/bibles/{sourceName}/audios', response_model=NormalResponse, status_code=201, tags=["Bibles"])
def edit_audio_bible(sourceName: tableNamePattern, audios: List[AudioBibleEdit] = Body(...)):
	''' Changes the mentioned fields of audio bible row'''
	logging.info(audios)
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message" : f"Updated audio bible details"}


# ### DB change ####
# # field books should accept only valid book codes(or list of book_codes)






# ##### Bible Book names in regional languages ########################

# ##### DB change suggested #######
# Currently, this is a separate table in DB. 
# It could be added to a metadata column in the _bible table or to a metadata column in bible_books_lookup table
# # change the columns name from 
# #	1. 'short' to 'short_name', 
# #	2. 'long' to 'long_name' and 
# #	3. 'abbr' to 'abbreviation' 
# in the metadata jSON object
# ##################################


# ##### Commentary #####

class Commentary(BaseModel):
	bookCode : BookCodePattern
	chapter: int
	verseNumber: int
	commentary: str

@app.get('/v2/commentaries/{sourceName}', response_model=List[Commentary], status_code=200, tags=["Commentaries"])
def get_commentary(sourceName: tableNamePattern, bookCode: BookCodePattern = None, chapter: int = None, verse: int = None, lastVerse: int = None):
	'''Fetches commentries under the specified source.
	Using the params bookCode, chapter, and verse the result set can be filtered as per need, like in the /v2/bibles/{sourceName}/verses API'''
	result = []	
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	return result

@app.post('/v2/commentaries/{sourceName}', response_model=NormalResponse, status_code=201, tags=["Commentaries"])
def add_commentary(sourceName: tableNamePattern, commentries:List[Commentary] = Body(...)):
	'''Uploads a list of commentaries.'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Commentaries uploaded successfully"}

@app.put('/v2/commentaries/{sourceName}', response_model=NormalResponse, status_code=201, tags=["Commentaries"])
def edit_commentary(sourceName: tableNamePattern, commentries: List[Commentary] = Body(...)):
	''' Changes the commentary field to the given value in the row selected using book, chapter, verse values'''
	logging.info(commentries)
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message" : f"Updated commentries"}



## ##NOTE##
# 1. The API to list all bibles is not provided with a /v2/bible... endpoint, but is available in /v2/sources?contentType=commentary
# 2. POST and PUT methods takes list of commentary objects and adds them together to DB. Process will be aborted in case of error in any of the rows
# 3. Type of verseNumber is mentioned as int here. Can be changed if required 


# ########### Dictionary ###################
letterPattern = constr(regex='^\w$')
class DictionaryWord(BaseModel):
	word: str
	details: dict

@app.get('/v2/dictionaries/{sourceName}', response_model=List[DictionaryWord], status_code=200, tags=["Dictionaries"])
def get_dictionary_words(sourceName: tableNamePattern, searchIndex: str = None):
	'''fetches list of dictionary words and all available details about them.
	Using the searchIndex appropriately, it is possible to get
	* All words starting with a letter
	* All words starting with a substring
	* An exact word search, giving the whole word'''
	result = []	
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	return result


@app.post('/v2/dictionaries/{sourceName}', response_model=NormalResponse, status_code=201, tags=["Dictionaries"])
def add_dictionary(sourceName: tableNamePattern, words: List[DictionaryWord] = Body(...)):
	''' uploads dictionay words'''
	logging.info(words)
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Dictionary table created and words uploaded successfully"}

@app.put('/v2/dictionaries/{sourceName}', response_model=NormalResponse, status_code=201, tags=["Dictionaries"])
def edit_dictionary(sourceName: tableNamePattern, words: List[DictionaryWord] = Body(...)):
	'''Updates the given fields mentioned in details object, of the specifed word'''
	logging.info(words)
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message" : f"Updated dictionary words"}

## ### NOTE ####
# Currently we only have Strongs numbers as a dictionary table.
# But we can have a wide variety of lexical collections with varying informations required to be stored in the DB.
# So suggesting a flexible table structure and APIs to accomodate future needs.
# ##### DB Change suggested ######
# 1. Have 3 columns word_id, word and details
# 	details column will be of JSON datatype and will have 
# 	all the additional info we have in that collection(for each word) as key-value pairs


# ###########################################



# ########### Infographic ###################

class Infographic(BaseModel):
	bookCode : BookCodePattern
	infographicsLink : AnyUrl

@app.get('/v2/infographics/{sourceName}', response_model=List[Infographic], status_code=200, tags=["Infographics"])
def get_infographic(sourceName: tableNamePattern, bookCode: BookCodePattern = None ):
	'''Fetches the infographics. Can use, bookCode to filter the results'''
	result = []	
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	return result

@app.post('/v2/infographics/{sourceName}', response_model=NormalResponse, status_code=201, tags=["Infographics"])
def add_infographics(sourceName: tableNamePattern, infographics:List[Infographic] = Body(...)):
	'''Uploads a list of infograhics.'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"Infographics uploaded successfully"}

@app.put('/v2/infographics/{sourceName}', response_model=NormalResponse, status_code=201, tags=["Infographics"])
def edit_infographics(sourceName: tableNamePattern, infographics: List[Infographic] = Body(...)):
	''' Changes the commentary field to the given value in the row selected using book, chapter, verse values'''
	logging.info(infographics)
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message" : f"Updated infographics"}




# ###########################################


# ########### bible videos ###################

class BibleVideo(BaseModel):
	bibleVideoId: int
	books: dict
	videoLink: AnyUrl
	title: str
	description: str
	theme: str
	language: str
	status: bool

class BibleVideoUpload(BaseModel):
	books: dict
	videoLink: AnyUrl
	title: str
	description: str
	theme: str
	language: str
	status: bool


class BibleVideoEdit(BaseModel):
	bibleVideoId: int
	books: dict  = None
	videoLink: AnyUrl  = None
	title: str  = None
	description: str  = None
	theme: str  = None
	language: str  = None
	status: bool  = None

@app.get('/v2/biblevideos', response_model=List[BibleVideo], status_code=200, tags=["Bible Videos"])
def get_bible_video(bookCode: BookCodePattern = None, language:langCodePattern = None, theme: str = None, title: str = None):
	'''Fetches the infographics. Can use the optional query params book, langugage, title and theme to filter the results'''
	result = []	
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	return result

@app.post('/v2/biblevideos', response_model=NormalResponse, status_code=201, tags=["Bible Videos"])
def add_bible_video(videos:List[BibleVideoUpload] = Body(...)):
	'''Uploads a list of bible video links and details.'''
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message": f"BibleVideo details uploaded successfully"}

@app.put('/v2/biblevideos', response_model=NormalResponse, status_code=201, tags=["Bible Videos"])
def edit_bible_video(videos: List[BibleVideoEdit] = Body(...)):
	''' Changes the commentary field to the given value in the row selected using book, chapter, verse values'''
	logging.info(videos)
	try:
		pass
	except Exception as e:
		raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
	except Exception as e:
		raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
	except Exception as e:
		raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
	return {"message" : f"Updated bible video details"}


# ### DB change ####
# # field books should accept only valid book codes and 
#    datatype should be JSON, like in audio bibles, not comma separated text

# ###########################################