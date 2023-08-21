'''API endpoints related to content management''' #pylint: disable=too-many-lines
import json
from typing import List,Dict
import jsonpickle
from fastapi import APIRouter, Query, Body, Depends, Path , Request,BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import AnyUrl
import db_models
from schema import schemas,schemas_nlp, schema_auth, schema_content
from dependencies import get_db, log, AddHiddenInput
from crud import structurals_crud, contents_crud, nlp_sw_crud
from custom_exceptions import NotAvailableException, AlreadyExistsException,\
    UnprocessableException
from auth.authentication import get_auth_access_check_decorator ,\
    get_user_or_none

router = APIRouter()

#pylint: disable=too-many-arguments,unused-argument
##### Content types #####
@router.get('/v2/resources/types', response_model=List[schemas.ResourceType],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}},  status_code=200,
    tags=["Resources Types"])
@get_auth_access_check_decorator
async def get_resources_types(request: Request,resource_type: str = Query(None, example="bible"),
     skip: int = Query(0, ge=0),limit: int = Query(100, ge=0),
     user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    '''fetches all the resources types supported and their details
    * the optional query parameter can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n'''
    log.info('In get_resources_types')
    log.debug('resourceType:%s, skip: %s, limit: %s',resource_type, skip, limit)
    return structurals_crud.get_resource_types(db_, resource_type=resource_type,
        skip=skip, limit=limit)

@router.post('/v2/resources/types', response_model=schemas.ResourceTypeUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    409: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Resources Types"])
@get_auth_access_check_decorator
async def add_resources_types(request: Request, resourcetype: schemas.ResourceTypeCreate,
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    ''' Creates a new resource type.
    Naming conventions to be followed
    - Use only english alphabets in lower case
    Additional operations required:
        1. Add corresponding table creation functions and mappings.
        2. Define input, output resources and all required APIs to handle this resource'''
    log.info('In add_resources_types')
    log.debug('resourcetype: %s',resourcetype)
    if len(structurals_crud.get_resource_types(db_, resource_type=resourcetype.resourceType)) > 0:
        raise AlreadyExistsException(f"{resourcetype.resourceType} already present")
    data = structurals_crud.create_resource_types(db_=db_, \
        resourcetype=resourcetype,user_id=user_details['user_id'])
    return {'message': "Resource type created successfully",
            "data": data}

@router.delete('/v2/resources/types',response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Resources Types"])
@get_auth_access_check_decorator
async def delete_resources_types(request: Request,
    resourcetype_id: int = Query(..., example=100001),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Delete Resourcetype
    * unique ResourceType Id can be used to delete an exisiting identity'''
    log.info('In delete_resources_types')
    log.debug('resourcetype-delete:%s',resourcetype_id)
    dbtable_name = "resource_types"
    if len(structurals_crud.get_resource_types(db_, resourcetype_id= resourcetype_id)) == 0:
        raise NotAvailableException(f"ResourceType id {resourcetype_id} not found")
    resourcetype_obj = resourcetype_id
    # print("####" ,resourcetype_obj)
    deleted_resourcetype = structurals_crud.delete_resource_types(db_=db_,
                                                                  resourcetype=resourcetype_obj)
    delcont = structurals_crud.add_deleted_data(db_=db_,del_content=  deleted_resourcetype,
            table_name = dbtable_name,deleting_user=user_details['user_id'])
    return {'message': f"ResourceType with identity {resourcetype_id} deleted successfully",
            "data": delcont}

##### languages #####
@router.get('/v2/resources/languages',
    response_model=List[schemas.LanguageResponse],
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Languages"])
@get_auth_access_check_decorator
async def get_language(request: Request,
    language_code : schemas.LangCodePattern = Query(None, example="hi"),
    language_name: str = Query(None, example="hindi"),
    search_word: str = Query(None, example="Sri Lanka"),
    localscript_name: str = Query(None,example="हिंदी"),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    '''fetches all the languages supported in the DB, their code and other details.
    * if any of the optional query parameters are provided, returns details of that language
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_language')
    log.debug('langauge_code:%s,language_name:%s,search_word:%s,localscript:%s,skip:%s,limit:%s',
        language_code, language_name, search_word,localscript_name, skip, limit)
    return structurals_crud.get_languages(db_, language_code, language_name, search_word,
        localscript_name = localscript_name, skip = skip, limit = limit)

@router.post('/v2/resources/languages', response_model=schemas.LanguageCreateResponse,
    responses={502: {"model":schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Languages"])
@get_auth_access_check_decorator
async def add_language(request: Request, lang_obj : schemas.LanguageCreate = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    ''' Creates a new language. Langugage code should follow BCP-47 standard.'''
    log.info('In add_language')
    log.debug('lang_obj: %s',lang_obj)
    if len(structurals_crud.get_languages(db_, language_code = lang_obj.code)) > 0:
        raise AlreadyExistsException(f"{lang_obj.code} already present")
    data =  structurals_crud.create_language(db_=db_, lang=lang_obj,
        user_id=user_details['user_id'])
    return {'message': "Language created successfully",
            "data": data}

@router.put('/v2/resources/languages', response_model=schemas.LanguageUpdateResponse,
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
        raise NotAvailableException(f"Language id {lang_obj.languageId} not found")
    return {'message': "Language edited successfully",
            "data": structurals_crud.update_language(db_=db_, lang=lang_obj,
            user_id=user_details['user_id'])}

@router.delete('/v2/resources/languages',response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Languages"])
@get_auth_access_check_decorator
async def delete_languages(request: Request,
    language_id: int = Query(..., example=100001),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Delete Language
    * unique Language Code can be used to delete an exisiting identity'''
    log.info('In delete_languages')
    log.debug('language-delete:%s',language_id)
    dbtable_name = "languages"
    if len(structurals_crud.get_languages(db_, language_id = language_id)) == 0:
        raise NotAvailableException(f"Language id {language_id} not found")
    deleted_content = structurals_crud.delete_language(db_=db_, lang=language_id)
    delcont = structurals_crud.add_deleted_data(db_=db_,del_content= deleted_content,
        table_name = dbtable_name,deleting_user=user_details['user_id'])
    return {'message': f"Language with identity {language_id} deleted successfully",
            "data": delcont}

########### Licenses ######################
@router.get('/v2/resources/licenses',
    response_model=List[schemas.LicenseResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Licenses"])
@get_auth_access_check_decorator
async def get_license(request: Request,
    license_code : schemas.LicenseCodePattern=Query(None, example="CC-BY-SA"),
    license_name: str=Query(None, example="Creative Commons License"),
    permission: schemas.ResourcePermissions=Query(None, example="open-access"),
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

@router.post('/v2/resources/licenses', response_model=schemas.LicenseCreateResponse,
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

@router.put('/v2/resources/licenses', response_model=schemas.LicenseUpdateResponse,
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

@router.delete('/v2/resources/licenses',response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Licenses"])
@get_auth_access_check_decorator
async def delete_licenses(request: Request,
    license_id:int = Query(..., example=100001),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Delete License
    * unique License Id can be used to delete an exisiting identity'''
    log.info('In delete_licenses')
    log.debug('license-delete:%s',license_id)
    dbtable_name = "licenses"
    if len(structurals_crud.get_licenses(db_, license_id= license_id)) == 0:
        raise NotAvailableException(f"License id {license_id} not found")
    deleted_content = structurals_crud.delete_license(db_=db_, content=license_id)
    delcont = structurals_crud.add_deleted_data(db_=db_,del_content= deleted_content,
            table_name = dbtable_name,deleting_user=user_details['user_id'])
    return {'message': f"License with identity {license_id} deleted successfully",
            "data": delcont}

##### Version #####
@router.get('/v2/resources/versions',
    response_model=List[schemas.VersionResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Versions"])
@get_auth_access_check_decorator
async def get_version(request: Request,
    version_abbreviation : schemas.VersionPattern = Query(None, example="KJV"),
    version_name: str = Query(None, example="King James Version"),
    version_tag : schemas.VersionTagPattern = Query(None),
    metadata: schemas.MetaDataPattern = Query(None, example='{"publishedIn":"1611"}'),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Fetches all versions and their details.
    * optional query parameters can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_version')
    log.debug('version_abbreviation:%s, version_name:%s, version_tag:%s, skip: %s, limit: %s',
        version_abbreviation, version_name, version_tag, skip, limit)
    return structurals_crud.get_versions(db_, version_abbreviation,
        version_name, version_tag, metadata, skip = skip, limit = limit)

@router.post('/v2/resources/versions', response_model=schemas.VersionCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Versions"])
@get_auth_access_check_decorator
async def add_version(request: Request, version_obj : schemas.VersionCreate = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    ''' Creates a new version. Version code provided will be used as unique identifier
    * For VersionTag, using a calender version, date separted by dot, is encouraged.
    But, if not provided, will be assumed as 1'''
    log.info('In add_version')
    log.debug('version_obj: %s',version_obj)
    if len(structurals_crud.get_versions(db_, version_obj.versionAbbreviation,
        version_tag =version_obj.versionTag)) > 0:
        raise AlreadyExistsException(f"{version_obj.versionAbbreviation}, "+\
            f"{version_obj.versionTag} already present")
    return {'message': "Version created successfully",
        "data": structurals_crud.create_version(db_=db_, version=version_obj,
        user_id=user_details['user_id'])}

@router.put('/v2/resources/versions', response_model=schemas.VersionUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Versions"])
@get_auth_access_check_decorator
async def edit_version(request: Request, ver_obj: schemas.VersionEdit = Body(...),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    ''' Changes one or more fields of version types table.
    * Item identifier is version id.
    * For VersionTag, using a calender version, date separted by dot, is encouraged.
    But, if not provided, will be assumed as "1"
    * Active field can be used to activate or deactivate a content.
    * Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_version')
    log.debug('ver_obj: %s',ver_obj)
    if len(structurals_crud.get_versions(db_, version_id = ver_obj.versionId)) == 0:
        raise NotAvailableException(f"Version id {ver_obj.versionId} not found")
    return {'message': "Version edited successfully",
        "data": structurals_crud.update_version(db_=db_, version=ver_obj,
        user_id=user_details['user_id'])}

@router.delete('/v2/resources/versions',response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Versions"])
@get_auth_access_check_decorator
async def delete_versions(request: Request,
    version_id: int = Query(..., example=100001),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Delete Version
    * unique Version Id can be used to delete an exisiting identity'''
    log.info('In delete_versions')
    log.debug('version-delete:%s',version_id)
    dbtable_name = "versions"
    if len(structurals_crud.get_versions(db_, version_id = version_id)) == 0:
        raise NotAvailableException(f"Version id {version_id} not found")
    deleted_content = structurals_crud.delete_version(db_=db_, ver=version_id)
    delcont = structurals_crud.add_deleted_data(db_=db_,del_content= deleted_content,
            table_name = dbtable_name,deleting_user=user_details['user_id'])
    return {'message': f"Version with identity {version_id} deleted successfully",
            "data": delcont}


###### Resource #####
@router.get('/v2/resources',
    response_model=List[schemas.ResourceResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse}},
    status_code=200, tags=["Resources"])
@get_auth_access_check_decorator
async def get_resource(request: Request, #pylint: disable=too-many-locals
    resource_name : schemas.TableNamePattern=Query(None, example="hi_IRV_1_bible"),
    resource_type: str=Query(None, example="commentary"),
    version_abbreviation: schemas.VersionPattern=Query(None,example="KJV"),
    version_tag: schemas.VersionTagPattern=Query(None, example="1611.12.31"),
    language_code: schemas.LangCodePattern=Query(None,example="en"),
    license_code: schemas.LicenseCodePattern=Query(None,example="ISC"),
    metadata: schemas.MetaDataPattern=Query(None,
        example='{"otherName": "KJBC, King James Bible Commentaries"}'),
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

@router.post('/v2/resources', response_model=schemas.ResourceCreateResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Resources"])
@get_auth_access_check_decorator
async def add_resource(request: Request, resource_obj : schemas.ResourceCreate = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    # user_details = Depends(auth_handler.kratos_session_validation)
    ''' Creates a new resource entry in resources table.
    * Also creates all associtated tables for the content type.
    * The required content type, version, language and license should be present in DB,
    * if not create them first.
    * Latest, can be included in labels for only one item per version.
    * AccessPermissions is list of permissions ["content", "open-access", "publishable",
        "downloadable","derivable"]. Default will be ["content"]
    * repo and defaultBranch should given in the metaData if resourceType is gitlabrepo,
        defaultBranch will be "main" if not mentioned in the metadata.
    '''
    log.info('In add_resource')
    log.debug('resource_obj: %s',resource_obj)
    if 'content' not in resource_obj.accessPermissions:
        resource_obj.accessPermissions.append(schemas.ResourcePermissions.CONTENT)
    resource_obj.metaData['accessPermissions'] = resource_obj.accessPermissions
    if resource_obj.resourceType == db_models.ResourceTypeName.GITLABREPO.value:
        if "repo" not in resource_obj.metaData:
            raise UnprocessableException("repo link in metadata is mandatory to create"+
                " resource with resourceType gitlabrepo")
        if len(structurals_crud.get_resources(db_, metadata =
                json.dumps({"repo":resource_obj.metaData["repo"]}))) > 0:
            raise AlreadyExistsException("already present Resource with same repo link")
        if "defaultBranch" not in resource_obj.metaData:
            resource_obj.metaData["defaultBranch"] = "main"
    return {'message': "Resource created successfully",
    "data": structurals_crud.create_resource(db_=db_, resource=resource_obj,
        user_id=user_details['user_id'])}

@router.put('/v2/resources', response_model=schemas.ResourceUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Resources"])
@get_auth_access_check_decorator
async def edit_resource(request: Request,resource_obj: schemas.ResourceEdit = Body(...),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    ''' Changes one or more fields of resource. Item identifier is resource_name.
    * Active field can be used to activate or deactivate a content.
    * Deactivated items are not included in normal fetch results if not specified otherwise
    * Edit of labels will overwrite the existing List of labels entirely
    * AccessPermissions is list of permissions ["content", "open-access", "publishable",
        "downloadable", "derivable"]. Edit accessPermission will overwrite the current list'''
    log.info('In edit_resource')
    log.debug('resource_obj: %s',resource_obj)
    if len(structurals_crud.get_resources(db_, resource_name = resource_obj.resourceName)) == 0:
        raise NotAvailableException(f"Resource {resource_obj.resourceName} not found")
    if 'content' not in resource_obj.accessPermissions:
        resource_obj.accessPermissions.append(schemas.ResourcePermissions.CONTENT)
    resource_obj.metaData['accessPermissions'] = resource_obj.accessPermissions
    if resource_obj.resourceName.split("_")[-1] == \
        db_models.ResourceTypeName.GITLABREPO.value:
        if "repo" not in resource_obj.metaData:
            raise UnprocessableException("repo link in metadata is mandatory to update"+
                " resource with resourceType gitlabrepo")
        current_resource = structurals_crud.get_resources(db_, metadata =
                json.dumps({"repo":resource_obj.metaData["repo"]}))
        if len(current_resource)>0 and not current_resource[0].resourceName ==\
             resource_obj.resourceName:
            raise AlreadyExistsException("already present another resource"+
            " with same repo link")
        if "defaultBranch" not in resource_obj.metaData:
            resource_obj.metaData["defaultBranch"] = "main"
    return {'message': "Resource edited successfully",
    "data": structurals_crud.update_resource(db_=db_, resource=resource_obj,
        user_id=user_details['user_id'])}

@router.delete('/v2/resources',response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Resources"])
@get_auth_access_check_decorator
async def delete_resources(request: Request,
    resource_id:int = Query(..., example=100001),
    user_details =Depends(get_user_or_none),  \
    db_: Session = Depends(get_db)):
    '''Delete Resource
    * unique Resource Id can be used to delete an exisiting identity'''
    log.info('In delete_resources')
    log.debug('resource-delete:%s',resource_id)
    dbtable_name = "resources"
    if len(structurals_crud.get_resources(db_, resource_id= resource_id)) == 0:
        raise NotAvailableException(f"Resource id {resource_id} not found")
    deleted_content = structurals_crud.delete_resource(db_=db_, delitem=resource_id)
    delcont = structurals_crud.add_deleted_data(db_=db_,del_content= deleted_content,
            table_name = dbtable_name,deleting_user=user_details['user_id'])
    return {'message': f"Resource with identity {resource_id} deleted successfully",
            "data": delcont}

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
@router.post('/v2/resources/bibles/{resource_name}/books',
    response_model=schema_content.BibleBookCreateResponse,
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse},409:{"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bibles"])
@get_auth_access_check_decorator
async def add_bible_book(request: Request,
    resource_name : schemas.TableNamePattern=Path(..., example="hi_IRV_1_bible"),
    books: List[schema_content.BibleBookUpload] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    '''Uploads a bible book. It update 2 tables: ..._bible, .._bible_cleaned.
    The JSON provided should be generated from the USFM, using usfm-grammar 2.0.0-beta.8 or above'''
    log.info('In add_bible_book')
    log.debug('resource_name: %s, books: %s',resource_name, books)
    return {'message': "Bible books uploaded and processed successfully",
        "data": contents_crud.upload_bible_books(db_=db_, resource_name=resource_name,
        books=books, user_id=user_details['user_id'])}

@router.put('/v2/resources/bibles/{resource_name}/books',
    response_model=schema_content.BibleBookUpdateResponse,
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Bibles"])
@get_auth_access_check_decorator
async def edit_bible_book(request: Request,
    resource_name: schemas.TableNamePattern=Path(..., example="hi_IRV_1_bible"),
    books: List[schema_content.BibleBookEdit] = Body(...),user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    '''Either changes the active status or the bible contents.
    * Active field can be used to activate or deactivate a content. For which,
    Item identifier is book code.
    Deactivated items are not included in normal fetch results if not specified otherwise
    * In the second case, the two fields, usfm and json,  are mandatory as they are interdependant.
    Contents of the respective bible_clean and bible_tokens tables
    are deleted and new data added, which changes the results of
    /v2/resources/bibles/{resource_name}/verses
    and tokens apis aswell.'''
    log.info('In edit_bible_book')
    log.debug('resource_name: %s, books: %s',resource_name, books)
    return {'message': "Bible books updated successfully",
        "data": contents_crud.update_bible_books(db_=db_, resource_name=resource_name,
        books=books, user_id=user_details['user_id'])}

@router.get('/v2/resources/bibles/{resource_name}/books',
    response_model=List[schema_content.BibleBookContent],
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Bibles"])
@get_auth_access_check_decorator
async def get_available_bible_book(request: Request,
    resource_name: schemas.TableNamePattern=Path(...,example="hi_IRV_1_bible"),
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
    log.debug('resource_name: %s, book_code: %s, resourceType: %s, active:%s, skip: %s, limit: %s',
        resource_name, book_code, content_type, active, skip, limit)
    return contents_crud.get_available_bible_books(db_, resource_name, book_code, content_type,
        active=active, skip = skip, limit = limit)

@router.delete('/v2/resources/bibles/{resource_name}/books',response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Bibles"])
@get_auth_access_check_decorator
async def delete_bible_book(request: Request,
    biblebook_id:int = Query(..., example=100001),
    resource_name: str = Path(...,example="en_KJV_1_bible"),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Delete Bible Book
    * unique bible book id with resource name can be used to delete an exisiting identity'''
    log.info('In delete_biblebook')
    log.debug('biblebook-delete:%s',biblebook_id)
    tb_name = db_models.dynamicTables[resource_name]
    dbtable_name = tb_name.__name__
    cleaned_tablename = dbtable_name+'_cleaned'
    get_bible_response = contents_crud.get_available_bible_books(db_, resource_name=resource_name, \
        biblecontent_id= biblebook_id)
    if len(get_bible_response['db_content']) == 0:
        raise NotAvailableException(f"Bible Book with id {biblebook_id} not found")
    deleted_content = contents_crud.delete_bible_book(db_=db_,delitem=biblebook_id,\
        resource_name=resource_name,user_id=user_details['user_id'])
    delcont = structurals_crud.add_deleted_data(db_= db_,del_content= deleted_content['db_content'],
        table_name = dbtable_name, resource = deleted_content['resource_content'],
        deleting_user=user_details['user_id'])
    del_clean=structurals_crud.add_deleted_data(db_=db_,del_content= deleted_content['db_content2'],#pylint: disable=unused-variable
        table_name=cleaned_tablename,resource=deleted_content['resource_content'],
        deleting_user=user_details['user_id'])
    return {'message': f"Bible Book with id {biblebook_id} deleted successfully",
            "data": delcont}

@router.get('/v2/resources/bibles/{resource_name}/versification',
    response_model= schema_content.Versification,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}}, status_code=200, tags=["Bibles"])
@get_auth_access_check_decorator
async def get_bible_versification(request: Request,
    resource_name:schemas.TableNamePattern=Path(..., example="hi_IRV_1_bible"),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db)):
    '''Fetches the versification structure of the specified bible,
    with details of number of chapters, max verses in each chapter etc'''
    log.info('In get_bible_versification')
    log.debug('resource_name: %s',resource_name)
    return contents_crud.get_bible_versification(db_, resource_name)

@router.get('/v2/resources/bibles/{resource_name}/verses',
    response_model=List[schema_content.BibleVerse],
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Bibles"])
@get_auth_access_check_decorator
async def get_bible_verse(request: Request,
    resource_name: schemas.TableNamePattern=Path(..., example="hi_IRV_1_bible"),
    book_code: schemas.BookCodePattern=Query(None, example="mat"),
    chapter: int=Query(None, example=1), verse: int=Query(None, example=1),
    last_verse: int=Query(None, example=15), search_phrase: str=Query(None, example='सन्‍तान'),
    active: bool=True,
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db)):
    ''' Fetches the cleaned contents of bible, within a verse range, if specified.
    This API could be used for fetching,
     * all verses of a resource : with out giving any query params.
     * all verses of a book: with only book_code
     * all verses of a chapter: with book_code and chapter
     * one verse: with bookCode, chapter and verse(without lastVerse).
     * any range of verses within a chapter: using verse and lastVerse appropriately
     * search for a query phrase in a bible and get matching verses: using search_phrase
     * skip=n: skips the first n objects in return list
     * limit=n: limits the no. of items to be returned to n
     * returns [] for not available content'''
    log.info('In get_bible_verse')
    log.debug('resource_name: %s, book_code: %s, chapter: %s, verse:%s, last_verse:%s,\
        search_phrase:%s, active:%s, skip: %s, limit: %s',
        resource_name, book_code, chapter, verse, last_verse, search_phrase, active, skip, limit)
    return contents_crud.get_bible_verses(db_, resource_name, book_code, chapter, verse,
    last_verse = last_verse, search_phrase=search_phrase, active=active,
    skip = skip, limit = limit)


# # ##### Commentary #####
@router.get('/v2/commentaries/{resource_name}',
    response_model=List[schema_content.CommentaryResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}}, status_code=200, tags=["Commentaries"])
@get_auth_access_check_decorator
async def get_commentary(request: Request,
    resource_name: schemas.TableNamePattern=Path(..., example="en_BBC_1_commentary"),
    book_code: schemas.BookCodePattern=Query(None, example="1ki"),
    chapter: int = Query(None, example=10, ge=-1), verse: int = Query(None, example=1, ge=-1),
    last_verse: int = Query(None, example=3, ge=-1), active: bool = True,
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Fetches commentries under the specified resource.
    * optional query parameters can be used to filter the result set
    * Using the params bookCode, chapter, and verse the result set can be filtered as per need,
    like in the /v2/resources/bibles/{resourceName}/verses API
    * Value 0 for verse and last_verse indicate chapter introduction and -1 indicate
    chapter epilogue.
    * Similarly 0 for chapter means book introduction and -1 for chapter means book epilogue
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content'''
    log.info('In get_commentary')
    log.debug('resource_name: %s, book_code: %s, chapter: %s, verse:%s,\
        last_verse:%s, skip: %s, limit: %s',
        resource_name, book_code, chapter, verse, last_verse, skip, limit)
    return contents_crud.get_commentaries(db_, resource_name=resource_name,chapter=chapter,\
        book_code=book_code,verse=verse, last_verse=last_verse,active=active,\
        skip = skip, limit = limit)

@router.post('/v2/commentaries/{resource_name}',
    response_model=schema_content.CommentaryCreateResponse, response_model_exclude_none=True,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Commentaries"])
@get_auth_access_check_decorator
async def add_commentary(request: Request,background_tasks: BackgroundTasks,
    resource_name : schemas.TableNamePattern=Path(...,example="en_BBC_1_commentary"),
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
    log.debug('resource_name: %s, commentaries: %s',resource_name, commentaries)
    # verify resource exist
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    job_info = nlp_sw_crud.create_job(db_=db_, user_id=user_details['user_id'])
    job_id = job_info.jobId
    background_tasks.add_task(contents_crud.upload_commentaries, db_=db_,
        resource_name=resource_name, commentaries=commentaries, job_id=job_id,
        user_id=user_details['user_id'])
    data = {"jobId": job_info.jobId, "status": job_info.status}
    job_resp = {"message": "Uploading Commentaries in background", "data": data}
    return {'db_content':job_resp,'resource_content':resource_db_content}
    # return {'message': "Commentaries added successfully",
    # "data": contents_crud.upload_commentaries(db_=db_, resource_name=resource_name,
    #     commentaries=commentaries, user_id=user_details['user_id'])}

@router.put('/v2/commentaries/{resource_name}',
    response_model=schema_content.CommentaryUpdateResponse,response_model_exclude_none=True,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Commentaries"])
@get_auth_access_check_decorator
async def edit_commentary(request: Request,background_tasks: BackgroundTasks,
    resource_name: schemas.TableNamePattern=Path(..., example="en_BBC_1_commentary"),
    commentaries: List[schema_content.CommentaryEdit] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    ''' Changes the commentary field to the given value in the row selected using
    book, chapter, verseStart and verseEnd values.
    Also active field can be used to activate or deactivate a content.
    Deactivated items are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_commentary')
    log.debug('resource_name: %s, commentaries: %s',resource_name, commentaries)
    # verify resource exist
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    job_info = nlp_sw_crud.create_job(db_=db_, user_id=user_details['user_id'])
    job_id = job_info.jobId
    background_tasks.add_task(contents_crud.update_commentaries,db_=db_,
        resource_name=resource_name, commentaries=commentaries, job_id=job_id,
        user_id=user_details['user_id'])
    data = {"jobId": job_info.jobId, "status": job_info.status}
    job_resp = {"message": "Updating Commentaries in background", "data": data}
    return {'db_content':job_resp,'resource_content':resource_db_content}
    # return {'message': "Commentaries updated successfully",
    # "data": contents_crud.update_commentaries(db_=db_, resource_name=resource_name,
    #     commentaries=commentaries, user_id=user_details['user_id'])}

@router.delete('/v2/commentaries/{resource_name}',response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Commentaries"])
@get_auth_access_check_decorator
async def delete_commentary(request: Request,
    commentary_id:int = Query(..., example=100001),
    resource_name: schemas.TableNamePattern=Path(..., example="en_BBC_1_commentary"),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Delete Commentary
    * unique Commentary Id with resource name can be used to delete an exisiting identity'''
    log.info('In delete_commentaries')
    log.debug('commentary-delete:%s',commentary_id)
    tb_name = db_models.dynamicTables[resource_name]
    dbtable_name = tb_name.__name__
    get_commentary_response = contents_crud.get_commentaries(db_, \
        resource_name=resource_name, commentary_id= commentary_id)
    if len(get_commentary_response['db_content']) == 0:
        raise NotAvailableException(f"Commentary with id {commentary_id} not found")
    deleted_content = contents_crud.delete_commentary(db_=db_,delitem=commentary_id,\
        table_name=tb_name,resource_name=resource_name,user_id=user_details['user_id'])
    delcont = structurals_crud.add_deleted_data(db_=db_,del_content= deleted_content['db_content'],
        table_name= dbtable_name, resource=deleted_content['resource_content'],
        deleting_user = user_details['user_id'])
    return {'message': f"Commentary id {commentary_id} deleted successfully",
            "data": delcont}
# # ########### Vocabulary ###################
@router.get('/v2/vocabularies/{resource_name}',
    response_model_exclude_unset=True,
    response_model=List[schema_content.VocabularyWordResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},}, status_code=200, tags=["Vocabularies"])
@get_auth_access_check_decorator
async def get_vocabulary_word(request: Request,
    resource_name: schemas.TableNamePattern=Path(...,example="en_TW_1_vocabulary"),
    search_word: str=Query(None, example="Adam"),
    exact_match: bool=False, word_list_only: bool=False,
    details: schemas.MetaDataPattern=Query(None, example='{"type":"person"}'), active: bool=None,
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

@router.get('/v2/vocabularies/{resource_name}/count',
    response_model=int,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},}, status_code=200, tags=["Vocabularies"])
@get_auth_access_check_decorator
async def get_vocabulary_word_count(request: Request,
    resource_name: schemas.TableNamePattern=Path(...,example="en_TW_1_vocabulary"),
    search_word: str=Query(None, example="Adam"),
    exact_match: bool=False,
    details: schemas.MetaDataPattern=Query(None, example='{"type":"person"}'),
    active: bool= Query(None),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db),
    operates_on=Depends(AddHiddenInput(value=schema_auth.ResourceType.CONTENT.value))):
    '''Counts vocabulary words that match the query criteria.
    Using the search_word appropriately, it is possible to count:
    * All word in the vocabulary, if not specified
    * All words starting with a letter
    * All words starting with a substring
    * An exact word search, giving the whole word and setting exactMatch to True
    * Based on any key value pair in details, which should be specified as a dict/JSON like string
    * Both active and deactivated words, by not specifiying a value for active, which is default.
        Recommended that it is set to true for regular use-cases
    '''
    log.info('In get_vocabulary_word_count')
    log.debug('resource_name: %s, search_word: %s, exact_match: %s,  details:%s',
        resource_name, search_word, exact_match, details)
    response = contents_crud.get_vocabulary_words(db_, resource_name=resource_name,
        search_word=search_word, exact_match=exact_match,
        word_list_only=True, details=details, active=active, skip=None, limit=None)
    response['db_content'] = len(response['db_content'])
    return response

@router.post('/v2/vocabularies/{resource_name}',
    response_model=schema_content.VocabularyCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Vocabularies"])
@get_auth_access_check_decorator
async def add_vocabulary_word(request: Request,
    resource_name : schemas.TableNamePattern=Path(..., example="en_TW_1_vocabulary"),
    vocabulary_words: List[schema_content.VocabularyWordCreate] = Body(...),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    ''' uploads dictionay words and their details. 'Details' should be of JSON datatype and  have
    all the additional info we have for each word, as key-value pairs.
    The word will serve as the unique identifier'''
    log.info('In add_vocabulary_word')
    log.debug('resource_name: %s, vocabulary_words: %s',resource_name, vocabulary_words)
    return {'message': "Vocabulary words added successfully",
        "data": contents_crud.upload_vocabulary_words(db_=db_, resource_name=resource_name,
        vocabulary_words=vocabulary_words, user_id=user_details['user_id'])}

@router.put('/v2/vocabularies/{resource_name}',
    response_model=schema_content.VocabularyUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Vocabularies"])
@get_auth_access_check_decorator
async def edit_vocabulary_word(request: Request,
    resource_name: schemas.TableNamePattern=Path(..., example="en_TW_1_vocabulary"),
    vocabulary_words: List[schema_content.VocabularyWordEdit] = Body(...),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    ''' Updates a vocabulary word. Item identifier is word, which cannot be altered.
    * Updates all the details, of the specifed word, if details is provided.
    * Active field can be used to activate or deactivate a word.
    Deactivated words are not included in normal fetch results if not specified otherwise'''
    log.info('In edit_vocabulary_word')
    log.debug('resource_name: %s, vocabulary_words: %s',resource_name, vocabulary_words)
    return {'message': "Vocabulary words updated successfully",
        "data": contents_crud.update_vocabulary_words(db_=db_, resource_name=resource_name,
        vocabulary_words=vocabulary_words, user_id=user_details['user_id'])}

@router.delete('/v2/vocabularies/{resource_name}',response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Vocabularies"])
@get_auth_access_check_decorator
async def delete_vocabularies(request: Request,
    word_id: int = Query(..., example=100001),
    resource_name: str = Path(...,example="en_KJV_1_vocabulary"),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Delete Vocabulary
    * unique word Id with resource name can be used to delete an exisiting identity'''
    log.info('In delete_vocabularies')
    log.debug('vocabulary-delete:%s',word_id)
    tb_name = db_models.dynamicTables[resource_name]
    dbtable_name = tb_name.__name__
    get_vocabulary_response = contents_crud.get_vocabulary_words(db_, resource_name=resource_name,
                 word_id= word_id)
    if len(get_vocabulary_response['db_content']) == 0:
        raise NotAvailableException(f"Vocabulary with id {word_id} not found")
    deleted_content = contents_crud.delete_vocabulary(db_=db_,
        delitem=word_id,
        table_name=tb_name,resource_name=resource_name,user_id=user_details['user_id'])
    delcont = structurals_crud.add_deleted_data(db_=db_,del_content= deleted_content['db_content'],
        table_name = dbtable_name, resource = deleted_content['resource_content'],
        deleting_user = user_details['user_id'])
    return {'message': f"Vocabulary id {word_id} deleted successfully",
            "data": delcont}

# # ########### Parascriptural ###################
@router.get('/v2/resources/parascripturals/{resource_name}',
    response_model=List[schema_content.ParascriptResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}}, status_code=200, tags=["Parascripturals"])
@get_auth_access_check_decorator
async def get_parascriptural(request: Request, #pylint: disable=too-many-locals
    resource_name:schemas.TableNamePattern=
    Path(...,example="en_KJV_1_parascriptural"),
    category:str=Query(None, example="Bible project video"),
    title:str=Query(None,example="Bible Video of Genesis"),
    description:str=Query(None, example="Origin Chronicles"),
    content:str=Query(None, example="A Visual Journey Through the Bible's Beginning"),
    reference: str = Query(None,
    example='{"book": "mat", "chapter": 1, "verseNumber": 6}'),
    link:AnyUrl=Query(None,example="http://someplace.com/resoucesid"),
    search_word:str=Query(None,example="subtitle"),
    metadata: schemas.MetaDataPattern=Query(None,
        example='{"otherName": "BPV, Videos of Bible chapters"}'),
    active: bool=Query(True),
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db)):
    '''Fetches the parascripturals. Can use, parascriptural name,type and/or title
       to filter the results
    * optional query parameters can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content
    * Filter with single reference -> eg :{"book": "mat", "chapter": 1, "verseNumber": 6}
    * Filter with cross chapter references -> eg:reference": {"book":"MRK", "chapter":11,
        "verseNumber":12,"bookEnd":"LUK", "chapterEnd":14, "verseEnd":15 }'''
    log.info('In get_parascriptural')
    log.debug('resource_name: %s,type: %s,title: %s, skip: %s,limit: %s,search_word: %s,\
        reference:%s,metadata:%s',resource_name,category,title,skip,limit,search_word,\
        reference,metadata)
    reference_dict: Dict[str, int] = None
    if reference:
        reference_dict = json.loads(reference)
    return contents_crud.get_parascripturals(db_, resource_name, category, title,
        description = description, content = content, reference = reference_dict, link = link,
        search_word = search_word, metadata = metadata, active = active, skip = skip, limit = limit)

@router.post('/v2/resources/parascripturals/{resource_name}',
    response_model=schema_content.ParascriptCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Parascripturals"])
@get_auth_access_check_decorator
async def add_parascripturals(request: Request,
    resource_name : schemas.TableNamePattern=Path(...,
    example="en_KJV_1_parascriptural"),
    parascriptural: List[schema_content.ParascripturalCreate] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    '''Uploads a list of parascripturals. category field is mandatory'''
    log.info('In add_parascripturals')
    log.debug('resource_name: %s, parascripturals: %s',resource_name, parascriptural)
    return {'message': "Parascripturals added successfully",
        "data": contents_crud.upload_parascripturals(db_=db_, resource_name=resource_name,
        parascriptural=parascriptural, user_id=user_details['user_id'])}

@router.put('/v2/resources/parascripturals/{resource_name}',
    response_model=schema_content.ParascriptUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Parascripturals"])
@get_auth_access_check_decorator
async def edit_parascripturals(request: Request,
    resource_name: schemas.TableNamePattern=Path(...,
    example="en_KJV_1_parascriptural"),
    parascripturals: List[schema_content.ParascriptEdit] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    ''' Changes description,content or link.
    Item identifier is parascript type and title, which cannot be altered.'''
    log.info('In edit_parascripturals')
    log.debug('resource_name: %s, parascripturals: %s',resource_name, parascripturals)
    return {'message': "Parascripturals updated successfully",
        "data": contents_crud.update_parascripturals(db_=db_, resource_name=resource_name,
        parascripturals=parascripturals, user_id=user_details['user_id'])}

@router.delete('/v2/resources/parascripturals/{resource_name}',
    response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Parascripturals"])
@get_auth_access_check_decorator
async def delete_parascripturals(request: Request,
    parascript_id:int = Query(..., example=100001),
    resource_name: str = Path(...,example="en_KJV_1_parascriptural"),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Delete Parascriptural
    * unique parascript Id with source name can be used to delete an exisiting identity'''
    log.info('In delete_parascripturals')
    log.debug('parascripturals-delete:%s',parascript_id)
    tb_name = db_models.dynamicTables[resource_name]
    dbtable_name = tb_name.__name__
    get_parascriptural_response = contents_crud.get_parascripturals(
        db_, resource_name=resource_name, parascript_id= parascript_id)
    if len(get_parascriptural_response['db_content']) == 0:
        raise NotAvailableException(f"Parascriptural with id {parascript_id} not found")
    deleted_content = contents_crud.delete_parascriptural(db_=db_,delitem=parascript_id,\
        table_name=tb_name,resource_name=resource_name,user_id=user_details['user_id'])
    delcont = structurals_crud.add_deleted_data(db_=db_,del_content= deleted_content['db_content'],
        table_name = dbtable_name, resource = deleted_content['resource_content'],
        deleting_user = user_details['user_id'])
    return {'message': f"Parascriptural id {parascript_id} deleted successfully",
            "data": delcont}

################ Audio Bibles ###################
@router.get('/v2/resources/bible/audios/{resource_name}',
    response_model=List[schema_content.AudioBibleResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}}, status_code=200, tags=["Audio Bibles"])
@get_auth_access_check_decorator
async def get_audio_bibles(request: Request, #pylint: disable=too-many-locals
    resource_name:schemas.TableNamePattern=
    Path(...,example="en_KJV_1_audiobible"),
    name:str=Query(None,example="Audio Bible of Genesis"),
    audio_format:str=Query(None, example="mp3"),
    reference: str = Query(None,
    example='{"book": "gen", "chapter": 1, "verseNumber": 6}'),
    link:AnyUrl=Query(None,example="http://someplace.com/resoucesid"),
    search_word:str=Query(None,example="subtitle"),
    metadata: schemas.MetaDataPattern=Query(None,
        example='{"otherName": "Creation"}'),
    active: bool=Query(True),
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db)):
    '''Fetches the Audio Bibles. Can use, Audio Bible name, audio_format
       reference,link,meatdata or search word to filter the results.
    * optional query parameters can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content
    * Filter with single reference -> eg :{"book": "gen", "chapter": 1, "verseNumber": 6}
    * Filter with cross chapter references -> eg:reference": {"book":"gen", "chapter":11,
        "verseNumber":12,"bookEnd":"luk", "chapterEnd":14, "verseEnd":15 }'''
    log.info('In get_audio_bibles')
    log.debug('resource_name: %s,name: %s, skip: %s,limit: %s,search_word: %s,\
        reference:%s,metadata:%s',resource_name,name,skip,limit,search_word,\
        reference,metadata)
    reference_dict: Dict[str, int] = None
    if reference:
        reference_dict = json.loads(reference)
    return contents_crud.get_audio_bible(db_, resource_name, name,
        audio_format = audio_format, reference = reference_dict, link = link,
        search_word = search_word, metadata = metadata, active = active, skip = skip, limit = limit)

@router.post('/v2/resources/bible/audios/{resource_name}',
    response_model=schema_content.AudioBibleCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Audio Bibles"])
@get_auth_access_check_decorator
async def add_audio_bibles(request: Request,
    resource_name : schemas.TableNamePattern=Path(...,
    example="en_KJV_1_audiobible"),
    audiobibles: List[schema_content.AudioBibleCreate] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    '''Uploads a list of audio_bibles. category field is mandatory'''
    log.info('In add_audio_bibles')
    log.debug('resource_name: %s, audiobibles: %s',resource_name, audiobibles)
    return {'message': "Audio Bibles added successfully",
        "data": contents_crud.upload_audio_bible(db_=db_, resource_name=resource_name,
        audiobibles=audiobibles, user_id=user_details['user_id'])}

@router.put('/v2/resources/bible/audios/{resource_name}',
    response_model=schema_content.AudioBibleUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Audio Bibles"])
@get_auth_access_check_decorator
async def edit_audio_bibles(request: Request,
    resource_name: schemas.TableNamePattern=Path(...,
    example="en_KJV_1_audiobible"),
    audiobibles: List[schema_content.AudioBibleEdit] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    ''' Changes description,reference or link.
    Item identifier is audioId, which cannot be altered.'''
    log.info('In edit_audio_bibles')
    log.debug('resource_name: %s, audiobible: %s',resource_name, audiobibles)
    return {'message': "Audio Bibles updated successfully",
        "data": contents_crud.update_audio_bible(db_=db_, resource_name=resource_name,
        audiobibles=audiobibles, user_id=user_details['user_id'])}

@router.delete('/v2/resources/bible/audios/{resource_name}',
    response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Audio Bibles"])
@get_auth_access_check_decorator
async def delete_audio_bibles(request: Request,
    audio_id:int = Query(..., example=100001),
    resource_name: str = Path(...,example="en_KJV_1_audiobible"),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Delete Audio Bible
    * unique audioId with source name can be used to delete an exisiting identity'''
    log.info('In delete_audio_bibles')
    log.debug('audio_bibles-delete:%s',audio_id)
    tb_name = db_models.dynamicTables[resource_name]
    dbtable_name = tb_name.__name__
    get_audio_response = contents_crud.get_audio_bible(
        db_, resource_name=resource_name, audio_id= audio_id)
    if len( get_audio_response['db_content']) == 0:
        raise NotAvailableException(f"Audio Bible with id {audio_id} not found")
    deleted_content = contents_crud.delete_audio_bible(db_=db_,delitem=audio_id,\
        table_name=tb_name,resource_name=resource_name,user_id=user_details['user_id'])
    delcont = structurals_crud.add_deleted_data(db_=db_,del_content= deleted_content['db_content'],
        table_name = dbtable_name, resource = deleted_content['resource_content'],
        deleting_user = user_details['user_id'])
    return {'message': f"Audio Bible id {audio_id} deleted successfully",
            "data": delcont}

# # ########### Sign Bible Video ###################
@router.get('/v2/resources/bible/videos/{resource_name}',
    response_model=List[schema_content.SignVideoResponse],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}}, status_code=200, tags=["Sign Bible Videos"])
@get_auth_access_check_decorator
async def get_sign_bible_videos(request: Request, #pylint: disable=too-many-locals
    resource_name:schemas.TableNamePattern=
    Path(...,example="ins_KJV_1_signbiblevideo"),
    title:str=Query(None,example="Sign Bible Video of Genesis"),
    description:str=Query(None, example="Origin Chronicles"),
    reference: str = Query(None,
    example='{"book": "gen", "chapter": 1, "verseNumber": 6}'),
    link:AnyUrl=Query(None,example="http://someplace.com/resoucesid"),
    search_word:str=Query(None,example="subtitle"),
    metadata: schemas.MetaDataPattern=Query(None,
        example='{"otherName": "ISL, Indian Sign Language Videos"}'),
    active: bool=Query(True),
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_: Session=Depends(get_db)):
    '''Fetches the sign bible videos. Can use, sign bible video title,description
       reference,link,meatdata or search word to filter the results.
    * optional query parameters can be used to filter the result set
    * skip=n: skips the first n objects in return list
    * limit=n: limits the no. of items to be returned to n
    * returns [] for not available content
    * Filter with single reference -> eg :{"book": "gen", "chapter": 1, "verseNumber": 6}
    * Filter with cross chapter references -> eg:reference": {"book":"gen", "chapter":11,
        "verseNumber":12,"bookEnd":"luk", "chapterEnd":14, "verseEnd":15 }'''
    log.info('In get_sign_bible_video')
    log.debug('resource_name: %s,title: %s, skip: %s,limit: %s,search_word: %s,\
        reference:%s,metadata:%s',resource_name,title,skip,limit,search_word,\
        reference,metadata)
    reference_dict: Dict[str, int] = None
    if reference:
        reference_dict = json.loads(reference)
    return contents_crud.get_sign_bible_videos(db_, resource_name, title,
        description = description, reference = reference_dict, link = link,
        search_word = search_word, metadata = metadata, active = active, skip = skip, limit = limit)

@router.post('/v2/resources/bible/videos/{resource_name}',
    response_model=schema_content.SignVideoCreateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
    415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Sign Bible Videos"])
@get_auth_access_check_decorator
async def add_sign_bible_videos(request: Request,
    resource_name : schemas.TableNamePattern=Path(...,
    example="ins_KJV_1_signbiblevideo"),
    signvideos: List[schema_content.SignVideoCreate] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    '''Uploads a list of sign bible videos. category field is mandatory'''
    log.info('In add_sign_bible_video')
    log.debug('resource_name: %s, signvideos: %s',resource_name, signvideos)
    return {'message': "Sign Bible Videos added successfully",
        "data": contents_crud.upload_sign_bible_videos(db_=db_, resource_name=resource_name,
        signvideos=signvideos, user_id=user_details['user_id'])}

@router.put('/v2/resources/bible/videos/{resource_name}',
    response_model=schema_content.SignVideoUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse}, \
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401:{"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse}},
    status_code=201, tags=["Sign Bible Videos"])
@get_auth_access_check_decorator
async def edit_sign_bible_videos(request: Request,
    resource_name: schemas.TableNamePattern=Path(...,
    example="ins_KJV_1_signbiblevideo"),
    signvideos: List[schema_content.SignVideoEdit] = Body(...),
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    ''' Changes description,reference or link.
    Item identifier is signvideoId, which cannot be altered.'''
    log.info('In edit_sign_bible_videos')
    log.debug('resource_name: %s, signvideo: %s',resource_name, signvideos)
    return {'message': "Sign Bible Videos updated successfully",
        "data": contents_crud.update_sign_bible_videos(db_=db_, resource_name=resource_name,
        signvideos = signvideos, user_id=user_details['user_id'])}

@router.delete('/v2/resources/bible/videos/{resource_name}',
    response_model=schemas.DeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Sign Bible Videos"])
@get_auth_access_check_decorator
async def delete_sign_bible_videos(request: Request,
    signvideo_id:int = Query(..., example=100001),
    resource_name: str = Path(...,example="ins_KJV_1_signbiblevideo"),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Delete Sign Bible Video
    * unique signvideoId with source name can be used to delete an exisiting identity'''
    log.info('In delete_sign_bible_videos')
    log.debug('sign_bible_videos-delete:%s',signvideo_id)
    tb_name = db_models.dynamicTables[resource_name]
    dbtable_name = tb_name.__name__
    get_signvideo_response = contents_crud.get_sign_bible_videos(
        db_, resource_name=resource_name, signvideo_id= signvideo_id)
    if len( get_signvideo_response['db_content']) == 0:
        raise NotAvailableException(f"Sign Bible Video with id {signvideo_id} not found")
    deleted_content = contents_crud.delete_sign_bible_videos(db_=db_,delitem=signvideo_id,\
        table_name=tb_name,resource_name=resource_name,user_id=user_details['user_id'])
    delcont = structurals_crud.add_deleted_data(db_=db_,del_content= deleted_content['db_content'],
        table_name = dbtable_name, resource = deleted_content['resource_content'],
        deleting_user = user_details['user_id'])
    return {'message': f"Sign Bible Video id {signvideo_id} deleted successfully",
            "data": delcont}

@router.get('/v2/resources/get-sentence', response_model=List[schemas_nlp.SentenceInput],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Resources"])
@get_auth_access_check_decorator
async def extract_text_contents(request:Request, #pylint: disable=W0613
    resource_name:schemas.TableNamePattern=Query(None,example="en_TBP_1_bible"),
    books:List[schemas.BookCodePattern]=Query(None,example='GEN'),
    language_code:schemas.LangCodePattern=Query(None, example="hi"),
    resource_type:str=Query(None, example="commentary"),
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

#### Data Manipulation ####
@router.put('/v2/admin/restore', response_model=schemas.DataRestoreResponse,
    responses={502:{"model":schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse}, 404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=201, tags=["Data Manipulation"])
@get_auth_access_check_decorator
async def restore_content(request: Request, content: schemas.RestoreIdentity,
    user_details =Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    ''' Restore deleted data to the original table.
    * Unique deleted item ID can be used to restore data'''
    log.info('In restore_content')
    log.debug('restore: %s',content)
    if len(structurals_crud.get_restore_item_id(db_, restore_item_id= content.itemId)) == 0:
        raise NotAvailableException(f"Restore item id {content.itemId} not found")
    data = structurals_crud.restore_data(db_=db_, restored_item=content)
    data = jsonpickle.encode(data)
    data=json.loads(data)
    del data['py/object'],data['_sa_instance_state']
    return {'message': f"Deleted Item with identity {content.itemId} restored successfully",
    "data": data}

@router.delete('/v2/admin/cleanup',response_model=schemas.CleanupDB,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse}, \
    502: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Data Manipulation"])
@get_auth_access_check_decorator
async def delete_deleteditems(request: Request,user_details =Depends(get_user_or_none), \
    db_: Session = Depends(get_db)):
    '''Periodic Cleaning of Database
    * Clearing deleted_items table
    * Delete dangling dynamic tables whose resource does not exist in resources table '''
    log.info('In delete_deleteditems')
    deleted_item_count = structurals_crud.cleanup_database(db_=db_)
    return {'message': "Database cleanup done!!",'deletedItemCount':deleted_item_count}
