'''Defines all API endpoints for the web server app'''

from typing import List, Tuple
from fastapi import FastAPI, Query, Body, Depends, Path, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

import db_models
import schemas, schemas_nlp
from logger import log
from database import SessionLocal, engine
from custom_exceptions import GenericException
from custom_exceptions import NotAvailableException, AlreadyExistsException, TypeException

#pylint: disable=E0401
#pylint gives import error if relative import is not used. But app(uvicorn) doesn't accept it
from crud import structurals_crud, contents_crud, nlp_crud



app = FastAPI()

######### Error Handling ##############

@app.exception_handler(Exception)
async def any_exception_handler(request, exc: Exception):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",'Error', str(exc))
    if hasattr(exc, "status_code"):
        status_code=exc.status_code
    else:
        status_code = 500
    return JSONResponse(
        status_code =status_code,
        content={"error": 'Error', "details" : str(exc)},
    )

@app.exception_handler(GenericException)
async def generic_exception_handler(request, exc: GenericException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request, exc: SQLAlchemyError):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    if hasattr(exc, 'orig'):
        detail = str(exc.orig).replace('DETAIL:','')
    else:
        detail = str(exc)
    log.exception("%s: %s","Database Error", detail)
    return JSONResponse(
        status_code=502,
        content={"error": "Database Error", "details" : detail},
    )


@app.exception_handler(NotAvailableException)
async def na_exception_handler(request, exc: NotAvailableException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )


@app.exception_handler(AlreadyExistsException)
async def exists_exception_handler(request, exc: AlreadyExistsException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(TypeException)
async def type_exception_handler(request, exc: TypeException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    '''logs and returns error details'''
    log.error("Request URL:%s %s, from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("Http Error: %s", exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Error", "details": str(exc.detail)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    '''logs and returns error details'''
    log.error("Request URL:%s %s, from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("Input Validation Error: %s", str(exc))
    return JSONResponse(
        status_code=422,
        content={"error": "Input Validation Error" ,"details": str(exc).replace("\n", ". ")}
    )

@app.exception_handler(IntegrityError)
async def unique_violation_exception_handler(request, exc: IntegrityError):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s","Already Exists", exc.__dict__)
    return JSONResponse(
        status_code=409,
        content={"error": "Already Exists", "details" : str(exc.orig).replace("DETAIL","")},
    )
######################################################

def get_db():
    '''To start a DB connection(session)'''
    db_ = SessionLocal()
    try:
        yield db_
    finally:
        pass
        # db_.close()

db_models.map_all_dynamic_tables(db_= next(get_db()))
db_models.Base.metadata.create_all(bind=engine)


@app.get('/', response_model=schemas.NormalResponse, status_code=200)
def test(db_: Session = Depends(get_db)):
    '''tests if app is running and the DB connection is active'''
    db_.query(db_models.Language).first()
    return {"message": "App is up and running"}



##### Content types #####

@app.get('/v2/contents', response_model=List[schemas.ContentType],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}},  status_code=200,
    tags=["Contents Types"])
def get_contents(content_type: str = Query(None, example="bible"), skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=0), db_: Session = Depends(get_db)):
    '''fetches all the contents types supported and their details
    * the optional query parameter can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n'''
    log.info('In get_contents')
    log.debug('contentType:%s, skip: %s, limit: %s',content_type, skip, limit)
    return structurals_crud.get_content_types(db_, content_type, skip, limit)

@app.post('/v2/contents', response_model=schemas.ContentTypeUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Contents Types"])
def add_contents(content: schemas.ContentTypeCreate, db_: Session = Depends(get_db)):
    ''' Creates a new content type.
    Naming conventions to be followed
    - Use only english alphabets in lower case
    Additional operations required:
        1. Add corresponding table creation functions and mappings.
        2. Define input, output resources and all required APIs to handle this content'''
    log.info('In add_contents')
    log.debug('content: %s',content)
    if len(structurals_crud.get_content_types(db_, content.contentType)) > 0:
        raise AlreadyExistsException("%s already present"%(content.contentType))
    return {'message': "Content type created successfully",
    "data": structurals_crud.create_content_type(db_=db_, content=content)}

#################

##### languages #####

@app.get('/v2/languages',
    response_model=List[schemas.LanguageResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Languages"])
def get_language(language_code : schemas.LangCodePattern = Query(None, example="hin"),
    language_name: str = Query(None, example="hindi"),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0), db_: Session = Depends(get_db)):
    '''fetches all the languages supported in the DB, their code and other details.
    * if any of the optional query parameters are provided, returns details of that language
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_language')
    log.debug('langauge_code:%s, language_name: %s, skip: %s, limit: %s',
        language_code, language_name, skip, limit)
    return structurals_crud.get_languages(db_, language_code, language_name,
        skip = skip, limit = limit)

@app.post('/v2/languages', response_model=schemas.LanguageCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Languages"])
def add_language(lang_obj : schemas.LanguageCreate = Body(...), db_: Session = Depends(get_db)):
    ''' Creates a new language. Langugage code should of 3 letters which uniquely identifies it.'''
    log.info('In add_language')
    log.debug('lang_obj: %s',lang_obj)
    if len(structurals_crud.get_languages(db_, language_code = lang_obj.code)) > 0:
        raise AlreadyExistsException("%s already present"%(lang_obj.code))
    return {'message': "Language created successfully",
    "data": structurals_crud.create_language(db_=db_, lang=lang_obj)}

@app.put('/v2/languages', response_model=schemas.LanguageUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Languages"])
def edit_language(lang_obj: schemas.LanguageEdit = Body(...), db_: Session = Depends(get_db)):
    ''' Changes one or more fields of language'''
    log.info('In edit_language')
    log.debug('lang_obj: %s',lang_obj)
    if len(structurals_crud.get_languages(db_, language_id = lang_obj.languageId)) == 0:
        raise NotAvailableException("Language id %s not found"%(lang_obj.languageId))
    return {'message': "Language edited successfully",
        "data": structurals_crud.update_language(db_=db_, lang=lang_obj)}

# ################################


########### Licenses ######################
@app.get('/v2/licenses',
    response_model=List[schemas.LicenseResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Licenses"])
def get_license(license_code : schemas.LicenseCodePattern=Query(None, example="CC-BY-SA"), #pylint: disable=too-many-arguments
    license_name: str=Query(None, example="Creative Commons License"),
    permission: schemas.LicensePermisssion=Query(None, example="Commercial_use"),
    active: bool=Query(True),
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0), db_: Session=Depends(get_db)):
    '''fetches all the licenses present in the DB, their code and other details.
    * optional query parameters can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_license')
    log.debug('license_code:%s, license_name: %s, permission:%s, active:%s, skip: %s, limit: %s',
        license_code, license_name, permission, active, skip, limit)
    return structurals_crud.get_licenses(db_, license_code, license_name, permission,
        active, skip = skip, limit = limit)

@app.post('/v2/licenses', response_model=schemas.LicenseCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Licenses"])
def add_license(license_obj : schemas.LicenseCreate = Body(...), db_: Session = Depends(get_db)):
    ''' Uploads a new license. License code provided will be used as the unique identifier.'''
    log.info('In add_license')
    log.debug('license_obj: %s',license_obj)
    return {'message': "License uploaded successfully",
        "data": structurals_crud.create_license(db_, license_obj, user_id=None)}

@app.put('/v2/licenses', response_model=schemas.LicenseUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Licenses"])
def edit_license(license_obj: schemas.LicenseEdit = Body(...), db_: Session = Depends(get_db)):
    ''' Changes one or more fields of license.
    Item identifier is license code, which cannot be altered.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_license')
    log.debug('license_obj: %s',license_obj)
    return {'message': "License edited successfully",
        "data": structurals_crud.update_license(db_=db_, license_obj=license_obj, user_id=None)}

##### Version #####

@app.get('/v2/versions',
    response_model=List[schemas.VersionResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Versions"])
def get_version(version_abbreviation : schemas.VersionPattern = Query(None, example="KJV"), #pylint: disable=too-many-arguments
    version_name: str = Query(None, example="King James Version"), revision : int = Query(None),
    metadata: schemas.MetaDataPattern = Query(None, example='{"publishedIn":"1611"}'),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0), db_: Session = Depends(get_db)):
    '''Fetches all versions and their details.
    * optional query parameters can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_version')
    log.debug('version_abbreviation:%s, skip: %s, limit: %s',
        version_abbreviation, skip, limit)
    return structurals_crud.get_versions(db_, version_abbreviation,
        version_name, revision, metadata, skip = skip, limit = limit)

@app.post('/v2/versions', response_model=schemas.VersionCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Versions"])
def add_version(version_obj : schemas.VersionCreate = Body(...),
    db_: Session = Depends(get_db)):
    ''' Creates a new version. Version code provided will be used as unique identifier'''
    log.info('In add_version')
    log.debug('version_obj: %s',version_obj)
    if not version_obj.revision:
        version_obj.revision = 1
    if len(structurals_crud.get_versions(db_, version_obj.versionAbbreviation,
        revision =version_obj.revision)) > 0:
        raise AlreadyExistsException("%s, %s already present"%(
            version_obj.versionAbbreviation, version_obj.revision))
    return {'message': "Version created successfully",
    "data": structurals_crud.create_version(db_=db_, version=version_obj)}


@app.put('/v2/versions', response_model=schemas.VersionUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Versions"])
def edit_version(ver_obj: schemas.VersionEdit = Body(...), db_: Session = Depends(get_db)):
    ''' Changes one or more fields of version types table.
    Item identifier is version id.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_version')
    log.debug('ver_obj: %s',ver_obj)
    if len(structurals_crud.get_versions(db_, version_id = ver_obj.versionId)) == 0:
        raise NotAvailableException("Version id %s not found"%(ver_obj.versionId))
    return {'message': "Version edited successfully",
    "data": structurals_crud.update_version(db_=db_, version=ver_obj)}

# ##### Source #####
@app.get('/v2/sources',
    response_model=List[schemas.SourceResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Sources"])
def get_source(content_type: str=Query(None, example="commentary"), #pylint: disable=too-many-arguments
    version_abbreviation: schemas.VersionPattern=Query(None,example="KJV"),
    revision: int=Query(None, example=1),
    language_code: schemas.LangCodePattern=Query(None,example="eng"),
    license_code: schemas.LicenseCodePattern=Query(None,example="ISC"),
    metadata: schemas.MetaDataPattern=Query(None,
        example='{"otherName": "KJBC, King James Bible Commentaries"}'),
    active: bool = True, latest_revision: bool = True,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0), db_: Session = Depends(get_db)):
    '''Fetches all sources and their details.
    * optional query parameters can be used to filter the result set
    * If revision is not explictly set or latest_revision is not set to False,
    then only the highest number revision from the avaliable list in each version would be returned.
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_source')
    log.debug('contentType:%s, versionAbbreviation: %s, revision: %s, languageCode: %s,\
        license_code:%s, metadata: %s, latest_revision: %s, active: %s, skip: %s, limit: %s',
        content_type, version_abbreviation, revision, language_code, license_code, metadata,
        latest_revision, active, skip, limit)
    return structurals_crud.get_sources(db_, content_type, version_abbreviation, revision,
        language_code, license_code, metadata, latest_revision=latest_revision, active=active,
        skip=skip, limit=limit)

@app.post('/v2/sources', response_model=schemas.SourceCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Sources"])
def add_source(source_obj : schemas.SourceCreate = Body(...),
    db_: Session = Depends(get_db)):
    ''' Creates a new source entry in sources table.
    Also creates all associtated tables for the content type.
    The required content type, version, language and license should be present in DB,
    if not create them first.
    Revision, if not provided, will be assumed as 1
    '''
    log.info('In add_source')
    log.debug('source_obj: %s',source_obj)
    if not source_obj.revision:
        source_obj.revision = 1
    table_name = source_obj.language + "_" + source_obj.version + "_" +\
    source_obj.revision + "_" + source_obj.contentType
    if len(structurals_crud.get_sources(db_, table_name = table_name)) > 0:
        raise AlreadyExistsException("%s already present"%table_name)
    return {'message': "Source created successfully",
    "data": structurals_crud.create_source(db_=db_, source=source_obj, table_name=table_name,
        user_id=None)}


@app.put('/v2/sources', response_model=schemas.SourceUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Sources"])
def edit_source(source_obj: schemas.SourceEdit = Body(...), db_: Session = Depends(get_db)):
    ''' Changes one or more fields of source. Item identifier is source_name.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_source')
    log.debug('source_obj: %s',source_obj)
    if len(structurals_crud.get_sources(db_, table_name = source_obj.sourceName)) == 0:
        raise NotAvailableException("Source %s not found"%(source_obj.sourceName))
    return {'message': "Source edited successfully",
    "data": structurals_crud.update_source(db_=db_, source=source_obj, user_id=None)}

# # #################

# ############ Bible Books ##########


@app.get('/v2/lookup/bible/books',
    response_model=List[schemas.BibleBook],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Lookups"])
def get_bible_book(book_id: int=Query(None, example=67), #pylint: disable=too-many-arguments
    book_code: schemas.BookCodePattern=Query(None,example='rev'),
    book_name: str=Query(None, example="Revelation"),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0), db_: Session = Depends(get_db)):
    ''' returns the list of book ids, codes and names.
    * optional query parameters can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_bible_book')
    log.debug('book_id: %s, book_code: %s, book_name: %s, skip: %s, limit: %s',
        book_id, book_code, book_name, skip, limit)
    return structurals_crud.get_bible_books(db_, book_id, book_code, book_name,
        skip = skip, limit = limit)

# #### Bible #######


@app.post('/v2/bibles/{source_name}/books', response_model=schemas.BibleBookCreateResponse,
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bibles"])
def add_bible_book(source_name : schemas.TableNamePattern=Path(..., example="hin_IRV_1_bible"),
    books: List[schemas.BibleBookUpload] = Body(...), db_: Session = Depends(get_db)):
    '''Uploads a bible book. It update 2 tables: ..._bible, .._bible_cleaned.
    The JSON provided should be generated from the USFM, using usfm-grammar 2.0.0-beta.8 or above'''
    log.info('In add_bible_book')
    log.debug('source_name: %s, books: %s',source_name, books)
    return {'message': "Bible books uploaded and processed successfully",
        "data": contents_crud.upload_bible_books(db_=db_, source_name=source_name,
        books=books, user_id=None)}


@app.put('/v2/bibles/{source_name}/books', response_model=schemas.BibleBookUpdateResponse,
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bibles"])
def edit_bible_book(source_name: schemas.TableNamePattern=Path(..., example="hin_IRV_1_bible"),
    books: List[schemas.BibleBookEdit] = Body(...), db_: Session = Depends(get_db)):
    '''Either changes the active status or the bible contents.
    * Active field can be used to activate or deactivate a content. For which,
    Item identifier is book code.
    Deactivated items are not included in normal fetch results if not specified otherwise
    * In the second case, the two fields, usfm and json,  are mandatory as they are interdependant.
    Contents of the respective bible_clean and bible_tokens tables
    are deleted and new data added, which changes the results of /v2/bibles/{source_name}/verses
    and tokens apis aswell.'''
    log.info('In edit_bible_book')
    log.debug('source_name: %s, books: %s',source_name, books)
    return {'message': "Bible books updated successfully",
        "data": contents_crud.update_bible_books(db_=db_, source_name=source_name,
        books=books, user_id=None)}

@app.get('/v2/bibles/{source_name}/books',
    response_model=List[schemas.BibleBookContent],
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Bibles"])
def get_available_bible_book(source_name: schemas.TableNamePattern=Path(..., #pylint: disable=too-many-arguments
    example="hin_IRV_1_bible"),
    book_code: schemas.BookCodePattern=Query(None, example="mat"),
    content_type: schemas.BookContentType=Query(None),
    versification: bool=False, active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0), db_: Session=Depends(get_db)):
    '''Fetches all the books available(has been uploaded) in the specified bible
    * by default returns list of available(uploaded) books, without their contents
    * optional query parameters can be used to filter the result set
    * versification can be set to true if the book structure is required(list of chapters & verses)
    * returns the JSON, USFM and/or Audio contents also: if contentType is given
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_available_bible_book')
    log.debug('source_name: %s, book_code: %s, contentType: %s, versification:%s,\
        active:%s, skip: %s, limit: %s',
        source_name, book_code, content_type, versification, active, skip, limit)
    return contents_crud.get_available_bible_books(db_, source_name, book_code, content_type,
        versification, active=active, skip = skip, limit = limit)


@app.get('/v2/bibles/{source_name}/verses',
    response_model=List[schemas.BibleVerse],
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Bibles"])
def get_bible_verse(source_name: schemas.TableNamePattern=Path(..., example="hin_IRV_1_bible"), #pylint: disable=too-many-arguments
    book_code: schemas.BookCodePattern=Query(None, example="mat"),
    chapter: int=Query(None, example=1), verse: int=Query(None, example=1),
    last_verse: int=Query(None, example=15), search_phrase: str=Query(None, example='सन्‍तान'),
    active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0), db_: Session=Depends(get_db)):
    ''' Fetches the cleaned contents of bible, within a verse range, if specified.
    This API could be used for fetching,
     * all verses of a source : with out giving any query params.
     * all verses of a book: with only book_code
     * all verses of a chapter: with book_code and chapter
     * one verse: with bookCode, chapter and verse(without lastVerse).
     * any range of verses within a chapter: using verse and lastVerse appropriately
     * search for a query phrase in a bible and get matching verses: using search_phrase
     * skip=n: skips the first n objects in return list
     * limit=n: limits the no. of items to be returned to n
     * returns [] for not available content'''
    log.info('In get_bible_verse')
    log.debug('source_name: %s, book_code: %s, chapter: %s, verse:%s, last_verse:%s,\
        search_phrase:%s, active:%s, skip: %s, limit: %s',
        source_name, book_code, chapter, verse, last_verse, search_phrase, active, skip, limit)
    return contents_crud.get_bible_verses(db_, source_name, book_code, chapter, verse, last_verse,
        search_phrase, active=active, skip = skip, limit = limit)


# # ########### Audio bible ###################

@app.post('/v2/bibles/{source_name}/audios', response_model=schemas.AudioBibleCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bibles"])
def add_audio_bible(source_name : schemas.TableNamePattern=Path(..., example="hin_IRV_1_bible"),
    audios: List[schemas.AudioBibleUpload] = Body(...), db_: Session = Depends(get_db)):
    '''uploads audio(links and related info, not files) for a bible'''
    log.info('In add_audio_bible')
    log.debug('source_name: %s, audios: %s',source_name, audios)
    return {'message': "Bible audios details uploaded successfully",
        "data": contents_crud.upload_bible_audios(db_=db_, source_name=source_name,
        audios=audios, user_id=None)}


@app.put('/v2/bibles/{source_name}/audios', response_model=schemas.AudioBibleUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bibles"])
def edit_audio_bible(source_name: schemas.TableNamePattern=Path(..., example="hin_IRV_1_bible"),
    audios: List[schemas.AudioBibleEdit] = Body(...), db_: Session = Depends(get_db)):
    ''' Changes the mentioned fields of audio bible row.
    book codes are used to identify items and at least one is mandatory.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_audio_bible')
    log.debug('source_name: %s, audios: %s',source_name, audios)
    return {'message': "Bible audios details updated successfully",
        "data": contents_crud.update_bible_audios(db_=db_, source_name=source_name,
        audios=audios, user_id=None)}

# # ##### Commentary #####

@app.get('/v2/commentaries/{source_name}',
    response_model=List[schemas.CommentaryResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Commentaries"])
def get_commentary(#pylint: disable=too-many-arguments
    source_name: schemas.TableNamePattern=Path(..., example="eng_BBC_1_commentary"),
    book_code: schemas.BookCodePattern=Query(None, example="1ki"),
    chapter: int = Query(None, example=10, ge=-1), verse: int = Query(None, example=1, ge=-1),
    last_verse: int = Query(None, example=3, ge=-1), active: bool = True,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0), db_: Session = Depends(get_db)):
    '''Fetches commentries under the specified source.
    * optional query parameters can be used to filter the result set
    * Using the params bookCode, chapter, and verse the result set can be filtered as per need,
    like in the /v2/bibles/{sourceName}/verses API
    * Value 0 for verse and last_verse indicate chapter introduction and -1 indicate
    chapter epilogue.
    * Similarly 0 for chapter means book introduction and -1 for chapter means book epilogue
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_commentary')
    log.debug('source_name: %s, book_code: %s, chapter: %s, verse:%s,\
        last_verse:%s, skip: %s, limit: %s',
        source_name, book_code, chapter, verse, last_verse, skip, limit)
    return contents_crud.get_commentaries(db_, source_name, book_code, chapter, verse, last_verse,
        active=active, skip = skip, limit = limit)

@app.post('/v2/commentaries/{source_name}', response_model=schemas.CommentaryCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Commentaries"])
def add_commentary(source_name : schemas.TableNamePattern=Path(...,example="eng_BBC_1_commentary"),
    commentaries: List[schemas.CommentaryCreate] = Body(...), db_: Session = Depends(get_db)):
    '''Uploads a list of commentaries.
    * Duplicate commentries are allowed for same verses,
    unless they have excalty same values for reference range.
    That is, if commentary is present for (gen, 1, 1-10) and
    new entries are made for (gen, 1, 1-20)
    or (gen, 1, 5-10), they will be accepted and added to DB
    * Value 0 for verse and last_verse indicate chapter introduction and
    -1 indicate chapter epilogue.
    * Similarly 0 for chapter means book introduction and -1 for chapter means book epilogue,
    verses fields can be null in these cases'''
    log.info('In add_commentary')
    log.debug('source_name: %s, commentaries: %s',source_name, commentaries)
    return {'message': "Commentaries added successfully",
    "data": contents_crud.upload_commentaries(db_=db_, source_name=source_name,
        commentaries=commentaries, user_id=None)}


@app.put('/v2/commentaries/{source_name}', response_model=schemas.CommentaryUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Commentaries"])
def edit_commentary(source_name: schemas.TableNamePattern=Path(..., example="eng_BBC_1_commentary"),
    commentaries: List[schemas.CommentaryEdit] = Body(...), db_: Session = Depends(get_db)):
    ''' Changes the commentary field to the given value in the row selected using
    book, chapter, verseStart and verseEnd values.
    Also active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_commentary')
    log.debug('source_name: %s, commentaries: %s',source_name, commentaries)
    return {'message': "Commentaries updated successfully",
    "data": contents_crud.update_commentaries(db_=db_, source_name=source_name,
        commentaries=commentaries, user_id=None)}

# # ########### Dictionary ###################

@app.get('/v2/dictionaries/{source_name}',
    response_model_exclude_unset=True,
    response_model=List[schemas.DictionaryWordResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Dictionaries"])
def get_dictionary_word( #pylint: disable=too-many-arguments
    source_name: schemas.TableNamePattern=Path(...,example="eng_TW_1_dictionary"),
    search_word: str=Query(None, example="Adam"),
    exact_match: bool=False, word_list_only: bool=False,
    details: schemas.MetaDataPattern=Query(None, example='{"type":"person"}'), active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0), db_: Session=Depends(get_db)):
    '''fetches list of dictionary words and all available details about them.
    Using the searchIndex appropriately, it is possible to get
    * All words starting with a letter
    * All words starting with a substring
    * An exact word search, giving the whole word and setting exactMatch to True
    * Based on any key value pair in details, which should be specified as a dict/JSON like string
    * By setting the wordListOnly flag to True, only the words would be included
     in the return object, without the details
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_dictionary_word')
    log.debug('source_name: %s, search_word: %s, exact_match: %s, word_list_only:%s, details:%s\
        skip: %s, limit: %s', source_name, search_word, exact_match, word_list_only, details,
        skip, limit)
    return contents_crud.get_dictionary_words(db_, source_name, search_word,
        exact_match=exact_match,
        word_list_only=word_list_only, details=details, active=active, skip=skip, limit=limit)


@app.post('/v2/dictionaries/{source_name}', response_model=schemas.DictionaryCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Dictionaries"])
def add_dictionary_word(
    source_name : schemas.TableNamePattern=Path(..., example="eng_TW_1_dictionary"),
    dictionary_words: List[schemas.DictionaryWordCreate] = Body(...),
    db_: Session = Depends(get_db)):
    ''' uploads dictionay words and their details. 'Details' should be of JSON datatype and  have
    all the additional info we have for each word, as key-value pairs.
    The word will serve as the unique identifier'''
    log.info('In add_dictionary_word')
    log.debug('source_name: %s, dictionary_words: %s',source_name, dictionary_words)
    return {'message': "Dictionary words added successfully",
        "data": contents_crud.upload_dictionary_words(db_=db_, source_name=source_name,
        dictionary_words=dictionary_words, user_id=None)}


@app.put('/v2/dictionaries/{source_name}', response_model=schemas.DictionaryUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Dictionaries"])
def edit_dictionary_word(
    source_name: schemas.TableNamePattern=Path(..., example="eng_TW_1_dictionary"),
    dictionary_words: List[schemas.DictionaryWordEdit] = Body(...),
    db_: Session = Depends(get_db)):
    ''' Updates a dictionary word. Item identifier is word, which cannot be altered.
    * Updates all the details, of the specifed word, if details is provided.
    * Active field can be used to activate or deactivate a word.
    Deactivated words are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_dictionary_word')
    log.debug('source_name: %s, dictionary_words: %s',source_name, dictionary_words)
    return {'message': "Dictionary words updated successfully",
        "data": contents_crud.update_dictionary_words(db_=db_, source_name=source_name,
        dictionary_words=dictionary_words, user_id=None)}

# # ###########################################

# # ########### Infographic ###################

@app.get('/v2/infographics/{source_name}',
    response_model=List[schemas.InfographicResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Infographics"])
def get_infographic(#pylint: disable=too-many-arguments
    source_name:schemas.TableNamePattern=Path(...,example="hin_IRV_1_infographic"),
    book_code: schemas.BookCodePattern=Query(None, example="exo"),
    title: str=Query(None, example="Ark of Covenant"), active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0), db_: Session=Depends(get_db)):
    '''Fetches the infographics. Can use, bookCode and/or title to filter the results
    * optional query parameters can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_infographic')
    log.debug('source_name: %s, book_code: %s skip: %s, limit: %s',
        source_name, book_code, skip, limit)
    return contents_crud.get_infographics(db_, source_name, book_code, title,
        active=active, skip = skip, limit = limit)

@app.post('/v2/infographics/{source_name}', response_model=schemas.InfographicCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Infographics"])
def add_infographics(source_name : schemas.TableNamePattern=Path(...,
    example="hin_IRV_1_infographic"),
    infographics: List[schemas.InfographicCreate] = Body(...), db_: Session = Depends(get_db)):
    '''Uploads a list of infograhics. BookCode and title provided, serves as the unique idetifier
    Only the  link to infographic is stored, not the actual file'''
    log.info('In add_infographics')
    log.debug('source_name: %s, infographics: %s',source_name, infographics)
    return {'message': "Infographics added successfully",
        "data": contents_crud.upload_infographics(db_=db_, source_name=source_name,
        infographics=infographics, user_id=None)}

@app.put('/v2/infographics/{source_name}', response_model=schemas.InfographicUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Infographics"])
def edit_infographics(source_name: schemas.TableNamePattern=Path(...,
    example="hin_IRV_1_infographic"),
    infographics: List[schemas.InfographicEdit] = Body(...),
    db_: Session = Depends(get_db)):
    ''' Changes either the infographic link or active status.
    Item identifier is book code and title, which cannot be altered.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_infographics')
    log.debug('source_name: %s, infographics: %s',source_name, infographics)
    return {'message': "Infographics updated successfully",
        "data": contents_crud.update_infographics(db_=db_, source_name=source_name,
        infographics=infographics, user_id=None)}
# # ###########################################


# # ########### bible videos ###################

@app.get('/v2/biblevideos/{source_name}',
    response_model=List[schemas.BibleVideo],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Bible Videos"])
def get_biblevideo(#pylint: disable=too-many-arguments
    source_name:schemas.TableNamePattern=Path(...,example="eng_TBP_1_biblevideo"),
    book_code: schemas.BookCodePattern=Query(None, example="sng"),
    title: str=Query(None, example="Overview: song of songs"),
    theme: str=Query(None, example="Old Testament"), active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0), db_: Session=Depends(get_db)):
    '''Fetches the Bible video details and URL.
    * optional query parameters can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_biblevideo')
    log.debug('source_name: %s, book_code: %s, title: %s, theme: %s, skip: %s, limit: %s',
        source_name, book_code, title, theme, skip, limit)
    return contents_crud.get_bible_videos(db_, source_name, book_code, title, theme, active,
        skip=skip, limit=limit)


@app.post('/v2/biblevideos/{source_name}', response_model=schemas.BibleVideoCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bible Videos"])
def add_biblevideo(source_name:schemas.TableNamePattern=Path(...,example="eng_TBP_1_biblevideo"),
    videos: List[schemas.BibleVideoUpload] = Body(...), db_: Session = Depends(get_db)):
    '''Uploads a list of bible video links and details.
    Provided title will serve as the unique identifier'''
    log.info('In add_biblevideo')
    log.debug('source_name: %s, videos: %s',source_name, videos)
    return {'message': "Bible videos added successfully",
        "data": contents_crud.upload_bible_videos(db_=db_, source_name=source_name,
        videos=videos, user_id=None)}


@app.put('/v2/biblevideos/{source_name}', response_model=schemas.BibleVideoUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bible Videos"])
def edit_biblevideo(source_name:schemas.TableNamePattern=Path(...,example="eng_TBP_1_biblevideo"),
    videos: List[schemas.BibleVideoEdit] = Body(...),
    db_: Session = Depends(get_db)):
    ''' Changes the selected rows of bible videos table.
    Item identified by title, which cannot be altered.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_biblevideo')
    log.debug('source_name: %s, videos: %s',source_name, videos)
    return {'message': "Bible videos updated successfully",
        "data": contents_crud.update_bible_videos(db_=db_, source_name=source_name,
        videos=videos, user_id=None)}
# # ###########################################

########### Generic Translation ##################
#pylint: disable=all

@app.put('/v2/translation/tokens', response_model=List[schemas_nlp.Token],
    status_code=200, tags=['Generic Translation'])
def tokenize(source_language:schemas.LangCodePattern=Query(...,example="hin"),
    sentence_list:List[schemas_nlp.SentenceInput]=Body(...),
    target_language:schemas.LangCodePattern=Query(None,example="mal"),
    use_translation_memory:bool=True, include_phrases:bool=True, include_stopwords:bool=False,
    punctuations:List[str]=Body(None), stopwords:schemas_nlp.Stopwords=Body(None),
    db_:Session=Depends(get_db)):
    '''Tokenize any set of input sentences.
    Makes use of translation memory and stopwords for forming better phrase tokens.
    Flags use_translation_memory, include_phrases and include_stopwords can be
    used to alter the tokens output as per user need'''
    log.info('In tokenize')
    log.debug('source_language: %s, sentence_list:%s, target_language:%s, punctuations:%s,'+
        'stopwords:%s, use_translation_memory:%s, include_phrases:%s, include_stopwords:%s',
        source_language, sentence_list, target_language, punctuations, stopwords,
        use_translation_memory, include_phrases, include_stopwords)
    return nlp_crud.get_generic_tokens(db_, source_language, sentence_list, target_language,
        punctuations, stopwords, use_translation_memory, include_phrases, include_stopwords)


@app.put('/v2/translation/token-translate', response_model=schemas_nlp.TranslateResponse,
    status_code=200, tags=['Generic Translation'])
def token_replace(sentence_list:List[schemas_nlp.DraftInput]=Body(...),
    token_translations:List[schemas_nlp.TokenUpdate]=Body(...),
    source_language:schemas.LangCodePattern=Query(...,example='hin'),
    target_language:schemas.LangCodePattern=Query(...,example='mal'),
    use_data_for_learning:bool=True, db_:Session=Depends(get_db)):
    '''Perform token replacement on provided sentences and 
    returns obtained drafts and draft_meta'''
    log.info('In token_replace')
    log.debug('sentence_list:%s, token_translations:%s,'+
        'source_lanuage:%s, target_language:%s, use_data_for_learning:%s',
        sentence_list, token_translations, source_language, target_language, use_data_for_learning)
    result = nlp_crud.replace_bulk_tokens(db_, sentence_list, token_translations, source_language,
        target_language, use_data_for_learning)
    return {"message": "Tokens replaced with translations", "data": result}

@app.put('/v2/translation/suggestions', response_model=List[schemas_nlp.Sentence],
    status_code=200, tags=['Generic Translation'])
def suggest_translation(source_language:schemas.LangCodePattern=Query(...,example="hin"),
    target_language:schemas.LangCodePattern=Query(...,example="mal"),
    sentence_list:List[schemas_nlp.DraftInput]=Body(...),
    punctuations:List[str]=Body(None), stopwords:schemas_nlp.Stopwords=Body(None),
    db_:Session=Depends(get_db)):
    '''Attempts to tokenize sentences and prepare draft with autogenerated suggestions
    If draft and draft_meta are provided indicating some portion of sentence is user translated, 
    then it is left untouched.'''
    log.info("In suggest_translation")
    log.debug('source_language:%s, target_language:%s, sentence_list:%s,punctuations:%s'+
        'stopwords:%s', source_language, target_language, sentence_list, punctuations, stopwords)
    return nlp_crud.auto_translate(db_, sentence_list, source_language, target_language,
        punctuations, stopwords)

@app.get('/v2/translation/gloss', response_model=List[schemas_nlp.Suggestion],
    status_code=200, tags=['Generic Translation'])
def get_glossary(source_language:schemas.LangCodePattern=Query(...,example="eng"),
    target_language:schemas.LangCodePattern=Query(...,example="hin"),
    token:str=Query(...,example="duck"),
    context:str=Query(None,example="The duck swam in the lake"),
    token_offset:List[int]=Query(None,max_items=2,min_items=2,example=(4,8)),
    db_:Session=Depends(get_db)):
    '''Finds translation suggestions or gloss for one token in the given context'''
    log.info('In get_glossary')
    log.debug('source_language:%s, target_language:%s, token:%s, context:%s,'+
        'token_offset:%s',source_language, target_language, token,
            context, token_offset)
    return nlp_crud.glossary(db_, source_language, target_language, token, context, token_offset)


@app.put('/v2/translation/draft', status_code=200, tags=['Generic Translation'])
def generate_draft(sentence_list:List[schemas_nlp.DraftInput]=Body(...),
    doc_type:schemas_nlp.TranslationDocumentType=Query(schemas_nlp.TranslationDocumentType.USFM)):
    '''Converts the drafts in input sentences to following output formats:
    usfm, text, csv or alignment-json'''
    log.info('In generate_draft')
    log.debug('sentence_list:%s, doc_type:%s',sentence_list, doc_type)
    return nlp_crud.obtain_draft(sentence_list, doc_type)

@app.post('/v2/translation/learn/gloss', response_model=schemas_nlp.GlossUpdateResponse,
    status_code=201, tags=['Generic Translation'])
def add_gloss(source_language:schemas.LangCodePattern, target_language:schemas.LangCodePattern,
    token_translations:List[schemas_nlp.GlossInput], db_:Session=Depends(get_db)):
    '''Load a list of predefined tokens and translations to improve tokenization and suggestion'''
    log.info('In add_gloss')
    log.debug('source_language:%s, target_language:%s, token_translations:%s',
        source_language, target_language, token_translations)
    tw_data = nlp_crud.add_to_translation_memory(db_,source_language, target_language,
        token_translations)
    return { "message": "Added to glossary", "data":tw_data }

@app.post('/v2/translation/learn/alignment', response_model=schemas_nlp.GlossUpdateResponse,
    status_code=201, tags=['Generic Translation'])
def add_alignments(source_language:schemas.LangCodePattern, target_language:schemas.LangCodePattern,
    alignments:List[schemas_nlp.Alignment], db_:Session=Depends(get_db)):
    '''Prepares training data with the alignments and update translation memory and suggestion models'''
    log.info('In add_alignments')
    log.debug('source_language:%s, target_language:%s, alignments:%s',
        source_language, target_language, alignments)
    tw_data = nlp_crud.alignments_to_trainingdata(db_,source_language, target_language,
        alignments, user_id=20202)
    return { "message": "Alignments used for learning", "data":tw_data }
############## Autographa Projects ##########################

@app.get('/v2/autographa/projects', response_model=List[schemas_nlp.TranslationProject],
    status_code=200, tags=['Autographa-Project management'])
def get_projects(project_name:str=Query(None,example="Hindi-Bilaspuri Gospels"),
    source_language:schemas.LangCodePattern=Query(None,example='eng'),
    target_language:schemas.LangCodePattern=Query(None,example='mal'),
    active:bool=True, user_id:int=Query(None), db_:Session=Depends(get_db)):
    '''Fetches the list of proejct and their details'''
    log.info('In get_projects')
    log.debug('project_name: %s, source_language:%s, target_language:%s,'+
        'active:%s, user_id:%s',project_name, source_language, target_language, active, user_id)
    return nlp_crud.get_agmt_projects(db_, project_name, source_language, target_language, active, user_id)

@app.post('/v2/autographa/projects', status_code=201,
    response_model=schemas_nlp.TranslationProjectUpdateResponse, tags=['Autographa-Project management'])
def create_project(project_obj:schemas_nlp.TranslationProjectCreate, db_:Session=Depends(get_db)):
    '''Creates a new autographa MT project'''
    log.info('In create_project')
    log.debug('project_obj: %s',project_obj)
    return {'message': "Project created successfully",
        "data": nlp_crud.create_agmt_project(db_=db_, project=project_obj, user_id=10101)}

@app.put('/v2/autographa/projects', status_code=201,
    response_model=schemas_nlp.TranslationProjectUpdateResponse, tags=['Autographa-Project management'])
def update_project(project_obj:schemas_nlp.TranslationProjectEdit, db_:Session=Depends(get_db)):
    '''Adds more books to a autographa MT project's source. Delete or activate project.'''
    log.info('In update_project')
    log.debug('project_obj: %s',project_obj)
    return {'message': "Project updated successfully",
        "data": nlp_crud.update_agmt_project(db_, project_obj, user_id=10101)}

@app.post('/v2/autographa/project/user', status_code=201,
    response_model=schemas_nlp.UserUpdateResponse, tags=['Autographa-Project management'])
def add_user(project_id:int, user_id:int, db_:Session=Depends(get_db)):
    '''Adds new user to a project.'''
    log.info('In add_user')
    log.debug('project_id: %s, user_id:%s',project_id, user_id)
    return {'message': "User added to project successfully",
        "data": nlp_crud.add_agmt_user(db_, project_id, user_id, current_user=10101)}

@app.put('/v2/autographa/project/user', status_code=201,
    response_model=schemas_nlp.UserUpdateResponse, tags=['Autographa-Project management'])
def update_user(user_obj:schemas_nlp.ProjectUser, db_:Session=Depends(get_db)):
    '''Changes role, metadata or active status of user of a project.'''
    log.info('In update_user')
    log.debug('user_obj:%s',user_obj)
    return {'message': "User updated in project successfully",
        "data": nlp_crud.update_agmt_user(db_, user_obj, current_user=10101)}

############## Autographa Translations ##########################

@app.get('/v2/autographa/project/tokens', response_model=List[schemas_nlp.Token],
    status_code=200, tags=['Autographa-Translation'])
def get_tokens(project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=(410010001, 41001999)),
    sentence_id_list:List[int]=Query(None, example=[41001001,41001002,41001003]),
    use_translation_memory:bool=True, include_phrases:bool=True, include_stopwords:bool=False,
    db_:Session=Depends(get_db)):
    '''Tokenize the source texts. Optional params books, sentence_id_range or sentence_id_list can be used 
    to specify the source verses. If more than one of these filters are given, only one would be used
    in the following order of priority: books, range, list.
    Flags use_translation_memory, include_phrases and include_stopwords can be
    used to alter the tokens output as per user need'''
    log.info('In get_tokens')
    log.debug('project_id: %s, books:%s, sentence_id_range:%s, sentence_id_list:%s'+
        'use_translation_memory:%s, include_phrases:%s, include_stopwords:%s',
        project_id, books, sentence_id_range, sentence_id_range, use_translation_memory,
        include_phrases, include_stopwords)
    return nlp_crud.get_agmt_tokens(db_, project_id, books, sentence_id_range, sentence_id_list,
        use_translation_memory, include_phrases, include_stopwords)

@app.put('/v2/autographa/project/tokens', response_model=schemas_nlp.TranslateResponse,
    status_code=201, tags=['Autographa-Translation'])
def apply_token_translations(project_id:int=Query(...,example="1022004"),
    token_translations:List[schemas_nlp.TokenUpdate]=Body(...), return_drafts:bool=True,
    db_:Session=Depends(get_db)):
    '''Updates drafts using the provided token translations and returns updated verses'''
    log.info('In apply_token_translations')
    log.debug('project_id: %s, token_translations:%s, ',project_id, token_translations)
    drafts = nlp_crud.save_agmt_translations(db_, project_id, token_translations, return_drafts,
        user_id=10101)
    return {"message": "Token translations saved", "data":drafts}

@app.get('/v2/autographa/project/draft', status_code=200, tags=['Autographa-Translation'])
def get_draft(project_id:int=Query(...,example="1022004"), 
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    output_format:schemas_nlp.DraftFormats=Query(schemas_nlp.DraftFormats.USFM), db_:Session=Depends(get_db)):
    '''Obtains draft, as per current project status, in any of the formats: 
    text for UI display, usfm for downloading, or alignment-json for project export'''
    log.info('In get_draft')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s,\
        output_format:%s',project_id, books, sentence_id_list, sentence_id_range,
        output_format)
    return nlp_crud.obtain_agmt_draft(db_, project_id, books, sentence_id_list, sentence_id_range,
        output_format)

@app.get('/v2/autographa/project/sentences', status_code=200,
    response_model_exclude_unset=True,
    response_model=List[schemas_nlp.Sentence], tags=['Autographa-Translation'])
def get_source(project_id:int=Query(...,example="1022004"), 
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    with_draft:bool=False, db_:Session=Depends(get_db)):
    '''Obtains source sentences or verses, as per the filters'''
    log.info('In get_source')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s, with_draft:%s',
        project_id, books, sentence_id_list, sentence_id_range, with_draft)
    return nlp_crud.obtain_agmt_source(db_, project_id, books, sentence_id_list, sentence_id_range,
        with_draft)

@app.get('/v2/autographa/project/progress', status_code=200,
    response_model=schemas_nlp.Progress, tags=['Autographa-Translation'])
def get_progress(project_id:int=Query(...,example="1022004"), 
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    db_:Session=Depends(get_db)):
    '''Obtains source sentences or verses, as per the filters'''
    log.info('In get_progress')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s',
        project_id, books, sentence_id_list, sentence_id_range)
    return nlp_crud.obtain_agmt_progress(db_, project_id, books, sentence_id_list, sentence_id_range)

@app.put('/v2/autographa/project/suggestions', status_code=200,
    response_model=List[schemas_nlp.Sentence], tags=['Autographa-Translation'])
def suggest_translation(project_id:int=Query(...,example="1022004"), 
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    confirm_all:bool=False, db_:Session=Depends(get_db)):
    '''Try to fill draft with suggestions. If confirm_all is set, will only change status of all
    "suggestion" to "confirmed" in the selected sentences and will not fill in new suggestion'''
    log.info('In suggest_translation')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s',
        project_id, books, sentence_id_list, sentence_id_range)
    return nlp_crud.agmt_suggest_translations(db_, project_id, books, sentence_id_list, sentence_id_range,
        confirm_all)
