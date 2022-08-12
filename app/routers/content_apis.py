'''API endpoints related to content management'''
import json
from typing import List
from fastapi import APIRouter, Query, Body, Depends, Path , Request,\
    BackgroundTasks
from sqlalchemy.orm import Session
import db_models
from schema import schemas,schemas_nlp, schema_auth, schema_content
from dependencies import get_db, log, AddHiddenInput
from crud import structurals_crud, contents_crud, nlp_sw_crud, media_crud
from custom_exceptions import NotAvailableException, AlreadyExistsException,\
    UnprocessableException

from auth.authentication import get_auth_access_check_decorator ,\
    get_user_or_none

router = APIRouter()

#pylint: disable=too-many-arguments,unused-argument
##### Content types #####
@router.get('/v2/contents', response_model=List[schemas.ContentType],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}},  status_code=200,
    tags=["Contents Types"])
@get_auth_access_check_decorator
async def get_contents(request: Request,content_type: str = Query(None, example="bible"),
     skip: int = Query(0, ge=0),limit: int = Query(100, ge=0),
     user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    '''fetches all the contents types supported and their details
    * the optional query parameter can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n'''
    log.info('In get_contents')
    log.debug('contentType:%s, skip: %s, limit: %s',content_type, skip, limit)
    return structurals_crud.get_content_types(db_, content_type, skip, limit)

@router.post('/v2/contents', response_model=schemas.ContentTypeUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Contents Types"])
@get_auth_access_check_decorator
async def add_contents(request: Request, content: schemas.ContentTypeCreate,
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
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
    data = structurals_crud.create_content_type(db_=db_, content=content)
    return {'message': "Content type created successfully",
            "data": data}

##### languages #####
@router.get('/v2/languages',
    response_model=List[schemas.LanguageResponse],
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Languages"])
@get_auth_access_check_decorator
async def get_language(request: Request,
    language_code : schemas.LangCodePattern = Query(None, example="hi"),
    language_name: str = Query(None, example="hindi"),
    search_word: str = Query(None, example="Sri Lanka"),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    '''fetches all the languages supported in the DB, their code and other details.
    * if any of the optional query parameters are provided, returns details of that language
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_language')
    log.debug('langauge_code:%s, language_name: %s, search_word:%s, skip: %s, limit: %s',
        language_code, language_name, search_word, skip, limit)
    return structurals_crud.get_languages(db_, language_code, language_name, search_word,
        skip = skip, limit = limit)

@router.post('/v2/languages', response_model=schemas.LanguageCreateResponse,
    responses={502: {"model":schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Languages"])
@get_auth_access_check_decorator
async def add_language(request: Request, lang_obj : schemas.LanguageCreate = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    ''' Creates a new language. Langugage code should of 3 letters which uniquely identifies it.'''
    log.info('In add_language')
    log.debug('lang_obj: %s',lang_obj)
    if len(structurals_crud.get_languages(db_, language_code = lang_obj.code)) > 0:
        raise AlreadyExistsException("%s already present"%(lang_obj.code))
    return {'message': "Language created successfully",
        "data": structurals_crud.create_language(db_=db_, lang=lang_obj,
        user_id=user_details['user_id'])}

@router.put('/v2/languages', response_model=schemas.LanguageUpdateResponse,
    responses={502:{"model":schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Languages"])
@get_auth_access_check_decorator
async def edit_language(request: Request, lang_obj: schemas.LanguageEdit = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    ''' Changes one or more fields of language'''
    log.info('In edit_language')
    log.debug('lang_obj: %s',lang_obj)
    if len(structurals_crud.get_languages(db_, language_id = lang_obj.languageId)) == 0:
        raise NotAvailableException("Language id %s not found"%(lang_obj.languageId))
    return {'message': "Language edited successfully",
            "data": structurals_crud.update_language(db_=db_, lang=lang_obj,
            user_id=user_details['user_id'])}

########### Licenses ######################
@router.get('/v2/licenses',
    response_model=List[schemas.LicenseResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Licenses"])
@get_auth_access_check_decorator
async def get_license(request: Request,
    license_code : schemas.LicenseCodePattern=Query(None, example="CC-BY-SA"),
    license_name: str=Query(None, example="Creative Commons License"),
    permission: schemas.SourcePermissions=Query(None, example="open-access"),
    active: bool=Query(True), skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none),db_: Session=Depends(get_db)):
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

@router.post('/v2/licenses', response_model=schemas.LicenseCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Licenses"])
@get_auth_access_check_decorator
async def add_license(request: Request, license_obj : schemas.LicenseCreate = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    ''' Uploads a new license. License code provided will be used as the unique identifier.'''
    log.info('In add_license')
    log.debug('license_obj: %s',license_obj)
    return {'message': "License uploaded successfully",
        "data": structurals_crud.create_license(db_, license_obj, user_id=user_details['user_id'])}

@router.put('/v2/licenses', response_model=schemas.LicenseUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Licenses"])
@get_auth_access_check_decorator
async def edit_license(request: Request, license_obj: schemas.LicenseEdit = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    ''' Changes one or more fields of license.
    Item identifier is license code, which cannot be altered.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_license')
    log.debug('license_obj: %s',license_obj)
    return {'message': "License edited successfully",
        "data": structurals_crud.update_license(db_=db_, license_obj=license_obj,
        user_id=user_details['user_id'])}

##### Version #####
@router.get('/v2/versions',
    response_model=List[schemas.VersionResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Versions"])
@get_auth_access_check_decorator
async def get_version(request: Request,
    version_abbreviation : schemas.VersionPattern = Query(None, example="KJV"),
    version_name: str = Query(None, example="King James Version"), revision : int = Query(None),
    metadata: schemas.MetaDataPattern = Query(None, example='{"publishedIn":"1611"}'),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
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

@router.post('/v2/versions', response_model=schemas.VersionCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Versions"])
@get_auth_access_check_decorator
async def add_version(request: Request, version_obj : schemas.VersionCreate = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
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
        "data": structurals_crud.create_version(db_=db_, version=version_obj,
        user_id=user_details['user_id'])}

@router.put('/v2/versions', response_model=schemas.VersionUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Versions"])
@get_auth_access_check_decorator
async def edit_version(request: Request, ver_obj: schemas.VersionEdit = Body(...),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    ''' Changes one or more fields of version types table.
    Item identifier is version id.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_version')
    log.debug('ver_obj: %s',ver_obj)
    if len(structurals_crud.get_versions(db_, version_id = ver_obj.versionId)) == 0:
        raise NotAvailableException("Version id %s not found"%(ver_obj.versionId))
    return {'message': "Version edited successfully",
        "data": structurals_crud.update_version(db_=db_, version=ver_obj,
        user_id=user_details['user_id'])}

###### Source #####
@router.get('/v2/sources',
    response_model=List[schemas.SourceResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse}},
    status_code=200, tags=["Sources"])
@get_auth_access_check_decorator
async def get_source(request: Request, #pylint: disable=too-many-locals
    source_name : schemas.TableNamePattern=Query(None, example="hi_IRV_1_bible"),
    content_type: str=Query(None, example="commentary"),
    version_abbreviation: schemas.VersionPattern=Query(None,example="KJV"),
    revision: int=Query(None, example=1),
    language_code: schemas.LangCodePattern=Query(None,example="en"),
    license_code: schemas.LicenseCodePattern=Query(None,example="ISC"),
    metadata: schemas.MetaDataPattern=Query(None,
        example='{"otherName": "KJBC, King James Bible Commentaries"}'),
    access_tag:List[schemas.SourcePermissions]=Query([schemas.SourcePermissions.CONTENT]),
    active: bool = True, latest_revision: bool = True,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db),
    operates_on=Depends(AddHiddenInput(value=schema_auth.ResourceType.CONTENT.value)),
    filtering_required=Depends(AddHiddenInput(value=True))):
    '''Fetches all sources and their details.
    * optional query parameters can be used to filter the result set
    * If revision is not explictly set or latest_revision is not set to False,
    then only the highest number revision from the avaliable list in each version would be returned.
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_source')
    log.debug('sourceName:%s,contentType:%s, versionAbbreviation: %s, revision: %s, \
    languageCode: %s,license_code:%s, metadata: %s, access_tag: %s, latest_revision:\
         %s, active: %s, skip: %s, limit: %s',source_name,
        content_type, version_abbreviation, revision, language_code, license_code, metadata,
        access_tag, latest_revision, active, skip, limit)
    return structurals_crud.get_sources(db_, content_type, version_abbreviation, revision=revision,
        language_code=language_code, license_code=license_code, metadata=metadata,
        access_tag=access_tag,latest_revision=latest_revision, active=active,skip=skip, limit=limit,
        source_name=source_name)

@router.post('/v2/sources', response_model=schemas.SourceCreateResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Sources"])
@get_auth_access_check_decorator
async def add_source(request: Request, source_obj : schemas.SourceCreate = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    # user_details = Depends(auth_handler.kratos_session_validation)
    ''' Creates a new source entry in sources table.
    * Also creates all associtated tables for the content type.
    * The required content type, version, language and license should be present in DB,
    * if not create them first.
    * Revision, if not provided, will be assumed as 1
    * AccessPermissions is list of permissions ["content", "open-access", "publishable",
        "downloadable","derivable"]. Default will be ["content"]
    * repo and defaultBranch should given in the metaData if contentType is gitlabrepo,
        defaultBranch will be "main" if not mentioned in the metadata.
    '''
    log.info('In add_source')
    log.debug('source_obj: %s',source_obj)
    if not source_obj.revision:
        source_obj.revision = 1
    source_name = source_obj.language + "_" + source_obj.version + "_" +\
    source_obj.revision + "_" + source_obj.contentType
    if len(structurals_crud.get_sources(db_, source_name = source_name)) > 0:
        raise AlreadyExistsException("%s already present"%source_name)
    if 'content' not in source_obj.accessPermissions:
        source_obj.accessPermissions.append(schemas.SourcePermissions.CONTENT)
    source_obj.metaData['accessPermissions'] = source_obj.accessPermissions
    if source_obj.contentType == db_models.ContentTypeName.GITLABREPO.value:
        if "repo" not in source_obj.metaData:
            raise UnprocessableException("repo link in metadata is mandatory to create"+
                " source with contentType gitlabrepo")
        if len(structurals_crud.get_sources(db_, metadata =
                json.dumps({"repo":source_obj.metaData["repo"]}))) > 0:
            raise AlreadyExistsException("already present Source with same repo link")
        if "defaultBranch" not in source_obj.metaData:
            source_obj.metaData["defaultBranch"] = "main"
    return {'message': "Source created successfully",
    "data": structurals_crud.create_source(db_=db_, source=source_obj, source_name=source_name,
        user_id=user_details['user_id'])}

@router.put('/v2/sources', response_model=schemas.SourceUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Sources"])
@get_auth_access_check_decorator
async def edit_source(request: Request,source_obj: schemas.SourceEdit = Body(...),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    ''' Changes one or more fields of source. Item identifier is source_name.
    * Active field can be used to activate or deactivate a content.
    * Deactivated items are not included in normal fetch results if not specified otherwise
    * AccessPermissions is list of permissions ["content", "open-access", "publishable",
        "downloadable", "derivable"]. Edit accessPermission will overwrite the current list'''
    log.info('In edit_source')
    log.debug('source_obj: %s',source_obj)
    if len(structurals_crud.get_sources(db_, source_name = source_obj.sourceName)) == 0:
        raise NotAvailableException("Source %s not found"%(source_obj.sourceName))
    if 'content' not in source_obj.accessPermissions:
        source_obj.accessPermissions.append(schemas.SourcePermissions.CONTENT)
    source_obj.metaData['accessPermissions'] = source_obj.accessPermissions
    if source_obj.sourceName.split("_")[-1] == \
        db_models.ContentTypeName.GITLABREPO.value:
        if "repo" not in source_obj.metaData:
            raise UnprocessableException("repo link in metadata is mandatory to update"+
                " source with contentType gitlabrepo")
        current_source = structurals_crud.get_sources(db_, metadata =
                json.dumps({"repo":source_obj.metaData["repo"]}))
        if len(current_source)>0 and not current_source[0].sourceName ==\
             source_obj.sourceName:
            raise AlreadyExistsException("already present another source"+
            " with same repo link")
        if "defaultBranch" not in source_obj.metaData:
            source_obj.metaData["defaultBranch"] = "main"
    return {'message': "Source edited successfully",
    "data": structurals_crud.update_source(db_=db_, source=source_obj,
        user_id=user_details['user_id'])}

# ############ Bible Books ##########
@router.get('/v2/lookup/bible/books',
    response_model=List[schema_content.BibleBook],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Lookups"])
@get_auth_access_check_decorator
async def get_bible_book(request: Request,book_id: int=Query(None, example=67),
    book_code: schemas.BookCodePattern=Query(None,example='rev'),
    book_name: str=Query(None, example="Revelation"),user_details =Depends(get_user_or_none),
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
@router.post('/v2/bibles/{source_name}/books',
    response_model=schema_content.BibleBookCreateResponse,
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse},409:{"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bibles"])
@get_auth_access_check_decorator
async def add_bible_book(request: Request,
    source_name : schemas.TableNamePattern=Path(..., example="hi_IRV_1_bible"),
    books: List[schema_content.BibleBookUpload] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    '''Uploads a bible book. It update 2 tables: ..._bible, .._bible_cleaned.
    The JSON provided should be generated from the USFM, using usfm-grammar 2.0.0-beta.8 or above'''
    log.info('In add_bible_book')
    log.debug('source_name: %s, books: %s',source_name, books)
    return {'message': "Bible books uploaded and processed successfully",
        "data": contents_crud.upload_bible_books(db_=db_, source_name=source_name,
        books=books, user_id=user_details['user_id'])}

@router.put('/v2/bibles/{source_name}/books', response_model=schema_content.BibleBookUpdateResponse,
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bibles"])
@get_auth_access_check_decorator
async def edit_bible_book(request: Request,
    source_name: schemas.TableNamePattern=Path(..., example="hi_IRV_1_bible"),
    books: List[schema_content.BibleBookEdit] = Body(...),user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
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
        books=books, user_id=user_details['user_id'])}

@router.get('/v2/bibles/{source_name}/books',
    response_model=List[schema_content.BibleBookContent],
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Bibles"])
@get_auth_access_check_decorator
async def get_available_bible_book(request: Request,
    source_name: schemas.TableNamePattern=Path(...,example="hi_IRV_1_bible"),
    book_code: schemas.BookCodePattern=Query(None, example="mat"),
    content_type: schema_content.BookContentType=Query(None), active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db)):
    '''Fetches all the books available(has been uploaded) in the specified bible
    * by default returns list of available(uploaded) books, without their contents
    * optional query parameters can be used to filter the result set
    * returns the JSON, USFM and/or Audio contents also: if contentType is given
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_available_bible_book')
    log.debug('source_name: %s, book_code: %s, contentType: %s, active:%s, skip: %s, limit: %s',
        source_name, book_code, content_type, active, skip, limit)
    return contents_crud.get_available_bible_books(db_, source_name, book_code, content_type,
        active=active, skip = skip, limit = limit)

@router.get('/v2/bibles/{source_name}/versification',
    response_model= schema_content.Versification,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Bibles"])
@get_auth_access_check_decorator
async def get_bible_versification(request: Request,
    source_name:schemas.TableNamePattern=Path(..., example="hi_IRV_1_bible"),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db)):
    '''Fetches the versification structure of the specified bible,
    with details of number of chapters, max verses in each chapter etc'''
    log.info('In get_bible_versification')
    log.debug('source_name: %s',source_name)
    return contents_crud.get_bible_versification(db_, source_name)

@router.get('/v2/bibles/{source_name}/verses',
    response_model=List[schema_content.BibleVerse],
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Bibles"])
@get_auth_access_check_decorator
async def get_bible_verse(request: Request,
    source_name: schemas.TableNamePattern=Path(..., example="hi_IRV_1_bible"),
    book_code: schemas.BookCodePattern=Query(None, example="mat"),
    chapter: int=Query(None, example=1), verse: int=Query(None, example=1),
    last_verse: int=Query(None, example=15), search_phrase: str=Query(None, example='सन्‍तान'),
    active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db)):
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
    return contents_crud.get_bible_verses(db_, source_name, book_code, chapter, verse,
    last_verse = last_verse, search_phrase=search_phrase, active=active,
    skip = skip, limit = limit)

# # ########### Audio bible ###################
@router.post('/v2/bibles/{source_name}/audios',
    response_model=schema_content.AudioBibleCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bibles"])
@get_auth_access_check_decorator
async def add_audio_bible(request: Request,
    source_name : schemas.TableNamePattern=Path(..., example="hi_IRV_1_bible"),
    audios: List[schema_content.AudioBibleUpload] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    '''uploads audio(links and related info, not files) for a bible'''
    log.info('In add_audio_bible')
    log.debug('source_name: %s, audios: %s',source_name, audios)
    return {'message': "Bible audios details uploaded successfully",
        "data": contents_crud.upload_bible_audios(db_=db_, source_name=source_name,
        audios=audios, user_id=user_details['user_id'])}

@router.put('/v2/bibles/{source_name}/audios',
    response_model=schema_content.AudioBibleUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bibles"])
@get_auth_access_check_decorator
async def edit_audio_bible(request: Request,
    source_name: schemas.TableNamePattern=Path(..., example="hi_IRV_1_bible"),
    audios: List[schema_content.AudioBibleEdit] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    ''' Changes the mentioned fields of audio bible row.
    book codes are used to identify items and at least one is mandatory.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_audio_bible')
    log.debug('source_name: %s, audios: %s',source_name, audios)
    return {'message': "Bible audios details updated successfully",
        "data": contents_crud.update_bible_audios(db_=db_, source_name=source_name,
        audios=audios, user_id=user_details['user_id'])}

# # ##### Commentary #####
@router.get('/v2/commentaries/{source_name}',
    response_model=List[schema_content.CommentaryResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}}, status_code=200, tags=["Commentaries"])
@get_auth_access_check_decorator
async def get_commentary(request: Request,
    source_name: schemas.TableNamePattern=Path(..., example="en_BBC_1_commentary"),
    book_code: schemas.BookCodePattern=Query(None, example="1ki"),
    chapter: int = Query(None, example=10, ge=-1), verse: int = Query(None, example=1, ge=-1),
    last_verse: int = Query(None, example=3, ge=-1), active: bool = True,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
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

@router.post('/v2/commentaries/{source_name}',
    response_model=schema_content.CommentaryCreateResponse, response_model_exclude_none=True,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Commentaries"])
@get_auth_access_check_decorator
async def add_commentary(request: Request,background_tasks: BackgroundTasks,
    source_name : schemas.TableNamePattern=Path(...,example="en_BBC_1_commentary"),
    commentaries: List[schema_content.CommentaryCreate] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
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
    # verify source exist
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    job_info = nlp_sw_crud.create_job(db_=db_, user_id=user_details['user_id'])
    job_id = job_info.jobId
    background_tasks.add_task(contents_crud.upload_commentaries,db_=db_, source_name=source_name,
        commentaries=commentaries, job_id=job_id, user_id=user_details['user_id'])
    data = {"jobId": job_info.jobId, "status": job_info.status}
    job_resp = {"message": "Uploading Commentaries in background", "data": data}
    return {'db_content':job_resp,'source_content':source_db_content}
    # return {'message': "Commentaries added successfully",
    # "data": contents_crud.upload_commentaries(db_=db_, source_name=source_name,
    #     commentaries=commentaries, user_id=user_details['user_id'])}

@router.put('/v2/commentaries/{source_name}',
    response_model=schema_content.CommentaryUpdateResponse,response_model_exclude_none=True,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Commentaries"])
@get_auth_access_check_decorator
async def edit_commentary(request: Request,background_tasks: BackgroundTasks,
    source_name: schemas.TableNamePattern=Path(..., example="en_BBC_1_commentary"),
    commentaries: List[schema_content.CommentaryEdit] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    ''' Changes the commentary field to the given value in the row selected using
    book, chapter, verseStart and verseEnd values.
    Also active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_commentary')
    log.debug('source_name: %s, commentaries: %s',source_name, commentaries)
    # verify source exist
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    job_info = nlp_sw_crud.create_job(db_=db_, user_id=user_details['user_id'])
    job_id = job_info.jobId
    background_tasks.add_task(contents_crud.update_commentaries,db_=db_, source_name=source_name,
        commentaries=commentaries, job_id=job_id, user_id=user_details['user_id'])
    data = {"jobId": job_info.jobId, "status": job_info.status}
    job_resp = {"message": "Updating Commentaries in background", "data": data}
    return {'db_content':job_resp,'source_content':source_db_content}
    # return {'message': "Commentaries updated successfully",
    # "data": contents_crud.update_commentaries(db_=db_, source_name=source_name,
    #     commentaries=commentaries, user_id=user_details['user_id'])}

# # ########### Dictionary ###################
@router.get('/v2/dictionaries/{source_name}',
    response_model_exclude_unset=True,
    response_model=List[schema_content.DictionaryWordResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},}, status_code=200, tags=["Dictionaries"])
@get_auth_access_check_decorator
async def get_dictionary_word(request: Request,
    source_name: schemas.TableNamePattern=Path(...,example="en_TW_1_dictionary"),
    search_word: str=Query(None, example="Adam"),
    exact_match: bool=False, word_list_only: bool=False,
    details: schemas.MetaDataPattern=Query(None, example='{"type":"person"}'), active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db),
    operates_on=Depends(AddHiddenInput(value=schema_auth.ResourceType.CONTENT.value))):
    #operates_on=schema_auth.ResourceType.CONTENT.value
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

@router.post('/v2/dictionaries/{source_name}',
    response_model=schema_content.DictionaryCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Dictionaries"])
@get_auth_access_check_decorator
async def add_dictionary_word(request: Request,
    source_name : schemas.TableNamePattern=Path(..., example="en_TW_1_dictionary"),
    dictionary_words: List[schema_content.DictionaryWordCreate] = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    ''' uploads dictionay words and their details. 'Details' should be of JSON datatype and  have
    all the additional info we have for each word, as key-value pairs.
    The word will serve as the unique identifier'''
    log.info('In add_dictionary_word')
    log.debug('source_name: %s, dictionary_words: %s',source_name, dictionary_words)
    return {'message': "Dictionary words added successfully",
        "data": contents_crud.upload_dictionary_words(db_=db_, source_name=source_name,
        dictionary_words=dictionary_words, user_id=user_details['user_id'])}

@router.put('/v2/dictionaries/{source_name}',
    response_model=schema_content.DictionaryUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Dictionaries"])
@get_auth_access_check_decorator
async def edit_dictionary_word(request: Request,
    source_name: schemas.TableNamePattern=Path(..., example="en_TW_1_dictionary"),
    dictionary_words: List[schema_content.DictionaryWordEdit] = Body(...),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    ''' Updates a dictionary word. Item identifier is word, which cannot be altered.
    * Updates all the details, of the specifed word, if details is provided.
    * Active field can be used to activate or deactivate a word.
    Deactivated words are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_dictionary_word')
    log.debug('source_name: %s, dictionary_words: %s',source_name, dictionary_words)
    return {'message': "Dictionary words updated successfully",
        "data": contents_crud.update_dictionary_words(db_=db_, source_name=source_name,
        dictionary_words=dictionary_words, user_id=user_details['user_id'])}

# # ########### Infographic ###################
@router.get('/v2/infographics/{source_name}',
    response_model=List[schema_content.InfographicResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}}, status_code=200, tags=["Infographics"])
@get_auth_access_check_decorator
async def get_infographic(request: Request,
    source_name:schemas.TableNamePattern=Path(...,example="hi_IRV_1_infographic"),
    book_code: schemas.BookCodePattern=Query(None, example="exo"),
    title: str=Query(None, example="Ark of Covenant"), active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db)):
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

@router.post('/v2/infographics/{source_name}',
    response_model=schema_content.InfographicCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Infographics"])
@get_auth_access_check_decorator
async def add_infographics(request: Request,
    source_name : schemas.TableNamePattern=Path(...,
    example="hi_IRV_1_infographic"),
    infographics: List[schema_content.InfographicCreate] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    '''Uploads a list of infograhics. BookCode and title provided, serves as the unique idetifier
    Only the  link to infographic is stored, not the actual file'''
    log.info('In add_infographics')
    log.debug('source_name: %s, infographics: %s',source_name, infographics)
    return {'message': "Infographics added successfully",
        "data": contents_crud.upload_infographics(db_=db_, source_name=source_name,
        infographics=infographics, user_id=user_details['user_id'])}

@router.put('/v2/infographics/{source_name}',
    response_model=schema_content.InfographicUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Infographics"])
@get_auth_access_check_decorator
async def edit_infographics(request: Request,
    source_name: schemas.TableNamePattern=Path(...,
    example="hi_IRV_1_infographic"),
    infographics: List[schema_content.InfographicEdit] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    ''' Changes either the infographic link or active status.
    Item identifier is book code and title, which cannot be altered.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_infographics')
    log.debug('source_name: %s, infographics: %s',source_name, infographics)
    return {'message': "Infographics updated successfully",
        "data": contents_crud.update_infographics(db_=db_, source_name=source_name,
        infographics=infographics, user_id=user_details['user_id'])}

# # ########### bible videos ###################
@router.get('/v2/biblevideos/{source_name}',
    response_model=List[schema_content.BibleVideo],response_model_exclude_none=True,
    responses={502: {"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Bible Videos"])
@get_auth_access_check_decorator
async def get_biblevideo(request: Request,
    source_name:schemas.TableNamePattern=Path(...,example="en_TBP_1_biblevideo"),
    title: str=Query(None, example="Overview: song of songs"),
    series: str=Query(None, example="Old Testament"),
    search_word: str = Query(None, example="faith"),
    book_code: schemas.BookCodePattern=Query(None, example="sng"),
    chapter: int=Query(None, example="1"),
    verse: int=Query(None, example="1"), active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db)):
    '''Fetches the Bible video details and URL.
    * optional query parameters can be used to filter the result set
    * Filter by reference in the format book, book and chapter, book-chapter-verse
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_biblevideo')
    log.debug('source_name: %s, book_code: %s, title: %s, theme: %s, skip: %s, limit: %s',
        source_name, book_code, title, series, skip, limit)
    return media_crud.get_bible_videos(db_, source_name, book_code, title, series,
    search_word=search_word,chapter=chapter,verse=verse,
    active=active, skip=skip, limit=limit)

@router.post('/v2/biblevideos/{source_name}',
    response_model=schema_content.BibleVideoCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bible Videos"])
@get_auth_access_check_decorator
async def add_biblevideo(request: Request,
    source_name:schemas.TableNamePattern=Path(...,example="en_TBP_1_biblevideo"),
    videos: List[schema_content.BibleVideoUpload] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    '''Uploads a list of bible video links and details.
    Provided title will serve as the unique identifier'''
    log.info('In add_biblevideo')
    log.debug('source_name: %s, videos: %s',source_name, videos)
    return {'message': "Bible videos added successfully",
        "data": media_crud.upload_bible_videos(db_=db_, source_name=source_name,
        videos=videos, user_id=user_details['user_id'])}

@router.put('/v2/biblevideos/{source_name}', response_model=schema_content.BibleVideoUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bible Videos"])
@get_auth_access_check_decorator
async def edit_biblevideo(request: Request,
    source_name:schemas.TableNamePattern=Path(...,example="en_TBP_1_biblevideo"),
    videos: List[schema_content.BibleVideoEdit] = Body(...),user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    ''' Changes the selected rows of bible videos table.
    Item identified by title, which cannot be altered.
    Active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_biblevideo')
    log.debug('source_name: %s, videos: %s',source_name, videos)
    return {'message': "Bible videos updated successfully",
        "data": media_crud.update_bible_videos(db_=db_, source_name=source_name,
        videos=videos, user_id=user_details['user_id'])}

@router.get('/v2/sources/get-sentence', response_model=List[schemas_nlp.SentenceInput],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Sources"])
@get_auth_access_check_decorator
async def extract_text_contents(request:Request, #pylint: disable=W0613
    source_name:schemas.TableNamePattern=Query(None,example="en_TBP_1_bible"),
    books:List[schemas.BookCodePattern]=Query(None,example='GEN'),
    language_code:schemas.LangCodePattern=Query(None, example="hi"),
    content_type:str=Query(None, example="commentary"),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0),
    user_details = Depends(get_user_or_none), db_: Session = Depends(get_db),
    operates_on=Depends(AddHiddenInput(value=schema_auth.ResourceType.RESEARCH.value))):
    '''A generic API for all content type tables to get just the text contents of that table
    that could be used for translation, as corpus for NLP operations like SW identification.
    If source_name is provided, only that filter will be considered over content_type & language.'''
    log.info('In extract_text_contents')
    log.debug('source_name: %s, language_code: %s',source_name, language_code)
    try:
        tables = await get_source(request=request, source_name=source_name,
            content_type=content_type, version_abbreviation=None,
            revision=None, language_code=language_code,
            license_code=None, metadata=None,
            access_tag = None, active= True, latest_revision= True,
            skip=0, limit=1000, user_details=user_details, db_=db_,
            operates_on=schema_auth.ResourceType.CONTENT.value,
            filtering_required=True)
    except Exception:
        log.error("Error in getting sources list")
        raise
    # the projects sources or drafts where people are willing to share their data for learning
    # could be used for text content extraction. But need to be able to filter projects based on
    # use_data_for_learning flag and translation status(need to add a field in metadata for that).
    # projects = projects_crud.get_agmt_projects(db_, source_language=language_code) +
    #     projects_crud.get_agmt_projects(db_, target_language=language_code)
    if len(tables) == 0:
        raise NotAvailableException("No sources available for the requested name or language")
    return contents_crud.extract_text(db_, tables, books, skip=skip, limit=limit)
