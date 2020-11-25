'''Defines all API endpoints for the web server app'''

import logging
import os
from typing import Optional, List
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Query, Path, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session

import crud 
import db_models
import schemas
from database import SessionLocal, engine

db_models.Base.metadata.create_all(bind=engine)


app = FastAPI()
logging.basicConfig(filename='../logs/API_logs.log',
    format='%(asctime)s|%(filename)s:%(lineno)d|%(levelname)-8s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')
log = logging.getLogger(__name__)
log.setLevel(os.environ.get("VACHAN_LOGGING_LEVEL", "WARNING"))
handler = RotatingFileHandler('../logs/API_logs.log', maxBytes=10000000, backupCount=10)
log.addHandler(handler)

######### Error Handling ##############

class DatabaseException(Exception):
    '''Format for Database error'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Database Error"
        self.detail = detail
        self.status_code = 502

@app.exception_handler(DatabaseException)
async def db_exception_handler(request, exc: DatabaseException):
    '''logs and returns error details'''
    log.error("Request:%s",request)
    log.error("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

class NotAvailableException(Exception):
    '''Format for not available Exception'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Requested Content Not Available"
        self.detail = detail
        self.status_code = 404

@app.exception_handler(NotAvailableException)
async def na_exception_handler(request, exc: NotAvailableException):
    '''logs and returns error details'''
    log.error("Request:%s",request)
    log.error("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

class AlreadyExistsException(Exception):
    '''Format for already exists error'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Already Exists"
        self.detail = detail
        self.status_code = 409

@app.exception_handler(AlreadyExistsException)
async def exists_exception_handler(request, exc: AlreadyExistsException):
    '''logs and returns error details'''
    log.error("Request:%s",request)
    log.error("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )
class TypeException(Exception):
    '''Format for type error'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Not the Required Type"
        self.detail = detail
        self.status_code = 415

@app.exception_handler(TypeException)
async def type_exception_handler(request, exc: TypeException):
    '''logs and returns error details'''
    log.error("Request:%s",request)
    log.error("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    '''logs and returns error details'''
    log.error("Request:%s",request)
    log.error("Http Error: %s", exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Error", "details": str(exc.detail)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    '''logs and returns error details'''
    log.error("Request:%s",request)
    log.error("Input Validation Error: %s", str(exc))
    return JSONResponse(
        status_code=422,
        content={"error": "Input Validation Error" ,"details": str(exc).replace("\n", ". ")}
    )
######################################################

def get_db():
    '''To start a DB connection(session)'''
    db_ = SessionLocal()
    try:
        yield db_
    finally:
        db_.close()

@app.get('/', response_model=schemas.NormalResponse, status_code=200)
def test():
    '''tests if app is running and the DB connection'''
    return {"message": "App is up and running"}



##### Content types #####

@app.get('/v2/contents', response_model=List[schemas.ContentType],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}},  status_code=200,
    tags=["Contents Types"])
def get_contents(content_type: str = Query(None), skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=0), db_: Session = Depends(get_db)):
    '''fetches all the contents types supported and their details
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n'''
    logging.info('In get_contents')
    logging.debug('contentType:%s, skip: %s, limit: %s',content_type, skip, limit)
    try:
        return crud.get_content_types(db_, content_type, skip, limit)
    except Exception as exe:
        logging.error('Error in get_contents')
        raise DatabaseException(str(exe))

@app.post('/v2/contents', response_model=schemas.ContentTypeUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Contents Types"])
def add_contents(content: schemas.ContentTypeCreate, db_: Session = Depends(get_db)):
    ''' Creates a new content type. 
    Additional operations required: 
        1. Add corresponding table creation functions to Database.
        2. Define input, output resources and all required APIs to handle this content'''
    logging.info('In add_contents')
    logging.debug('content: %s',content)
    if len(crud.get_content_types(db_, content.contentType)) > 0:
        logging.error('Error in add_contents')
        raise AlreadyExistsException("%s already present"%(content.contentType))
    try:
        return {'message': "Content type created successfully",
        "data": crud.create_content_type(db_=db_, content=content)}
    except Exception as exe:
        logging.error('Error in add_contents')
        raise DatabaseException(str(exe))

#################

##### languages #####

# @app.get('/v2/languages', response_model=List[schemas.LanguageResponse], status_code=200, tags=["Languages"])
# def get_language(language_code : schemas.langCodePattern = None, skip: int = 0, limit: int = 100):
#       '''fetches all the languages supported in the DB, their code and other details.
#       if query parameter, langauge_code is provided, returns details of that language if pressent
#       and 404, if not found
#       * skip=n: skips the first n objects in return list
#       * limit=n: limits the no. of items to be returned to n'''
#       result = [] 
#       try:
#           pass
#       except Exception as e:
#           raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#       return result

# @app.post('/v2/languages', response_model=schemas.LanguageUpdateResponse, status_code=201, tags=["Languages"])
# def add_language(lang_obj : schemas.Language = Body(...)):
#   ''' Create a new language'''
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message": f"Language {lang_obj.language} created successfully", "data": None}

# @app.put('/v2/languages', response_model=schemas.LanguageUpdateResponse, status_code=201, tags=["Languages"])
# def edit_language(lang_obj: schemas.LanguageEdit = Body(...)):
#   ''' Changes one or more fields of language'''
#   logging.info(lang_obj)
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message" : f"Updated language field(s)", 'data': None}

# ## NOTE
# # DELETE method not implemeneted for this resource
# # ################################


# ##### Version #####


# @app.get("/v2/versions", response_model=List[schemas.VersionResponse], status_code=200, tags=["Versions"])
# def get_version(versionAbbreviation : schemas.versionPattern = None, skip: int = 0, limit: int = 100):
#   '''Fetches all versions and their details.
#   If param versionAbbreviation is present, returns details of that version if pressent
#   and 404, if not found
#   * skip=n: skips the first n objects in return list
#   * limit=n: limits the no. of items to be returned to n'''
#   result = [] 
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   return result

# @app.post('/v2/versions', response_model=schemas.VersionUpdateResponse, status_code=201, tags=["Versions"])
# def add_version(version_obj : schemas.Version = Body(...)):
#   ''' Creates a new version '''
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message": f"Version {version_obj.versionAbbreviation} created successfully", "data": None}

# @app.put('/v2/versions', response_model=schemas.VersionUpdateResponse, status_code=201, tags=["Versions"])
# def edit_version(version_obj: schemas.VersionEdit = Body(...)):
#   ''' Changes one or more fields of vesrion types table'''
#   logging.info(version_obj)
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message" : f"Updated version field(s)", "data": None}

# ## NOTE
# # DELETE method not implemeneted for this resource
# # ################################


# ##### Source #####


# @app.get("/v2/sources", response_model=List[schemas.Source], status_code=200, tags=["Sources"])
# def get_source(contentType: str = None, versionAbbreviation: schemas.versionPattern = None, languageCode: schemas.langCodePattern =None, skip: int = 0, limit: int = 100, active: bool = True):
#   '''Fetches all sources and their details.
#   If one or more optional params are present, returns a filtered result if pressent
#   and 404, if not found
#   * skip=n: skips the first n objects in return list
#   * limit=n: limits the no. of items to be returned to n'''
#   result = [] 
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   return result

# @app.post('/v2/sources', response_model=schemas.SourceUpdateResponse, status_code=201, tags=["Sources"])
# def add_source(source_obj : schemas.Source = Body(...)):
#   ''' Creates a new source entry in sources table. 
#   Also creates all associtated tables for the content type.
#   '''
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message": f"Source {source_obj.version} {source_obj.contentType} created successfully", "data": None}

# @app.put('/v2/sources', response_model=schemas.SourceUpdateResponse, status_code=201, tags=["Sources"])
# def edit_source(source_obj: schemas.SourceEdit = Body(...)):
#   ''' Changes one or more fields of source '''
#   logging.info(source_obj)
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message" : f"Updated source field(s)", "data": None}


# # Point to discuss
# # * A separate DELETE method is not defined. 
# #   But soft delete can be performed by using the PUT method, and setting active to "False"
# # * uses language code, content name, version name etc, instead of their ID values like in previous implementation

# # #################

# ############ Bible Books ##########


# @app.get('/v2/lookup/bible/books', response_model=List[schemas.BibleBook], status_code=200, tags=["Lookups"])
# def get_bible_book(bookId: int = None, bookCode: schemas.BookCodePattern = None, skip: int = 0, limit: int = 100):
#   ''' returns the list of book ids, codes and names.
#   If any of the query params are provided the details of corresponding book
#   will be returned
#   * skip=n: skips the first n objects in return list
#   * limit=n: limits the no. of items to be returned to n'''
#   result = [] 
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   return result

# ## NOTE
# # This is a predefined table. So it is read-only and no PUT, POST or DELETE methods re defined for it


# # # #### Bible #######


# @app.post('/v2/bibles/{sourceName}/books', response_model=schemas.BibleBookUpdateResponse, status_code=201, tags=["Bibles"])
# def add_bible_book(sourceName: schemas.tableNamePattern, bibleBookObj : schemas.BibleBookUpload = Body(...)):
#   '''Uploads a bible book. It update 3 tables: ..._bible, .._bible_cleaned, ..._bible_tokens'''
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message": f"Bible book uploaded successfully", "data": None }


# @app.put('/v2/bibles/{sourceName}/books', response_model=schemas.BibleBookUpdateResponse, status_code=201, tags=["Bibles"])
# def edit_bible_book(sourceName: schemas.tableNamePattern, bibleBookObj: schemas.BibleBookUpload = Body(...)):
#   ''' Changes both usfm and json fileds of bible book. 
#   The contents of the respective bible_clean and bible_tokens tables' contents 
#   should be deleted and new data added. 
#   two fields are mandatory as usfm and json are interdependant'''
#   logging.info(bibleBookObj)
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message" : f"Updated bible book and associated tables", "data": None}


# @app.get('/v2/bibles/{sourceName}/books', response_model=List[schemas.BibleBookContent], status_code=200, tags=["Bibles"])
# def get_available_bible_books(sourceName: schemas.tableNamePattern, bookCode: schemas.BookCodePattern = None, contentType: schemas.BookContentType = None, versification: bool = False, skip: int = 0, limit: int = 100):
#   '''Fetches all the books available(has been uploaded) in the specified bible
#   * returns all available(uploaded) books without bookCode and contentType
#   * returns above details of one book: if bookCode is specified
#   * versification can be set to true if the book structure is required(chapters in a book and verse numbers in each chapter)
#   * returns the JSON, USFM and/or Audio contents also: if contentType is given
#   * skip=n: skips the first n objects in return list
#   * limit=n: limits the no. of items to be returned to n'''
#   result = [] 
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   return result


# @app.get("/v2/bibles/{sourceName}/verses", response_model=List[schemas.BibleVerse], status_code=200, tags=["Bibles"])
# def get_bible_verse(sourceName: schemas.tableNamePattern, bookCode: schemas.BookCodePattern = None, chapter: int = None, verse: int = None, lastVerse: int = None, searchPhrase: str = None, skip: int = 0, limit: int = 100):
#   ''' Fetches the cleaned contents of bible, within a verse range, if specified.
#   This API could be used for fetching, 
#    * all verses of a source : with out giving any query params.
#    * all verses of a book: with only book_code
#    * all verses of a chapter: with book_code and chapter 
#    * one verse: with bookCode, chapter and verse(without lastVerse).
#    * any range of verses within a chapter: using verse and lastVerse appropriately
#    * search for a query phrase in a bible and get matching verses: using searchPhrase
#    * skip=n: skips the first n objects in return list
#    * limit=n: limits the no. of items to be returned to n'''
#   result = [] 
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   return result

# # ##### NOTES for Discussion
# # 1. we use source_id in the input to identify the specific bible. 
# #    It could be replaced with the table name, which is in a more human understandable pattern
# # 2. The API to list all bibles is not provided with a /v2/bible... endpoint, but is available in /v2/sources?contentType=bible
# # 3. AT present the _bible_tokens table is populated upon uploading a new bible book to the DB. 
# #     As this table is used only in AgMT App, this table need to be populated after a request for tokens/creation of project with this source_id from the AgMT App
# # 4. No DELETE API for this resource. To delete(soft) the whole bible, the source's active status can be set to False.
# #      An uploaded bible book can be altered by uploading a new one(PUT), but it cannoted be deleted 



# # ########### Audio bible ###################

# @app.post('/v2/bibles/{sourceName}/audios', response_model=schemas.AudioBibleUpdateResponse, status_code=201, tags=["Bibles"])
# def add_audio_bible(sourceName: schemas.tableNamePattern, audios:List[schemas.AudioBibleUpload] = Body(...)):
#   '''Uploads a list of Audio Bible URLs and other associated info about them.'''
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message": f"Audio bible details uploaded successfully", "data": None}

# @app.put('/v2/bibles/{sourceName}/audios', response_model=schemas.AudioBibleUpdateResponse, status_code=201, tags=["Bibles"])
# def edit_audio_bible(sourceName: schemas.tableNamePattern, audios: List[schemas.AudioBibleEdit] = Body(...)):
#   ''' Changes the mentioned fields of audio bible row'''
#   logging.info(audios)
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message" : f"Updated audio bible details", "data": None}


# # ### DB change ####
# # # field books should accept only valid book codes(or list of book_codes)






# # ##### Bible Book names in regional languages ########################

# # ##### DB change suggested #######
# # Currently, this is a separate table in DB. 
# # It could be added to a metadata column in the _bible table 
# # # change the columns name from 
# # #   1. 'short' to 'short_name', 
# # #   2. 'long' to 'long_name' and 
# # #   3. 'abbr' to 'abbreviation' 
# # in the metadata jSON object
# # ##################################


# # ##### Commentary #####


# @app.get('/v2/commentaries/{sourceName}', response_model=List[schemas.Commentary], status_code=200, tags=["Commentaries"])
# def get_commentary(sourceName: schemas.tableNamePattern, bookCode: schemas.BookCodePattern = None, chapter: int = None, verse: int = None, lastVerse: int = None, skip: int = 0, limit: int = 100):
#   '''Fetches commentries under the specified source.
#   Using the params bookCode, chapter, and verse the result set can be filtered as per need, like in the /v2/bibles/{sourceName}/verses API
#   * skip=n: skips the first n objects in return list
#   * limit=n: limits the no. of items to be returned to n'''
#   result = [] 
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   return result

# @app.post('/v2/commentaries/{sourceName}', response_model=schemas.CommentaryUpdateResponse, status_code=201, tags=["Commentaries"])
# def add_commentary(sourceName: schemas.tableNamePattern, commentries:List[schemas.Commentary] = Body(...)):
#   '''Uploads a list of commentaries.'''
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message": f"Commentaries uploaded successfully", "data": None}

# @app.put('/v2/commentaries/{sourceName}', response_model=schemas.CommentaryUpdateResponse, status_code=201, tags=["Commentaries"])
# def edit_commentary(sourceName: schemas.tableNamePattern, commentries: List[schemas.Commentary] = Body(...)):
#   ''' Changes the commentary field to the given value in the row selected using book, chapter, verse values'''
#   logging.info(commentries)
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message" : f"Updated commentries", "data": None}



# ## ##NOTE##
# # 1. The API to list all bibles is not provided with a /v2/bible... endpoint, but is available in /v2/sources?contentType=commentary
# # 2. POST and PUT methods takes list of commentary objects and adds them together to DB. Process will be aborted in case of error in any of the rows
# # 3. Type of verseNumber is mentioned as int here. Can be changed if required 


# # ########### Dictionary ###################


# @app.get('/v2/dictionaries/{sourceName}', response_model=List[schemas.DictionaryWord], status_code=200, tags=["Dictionaries"])
# def get_dictionary_words(sourceName: schemas.tableNamePattern, searchIndex: str = None, wordListOnly: bool = False, skip: int = 0, limit: int = 100):
#   '''fetches list of dictionary words and all available details about them.
#   Using the searchIndex appropriately, it is possible to get
#   * All words starting with a letter
#   * All words starting with a substring
#   * An exact word search, giving the whole word
#   * By setting the wordListOnly flag to True, only the words would be inlcuded in the return object, without the details
#   * skip=n: skips the first n objects in return list
#   * limit=n: limits the no. of items to be returned to n'''
#   result = [] 
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   return result


# @app.post('/v2/dictionaries/{sourceName}', response_model=schemas.DictionaryUpdateResponse, status_code=201, tags=["Dictionaries"])
# def add_dictionary(sourceName: schemas.tableNamePattern, words: List[schemas.DictionaryWord] = Body(...)):
#   ''' uploads dictionay words'''
#   logging.info(words)
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message": f"Dictionary table created and words uploaded successfully", "data": None}

# @app.put('/v2/dictionaries/{sourceName}', response_model=schemas.DictionaryUpdateResponse, status_code=201, tags=["Dictionaries"])
# def edit_dictionary(sourceName: schemas.tableNamePattern, words: List[schemas.DictionaryWord] = Body(...)):
#   '''Updates the given fields mentioned in details object, of the specifed word'''
#   logging.info(words)
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message" : f"Updated dictionary words", "data": None}

# ## ### NOTE ####
# # Currently we only have Strongs numbers as a dictionary table.
# # But we can have a wide variety of lexical collections with varying informations required to be stored in the DB.
# # So suggesting a flexible table structure and APIs to accomodate future needs.
# # ##### DB Change suggested ######
# # 1. Have 3 columns word_id, word and details
# #     details column will be of JSON datatype and will have 
# #     all the additional info we have in that collection(for each word) as key-value pairs


# # ###########################################



# # ########### Infographic ###################


# @app.get('/v2/infographics/{sourceName}', response_model=List[schemas.Infographic], status_code=200, tags=["Infographics"])
# def get_infographic(sourceName: schemas.tableNamePattern, bookCode: schemas.BookCodePattern = None, skip: int = 0, limit: int = 100 ):
#   '''Fetches the infographics. Can use, bookCode to filter the results
#   * skip=n: skips the first n objects in return list
#   * limit=n: limits the no. of items to be returned to n'''
#   result = [] 
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   return result

# @app.post('/v2/infographics/{sourceName}', response_model=schemas.InfographicUpdateResponse, status_code=201, tags=["Infographics"])
# def add_infographics(sourceName: schemas.tableNamePattern, infographics:List[schemas.Infographic] = Body(...)):
#   '''Uploads a list of infograhics.'''
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message": f"Infographics uploaded successfully", "data": None}

# @app.put('/v2/infographics/{sourceName}', response_model=schemas.InfographicUpdateResponse, status_code=201, tags=["Infographics"])
# def edit_infographics(sourceName: schemas.tableNamePattern, infographics: List[schemas.Infographic] = Body(...)):
#   ''' Changes the commentary field to the given value in the row selected using book, chapter, verse values'''
#   logging.info(infographics)
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message" : f"Updated infographics", "data": None}




# # ###########################################


# # ########### bible videos ###################

# @app.get('/v2/biblevideos/{sourceName}', response_model=List[schemas.BibleVideo], status_code=200, tags=["Bible Videos"])
# def get_bible_video(bookCode: schemas.BookCodePattern = None, theme: str = None, title: str = None, skip: int = 0, limit: int = 100):
#   '''Fetches the Bible video details and URL. Can use the optional query params book, title and theme to filter the results
#   * skip=n: skips the first n objects in return list
#   * limit=n: limits the no. of items to be returned to n'''
#   result = [] 
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   return result

# @app.post('/v2/biblevideos/{sourceName}', response_model=schemas.BibleVideoUpdateResponse, status_code=201, tags=["Bible Videos"])
# def add_bible_video(videos:List[schemas.BibleVideoUpload] = Body(...)):
#   '''Uploads a list of bible video links and details.'''
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Already exists", detail="Content already present", status_code=409)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message": f"BibleVideo details uploaded successfully", "data": None}

# @app.put('/v2/biblevideos/{sourceName}', response_model=schemas.BibleVideoUpdateResponse, status_code=201, tags=["Bible Videos"])
# def edit_bible_video(videos: List[schemas.BibleVideoEdit] = Body(...)):
#   ''' Changes the commentary field to the given value in the row selected using book, chapter, verse values'''
#   logging.info(videos)
#   try:
#       pass
#   except Exception as e:
#       raise VachanApiException(name="Not available", detail="Requested content not available", status_code=404)
#   except Exception as e:
#       raise VachanApiException(name="Incorrect Content Type", detail="The source is not of the required type, for this function", status_code=415)
#   except Exception as e:
#       raise VachanApiException(name="Database Error", detail=str(e), status_code=502)
#   return {"message" : f"Updated bible video details", "data": None}


# # ### DB change ####
# # 1. The BibleVideos is made an entry in contentTypes table
# # 2. new source to be added to sources table and new table to be created for every language, at least(if version name and revision are same)
# # 3. the filed language can then be removed from the table
# # 4. field 'books' should accept only valid book codes and 
# #    datatype should be JSON, like in audio bibles, not comma separated text

# # ###########################################