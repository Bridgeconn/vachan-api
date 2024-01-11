'''API endpoints related to content management''' #pylint: disable=too-many-lines
from typing import List
from fastapi import APIRouter, Query, Depends, Path , Request
from sqlalchemy.orm import Session
from schema import schemas,schemas_nlp, schema_auth, schema_content
from dependencies import get_db, log, AddHiddenInput
from crud import structurals_crud, contents_crud
from custom_exceptions import NotAvailableException
from auth.authentication import get_auth_access_check_decorator ,\
    get_user_or_none

router = APIRouter()

#pylint: disable=too-many-arguments,unused-argument

###### Resource #####
@router.get('/v2/resources',
    response_model=List[schemas.ResourceResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse}},
    status_code=200, tags=["Resources"])
@get_auth_access_check_decorator
async def get_resource(request: Request, #pylint: disable=too-many-locals
    resource_name : schemas.TableNamePattern=Query(None, examples="hi_IRV_1_bible"),
    resource_type: str=Query(None, examples="commentary"),
    version_abbreviation: schemas.VersionPattern=Query(None,examples="KJV"),
    version_tag: schemas.VersionTagPattern=Query(None, examples="1611.12.31"),
    language_code: schemas.LangCodePattern=Query(None,examples="en"),
    license_code: schemas.LicenseCodePattern=Query(None,examples="ISC"),
    metadata: schemas.MetaDataPattern=Query(None,
        examples='{"otherName": "KJBC, King James Bible Commentaries"}'),
    access_tag:List[schemas.ResourcePermissions]=Query([schemas.ResourcePermissions.CONTENT]),
    labels:List[schemas.ResourceLabel] = Query([]),
    active: bool = True, latest_revision: bool = True,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db),
    operates_on=Depends(AddHiddenInput(value=schema_auth.ResourceType.CONTENT.value)),
    filtering_required=Depends(AddHiddenInput(value=True))):
    '''Fetches all resources and their details.
    * Optional query parameters can be used to filter the result set
    * If version_tag is not explictly set or latest_revision is not set to False, then only
     item with highest version_tag among same version would be returned.
     (If that is not the required version, use labels to mark another item as latest)
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_resource')
    log.debug('resourceName:%s,resourceType:%s, versionAbbreviation: %s, versionTag: %s, \
    languageCode: %s,license_code:%s, metadata: %s, access_tag: %s, latest_revision:\
         %s, labels:%s, active: %s, skip: %s, limit: %s',resource_name,
        resource_type, version_abbreviation, version_tag, language_code, license_code, metadata,
        access_tag, latest_revision, labels, active, skip, limit)
    return structurals_crud.get_resources(db_, resource_type, version_abbreviation,
        version_tag=version_tag,language_code=language_code, license_code=license_code,
        metadata=metadata,access_tag=access_tag,
        latest_revision=latest_revision, labels=labels,active=active,
        skip=skip, limit=limit,resource_name=resource_name)

# ########### Vocabulary ###################
@router.get('/v2/resources/vocabularies/{resource_name}',
    response_model_exclude_unset=True,
    response_model=List[schema_content.VocabularyWordResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},}, status_code=200, tags=["Vocabularies"])
@get_auth_access_check_decorator
async def get_vocabulary_word(request: Request,
    resource_name: schemas.TableNamePattern=Path(...,examples="en_TW_1_vocabulary"),
    search_word: str=Query(None, examples="Adam"),
    exact_match: bool=False, word_list_only: bool=False,
    details: schemas.MetaDataPattern=Query(None, examples='{"type":"person"}'), active: bool=None,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db),
    operates_on=Depends(AddHiddenInput(value=schema_auth.ResourceType.CONTENT.value))):
    #operates_on=schema_auth.ResourceType.CONTENT.value
    '''fetches list of vocabulary words and all available details about them.
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
    log.info('In get_vocabulary_word')
    log.debug('resource_name: %s, search_word: %s, exact_match: %s, word_list_only:%s, details:%s\
        skip: %s, limit: %s', resource_name, search_word, exact_match, word_list_only, details,
        skip, limit)
    return contents_crud.get_vocabulary_words(db_, resource_name=resource_name,
        search_word=search_word,
        exact_match=exact_match,
        word_list_only=word_list_only, details=details, active=active, skip=skip, limit=limit)


@router.get('/v2/resources/get-sentence', response_model=List[schemas_nlp.SentenceInput],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Resources"])
@get_auth_access_check_decorator
async def extract_text_contents(request:Request, #pylint: disable=W0613
    resource_name:schemas.TableNamePattern=Query(None,examples="en_TBP_1_bible"),
    books:List[schemas.BookCodePattern]=Query(None,examples='GEN'),
    language_code:schemas.LangCodePattern=Query(None, examples="hi"),
    resource_type:str=Query(None, examples="commentary"),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0),
    user_details = Depends(get_user_or_none), db_: Session = Depends(get_db),
    operates_on=Depends(AddHiddenInput(value=schema_auth.ResourceType.RESEARCH.value))):
    '''A generic API for all content type tables to get just the text contents of that table
    that could be used for translation, as corpus for NLP operations like SW identification.
    If resource_name is provided, only that filter will be considered over resource_type & 
    language.'''
    log.info('In extract_text_contents')
    log.debug('resource_name: %s, language_code: %s',resource_name, language_code)
    try:
        tables = await get_resource(request=request, resource_name=resource_name,
            resource_type=resource_type, version_abbreviation=None,
            version_tag=None, language_code=language_code,
            license_code=None, metadata=None,
            access_tag = None, labels=None, active= True, latest_revision= True,
            skip=0, limit=1000, user_details=user_details, db_=db_,
            operates_on=schema_auth.ResourceType.CONTENT.value,
            filtering_required=True)
    except Exception:
        log.error("Error in getting resources list")
        raise
    # the projects resources or drafts where people are willing to share their data for learning
    # could be used for text content extraction. But need to be able to filter projects based on
    # use_data_for_learning flag and translation status(need to add a field in metadata for that).
    # projects = projects_crud.get_agmt_projects(db_, resource_language=language_code) +
    #     projects_crud.get_agmt_projects(db_, target_language=language_code)
    if len(tables) == 0:
        raise NotAvailableException("No resources available for the requested name or language")
    return contents_crud.extract_text(db_, tables, books, skip=skip, limit=limit)


# @router.get('/v2/jobs', response_model=schemas_nlp.JobStatusResponse,
#     response_model_exclude_none=True, status_code=200,
#     responses={502: {"model": schemas.ErrorResponse},
#     422: {"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse}},
#     tags=['Jobs'])
# @get_auth_access_check_decorator
# async def check_job_status(request: Request,
#     job_id:int=Query(...,examples="100000"),user_details =Depends(get_user_or_none),
#     db_:Session=Depends(get_db)):
#     '''Checking the status of a job'''
#     log.info('In check_job_status')
#     log.debug('job_id:%s', job_id)
#     result = nlp_sw_crud.check_job_status(db_, job_id)
#     return result
