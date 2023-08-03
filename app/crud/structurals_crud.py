''' Place to define all Database CRUD operations for tables
Content_types, Languages, Licenses, versions, resources and bible_book_loopup'''

import json
import re
from datetime import datetime
import jsonpickle
from pytz import timezone
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import array
from sqlalchemy import MetaData
import db_models
from schema import schemas
from custom_exceptions import NotAvailableException, TypeException, AlreadyExistsException
from database import engine
from dependencies import log
from crud import utils

ist_timezone = timezone("Asia/Kolkata")
def get_resource_types(db_: Session, resource_type: str =None, resourcetype_id: int = None,
    skip: int = 0, limit: int = 100):
    '''Fetches all resource types, with pagination'''
    query = db_.query(db_models.ResourceType)
    if resource_type:
        query = query.filter(db_models.ResourceType.resourceType == resource_type)
    if resourcetype_id is not None:
        query = query.filter(db_models.ResourceType.resourcetypeId == resourcetype_id)
    return query.offset(skip).limit(limit).all()

def create_resource_types(db_: Session, resourcetype: schemas.ResourceTypeCreate,user_id=None):
    '''Adds a row to resource_types table'''
    db_resourcetype = db_models.ResourceType(resourceType = resourcetype.resourceType,
                                             createdUser= user_id)
    db_.add(db_resourcetype)
    # db_.commit()
    # db_.refresh(db_content)
    return db_resourcetype

def delete_resource_types(db_: Session, resourcetype:int):
    '''delete particular resource_types, selected via resource_type id'''
    db_resourcetype = db_.query(db_models.ResourceType).get(resourcetype)
    db_.delete(db_resourcetype)
    #db_.commit()
    return db_resourcetype

def get_languages(db_: Session, language_code = None, language_name = None, search_word=None,
    language_id = None, **kwargs):
    '''Fetches rows of language, with pagination and various filters'''
    localscript_name = kwargs.get("localscript_name",None)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.Language)
    if language_code:
        query = query.filter(func.lower(db_models.Language.code) == language_code.lower())
    if language_name:
        query = query.filter(func.lower(db_models.Language.language) == language_name.lower())
    if search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text("to_tsvector('simple', language_code || ' ' ||"+\
            " language_name || ' ' || "+\
            "jsonb_to_tsvector('simple', metadata, '[\"string\", \"numeric\"]') || ' ')"+\
            " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))
    if localscript_name:
        query = query.filter(db_models.Language.localScriptName == localscript_name)
    if language_id is not None:
        query = query.filter(db_models.Language.languageId == language_id)
    return query.offset(skip).limit(limit).all()

def create_language(db_: Session, lang: schemas.LanguageCreate, user_id=None):
    '''Adds a row to languages table'''
    valid, message = utils.validate_language_tag(lang.code)
    if not valid:
        raise TypeException(f"{lang.code} is not a valid BCP 47 tag. {message}."+\
            "Refer https://tools.ietf.org/html/bcp47.")
    db_content = db_models.Language(code = lang.code,
        language = lang.language.lower(),
        scriptDirection = lang.scriptDirection,
        localScriptName = lang.localScriptName,
        metaData = lang.metaData,
        createdUser= user_id,
        updatedUser=user_id)
    db_.add(db_content)
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

def update_language(db_: Session, lang: schemas.LanguageEdit, user_id=None):
    '''changes one or more fields of language, selected via language id'''
    db_content = db_.query(db_models.Language).get(lang.languageId)
    if lang.code:
        valid, message = utils.validate_language_tag(lang.code)
        if not valid:
            raise TypeException(f"{lang.code} is not a valid BCP 47 tag. {message}."+\
                "Refer https://tools.ietf.org/html/bcp47.")
        db_content.code = lang.code
    if lang.language:
        db_content.language = lang.language
    if lang.scriptDirection:
        db_content.scriptDirection = lang.scriptDirection
    if lang.localScriptName:
        db_content.localScriptName = lang.localScriptName
    if lang.metaData:
        db_content.metaData = lang.metaData
        flag_modified(db_content, "metaData")
    db_content.updatedUser = user_id
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

def add_deleted_data(db_: Session, del_content, table_name : str = None,\
    resource = None,deleting_user=None):
    '''backup deleted items from any table'''
    if hasattr(del_content, 'createTime') and del_content.createTime is not None:
        del_content.createTime = del_content.createTime.isoformat()
    if hasattr(del_content, 'updateTime') and del_content.updateTime is not None:
        del_content.updateTime = del_content.updateTime.isoformat()
    json_string = jsonpickle.encode(del_content)#, unpicklable=False
    json_string=json.loads(json_string)
    del json_string['py/object'],json_string['_sa_instance_state']
    del_item_createduser = deleting_user
    db_content =  db_models.DeletedItem(deletedData = json_string,
        createdUser = del_item_createduser,
        deletedTime=datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M:%S'),
        deletedFrom = table_name)
    db_.add(db_content)

    if resource is not None:
        response =  {
            'db_content':db_content,
            'resource_content': resource
                }
    else:
        response =  {
        'db_content':db_content,
        'resource_content':del_content
            }
    return response

def get_restore_item_id(db_: Session, restore_item_id = None, **kwargs):
    '''Fetches row of deleted item'''
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.DeletedItem)
    if restore_item_id is not None:
        query = query.filter(db_models.DeletedItem.itemId == restore_item_id)
    return query.offset(skip).limit(limit).all()

def restore_data(db_: Session, restored_item :schemas.RestoreIdentity):
    '''Restore deleted record back to the original table'''
    db_restore = db_.query(db_models.DeletedItem).get(restored_item.itemId)
    db_content=db_restore
    json_string = db_content.deletedData

    content_class_map = {
        "languages":db_models.Language,
        "licenses":db_models.License,
        "versions":db_models.Version,
        "resource_types": db_models.ResourceType,
        "resources":db_models.Resource,
        "translation_projects":db_models.TranslationProject,
        "translation_project_users": db_models.TranslationProjectUser,
        "translation_sentences": db_models.TranslationDraft,
        "translation_memory": db_models.TranslationMemory,
        "stopwords_look_up": db_models.StopWords}
    if db_restore.deletedFrom in content_class_map:
        model_cls = content_class_map[db_restore.deletedFrom]
    else:
        if db_restore.deletedFrom.endswith("audio"):
            renamed_table = db_restore.deletedFrom.replace("_audio", "")
            if not  get_resources(db_, table_name = renamed_table):
                raise NotAvailableException('Resource not found in database')
        elif db_restore.deletedFrom.endswith("cleaned"):
            renamed_table = db_restore.deletedFrom.replace("_cleaned", "")
            if not  get_resources(db_, table_name = renamed_table):
                raise NotAvailableException('Resource not found in database')
        if db_restore.deletedFrom.endswith(("audio","cleaned")) is False:
            if not  get_resources(db_, table_name=db_restore.deletedFrom):
                raise NotAvailableException('Resource not found in database')
            resource = get_resources(db_, table_name=db_restore.deletedFrom)[0]
            resource_name = resource.resourceName
            if resource_name.endswith("bible") is False:
                model_cls = db_models.dynamicTables[resource.resourceName]
            else:
                model_cls = db_models.dynamicTables[resource.resourceName]
                resource_table = db_restore.deletedFrom.replace("_cleaned", "")
                resource = get_resources(db_, table_name=resource_table)[0]
                model_cls2 = db_models.dynamicTables[resource.resourceName+'_cleaned']
                # cleanedtable_itemid = db_content.itemId + 1
                db_restore2 = db_.query(db_models.DeletedItem).get(db_content.itemId + 1)
                db_content2=db_restore2
                json_string2 = db_content2.deletedData
                db_content2 = utils.convert_dict_to_sqlalchemy(json_string2, model_cls2)
                db_.add(db_content2)
                db_.delete(db_restore2)
        else:
            resource_table = db_restore.deletedFrom.replace("_audio", "")
            resource = get_resources(db_, table_name=resource_table)[0]
            model_cls = db_models.dynamicTables[resource.resourceName+'_audio']
    db_content = utils.convert_dict_to_sqlalchemy(json_string, model_cls)
    db_.add(db_content)
    db_.delete(db_restore)
    #db_.commit()
    return db_content

def delete_language(db_: Session, lang:int):
    '''delete particular language, selected via language id'''
    db_content = db_.query(db_models.Language).get(lang)
    db_.delete(db_content)
    #db_.commit()
    return db_content

def get_licenses(db_: Session, license_code = None, license_name = None,
    permission = None, active=True, **kwargs):
    '''Fetches rows of licenses, with pagination and various filters'''
    license_id = kwargs.get("license_id",None)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.License)
    if license_code:
        query = query.filter(db_models.License.code == license_code.upper())
    if license_name:
        query = query.filter(db_models.License.name == license_name.strip())
    if license_id is not None:
        query = query.filter(db_models.License.licenseId == license_id)
    if permission is not None:
        query = query.filter(db_models.License.permissions.any(permission))
    return query.filter(db_models.License.active == active).offset(skip).limit(limit).all()

def create_license(db_: Session, license_obj: schemas.LicenseCreate, user_id=None):
    '''Adds a new license to Database'''
    db_content = db_models.License(code = license_obj.code.upper(),
        name = license_obj.name.strip(),
        license = utils.normalize_unicode(license_obj.license),
        permissions = license_obj.permissions,
        active=True,
        createdUser=user_id)
    db_.add(db_content)
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

def update_license(db_: Session, license_obj: schemas.LicenseEdit, user_id=None):
    '''changes one or more fields of license, selected via license code'''
    db_content = db_.query(db_models.License).filter(
        db_models.License.code == license_obj.code.strip().upper()).first()
    if not db_content:
        raise NotAvailableException(f"License with code, {license_obj.code}, "+\
            "not found in database")
    if license_obj.name:
        db_content.name = license_obj.name
    if license_obj.license:
        db_content.license = utils.normalize_unicode(license_obj.license)
    if license_obj.permissions:
        db_content.permissions = license_obj.permissions
    if license_obj.active is not None:
        db_content.active = license_obj.active
    db_content.updatedUser = user_id
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

def delete_license(db_: Session, content: int):
    '''delete particular license, selected via license id'''
    db_content = db_.query(db_models.License).get(content)
    db_.delete(db_content)
    #db_.commit()
    return db_content

def get_versions(db_: Session, version_abbr = None, version_name = None, version_tag = None,
    metadata = None, **kwargs):
    '''Fetches rows of versions table, with various filters and pagination'''
    version_id = kwargs.get("version_id",None)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.Version)
    if version_abbr:
        query = query.filter(db_models.Version.versionAbbreviation == version_abbr.upper().strip())
    if version_name:
        query = query.filter(db_models.Version.versionName == version_name.strip())
    if version_tag:
        version_array = version_tag_to_array(version_tag)
        query = query.filter(db_models.Version.versionTag == version_array)
    if metadata:
        meta = json.loads(metadata)
        for key in meta:
            query = query.filter(db_models.Version.metaData.op('->>')(key) == meta[key])
    if version_id:
        query = query.filter(db_models.Version.versionId == version_id)
    return query.offset(skip).limit(limit).all()

def version_tag_to_array(tag_str):
    '''converts "2022.1.11" to [2022, 1, 11, 0]. Used for writing to and querying DB'''
    if tag_str is None:
        tag_str = "1"
    tag_str = str(tag_str)
    split_tag = tag_str.split(".")
    return split_tag

def version_array_to_tag(tag_array):
    '''converts [2022, 1, 11, 0] to "2022.1.11". Used for naming resource and response'''
    tag_str = ""
    tag_str = ".".join(tag_array)
    return tag_str


def create_version(db_: Session, version: schemas.VersionCreate,user_id=None):
    '''Adds a row to versions table'''
    if version.versionTag is None:
        version.versionTag = "1.0.0"
    version_array = version_tag_to_array(version.versionTag)
    db_content = db_models.Version(
        versionAbbreviation = version.versionAbbreviation.upper().strip(),
        versionName = utils.normalize_unicode(version.versionName.strip()),
        versionTag = version_array,
        metaData = version.metaData,
        createdUser=user_id)
    db_.add(db_content)
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

def update_version(db_: Session, version: schemas.VersionEdit, user_id=None):
    '''changes one or more fields of versions, selected via version id'''
    db_content = db_.query(db_models.Version).get(version.versionId)
    if version.versionAbbreviation:
        db_content.versionAbbreviation = version.versionAbbreviation
    if version.versionName:
        db_content.versionName = utils.normalize_unicode(version.versionName)
    if version.versionTag:
        version_array = version_tag_to_array(version.versionTag)
        db_content.versionTag = version_array
    if version.metaData:
        db_content.metaData = version.metaData
    db_content.updatedUser = user_id
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

def delete_version(db_: Session, ver: int):
    '''delete particular version, selected via version id'''
    db_content = db_.query(db_models.Version).get(ver)
    db_.delete(db_content)
    #db_.commit()
    return db_content

def get_resources(db_: Session,#pylint: disable=too-many-locals,too-many-branches,too-many-nested-blocks, too-many-statements,too-many-arguments
    resource_type=None, version_abbreviation=None, version_tag=None, language_code=None,
    resource_id=None, **kwargs):
    '''Fetches the rows of resources table'''
    license_abbreviation = kwargs.get("license_abbreviation",None)
    metadata = kwargs.get("metadata",None)
    access_tags = kwargs.get("access_tag",None)
    latest_revision = kwargs.get("latest_revision",True)
    labels = kwargs.get("labels", [])
    active = kwargs.get("active",True)
    resource_name = kwargs.get("resource_name",None)
    table_name = kwargs.get("table_name",None)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.Resource)
    if resource_id:
        query = query.filter(db_models.Resource.resourceId == resource_id)
    if resource_type:
        query = query.filter(db_models.Resource.resourceType.has
        (resourceType = resource_type.strip()))
    if version_abbreviation:
        query = query.filter(
            db_models.Resource.version.has(versionAbbreviation = version_abbreviation.strip()))
    if version_tag:
        version_array = version_tag_to_array(version_tag)
        query = query.filter(
            db_models.Resource.version.has(versionTag = version_array))
    if license_abbreviation:
        query = query.filter(db_models.Resource.license.has(code = license_abbreviation.strip()))
    if language_code:
        query = query.filter(db_models.Resource.language.has(code = language_code.strip()))
    if metadata:
        meta = json.loads(metadata)
        for key in meta:
            query = query.filter(db_models.Resource.metaData.op('->>')(key) == meta[key])
    if labels:
        for label in labels:
            query = query.filter(db_models.Resource.labels.contains(label.value()))
    if active:
        query = query.filter(db_models.Resource.active)
    else:
        query = query.filter(db_models.Resource.active == False) #pylint: disable=singleton-comparison
    if resource_name:
        query = query.filter(db_models.Resource.resourceName == resource_name)
    if table_name:
        query = query.filter(db_models.Resource.tableName == table_name)
    if access_tags:
        query = query.filter(db_models.Resource.metaData.contains(
            {"accessPermissions":[tag.value for tag in access_tags]}))
    res = query.all()
    def digits_to_int(string):
        '''to convert number strings to int for sorting'''
        if re.match(r'^\d+$', string):
            return int(string)
        return string
    version_tags = []
    for res_item in res:
        converted_tag = [digits_to_int(part) for part in res_item.version.versionTag]
        version_tags.append((res_item.resourceType.resourceType, res_item.language.language,
         res_item.version.versionAbbreviation,
         converted_tag, res_item))
    sorted_res =[res_tuple[4] for res_tuple in sorted(version_tags, reverse=True)]

    if not latest_revision or version_tag is not None:
        sorted_res = sorted_res[skip:]
        if limit < len(sorted_res):
            sorted_res = sorted_res[:limit]
        return sorted_res

    # Take only the top most in each version, unless there is a differnt "latest"
    latest_res = {}
    for item in sorted_res:
        key_name = "_".join([item.language.code,
            item.version.versionAbbreviation,
            item.resourceType.resourceType])
        if key_name not in latest_res:
            latest_res[key_name] = item
        elif item.labels and schemas.ResourceLabel.LATEST in item.labels:
            latest_res[key_name] = item
    filtered_res = list(latest_res.values())
    filtered_res = filtered_res[skip:]
    if limit < len(filtered_res):
        filtered_res = filtered_res[:limit]

    return filtered_res

def create_resource(db_: Session, resource: schemas.ResourceCreate, user_id):
    '''Adds a row to resources table'''
    version_array = version_tag_to_array(resource.versionTag)
    resource_name = "_".join([resource.language, resource.version,
        version_array_to_tag(version_array), resource.resourceType])
    if len(get_resources(db_, resource_name = resource_name)) > 0:
        raise AlreadyExistsException(f"{resource_name} already present")
    resource_type = db_.query(db_models.ResourceType).filter(
        db_models.ResourceType.resourceType == resource.resourceType.strip()).first()
    if not resource_type:
        raise NotAvailableException(f"ResourceType, {resource.resourceType.strip()},"+\
            " not found in Database")
    version = db_.query(db_models.Version).filter(
        db_models.Version.versionAbbreviation == resource.version,
        db_models.Version.versionTag == version_array).first()
    if not version:
        raise NotAvailableException(f"Version, {resource.version} {resource.versionTag},"+\
            " not found in Database")
    language = db_.query(db_models.Language).filter(
        db_models.Language.code == resource.language).first()
    if not language:
        raise NotAvailableException(f"Language code, {resource.language}, not found in Database")
    license_obj = db_.query(db_models.License).filter(
        db_models.License.code == resource.license).first()
    if not license_obj:
        raise NotAvailableException(f"License code, {resource.license}, not found in Database")
    if resource.labels and schemas.ResourceLabel.LATEST in resource.labels:
        query = db_.query(db_models.Resource).join(db_models.Version).filter(
            db_models.Resource.version.has(versionAbbreviation = resource.version),
            db_models.Resource.resourcetypeId == resource_type.resourcetypeId,
            db_models.Resource.labels.op('&&')(array(schemas.ResourceLabel.LATEST.value)))
        another_latest = query.all()
        if another_latest:
            raise AlreadyExistsException(
                f"Another resource with latest tag exists: {another_latest[0].resourceName}")
    table_name_count = 0
    dynamic_tablename_pattern = re.compile(r"table_\d+$")
    for table_name in engine.table_names():
        if (re.match(dynamic_tablename_pattern, table_name) and
            int(table_name.split("_")[-1]) > table_name_count):
            table_name_count = int(table_name.split("_")[-1])
    table_name = "table_"+str(table_name_count+1)
    if resource_type.resourceType == db_models.ResourceTypeName.GITLABREPO.value:
        table_name = resource.metaData["repo"]
    db_content = db_models.Resource(
        year = resource.year,
        labels = resource.labels,
        resourceName = resource_name,
        tableName = table_name,
        resourcetypeId = resource_type.resourcetypeId,
        versionId = version.versionId,
        languageId = language.languageId,
        licenseId = license_obj.licenseId,
        metaData = resource.metaData,
        active = True,
        )
    db_content.createdUser = user_id
    db_.add(db_content)
    if not resource_type.resourceType == db_models.ResourceTypeName.GITLABREPO.value:
        db_models.create_dynamic_table(resource_name, table_name, resource_type.resourceType)
        db_models.dynamicTables[db_content.resourceName].\
            __table__.create(bind=engine, checkfirst=True)
    if resource_type.resourceType == db_models.ResourceTypeName.BIBLE.value:
        db_models.dynamicTables[db_content.resourceName+'_cleaned'].__table__.create(
            bind=engine, checkfirst=True)
        log.warning("User %s, creates a new table %s", user_id, db_content.resourceName+'_cleaned')
        db_models.dynamicTables[db_content.resourceName+'_audio'].__table__.create(
            bind=engine, checkfirst=True)
        log.warning("User %s, creates a new table %s", user_id, db_content.resourceName+'_audio')
    log.warning("User %s, creates a new table %s", user_id, db_content.resourceName)
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

def update_resource_resourcename(db_, resource, db_content):
    """update sourcename of resource table"""
    if resource.version:
        ver = resource.version
    else:
        ver = db_content.version.versionAbbreviation
    if resource.versionTag:
        version_array = version_tag_to_array(resource.versionTag)
    else:
        version_array = db_content.version.versionTag
    rev = version_array_to_tag(version_array)
    version = db_.query(db_models.Version).filter(
        db_models.Version.versionAbbreviation == ver,
        db_models.Version.versionTag == version_array).first()
    if not version:
        raise NotAvailableException(f"Version, {ver} {rev}, not found in Database")
    db_content.versionId = version.versionId
    table_name_parts = db_content.resourceName.split("_")
    db_content.resourceName = "_".join([table_name_parts[0],ver, rev, table_name_parts[-1]])
    return db_content

def update_resource(db_: Session, resource: schemas.ResourceEdit, user_id = None): #pylint: disable=too-many-branches
    '''changes one or more fields of sources, selected via resourceName or table_name'''
    db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource.resourceName).first()
    if resource.version or resource.versionTag:
        db_content =  update_resource_resourcename(db_, resource, db_content)

    if resource.language:
        language = db_.query(db_models.Language).filter(
            db_models.Language.code == resource.language).first()
        if not language:
            raise NotAvailableException(
    f"Language code, {resource.language}, not found in Database")
        db_content.languageId = language.languageId
        resource_name_parts = db_content.resourceName.split("_")
        db_content.resourceName = "_".join([resource.language]+resource_name_parts[1:])
    if resource.license:
        license_obj = db_.query(db_models.License).filter(
            db_models.License.code == resource.license).first()
        if not license_obj:
            raise NotAvailableException(f"License code, {resource.license}, not found in Database")
        db_content.licenseId = license_obj.licenseId
    if resource.labels is not None:
        if schemas.ResourceLabel.LATEST in resource.labels:
            query = db_.query(db_models.Resource).join(db_models.Version).filter(
                db_models.Resource.version.has(
                    versionAbbreviation = db_content.version.versionAbbreviation),
                db_models.Resource.resourcetypeId == db_content.resourcetypeId,
                db_models.Resource.labels.op('&&')(array(schemas.ResourceLabel.LATEST.value)),
                db_models.Resource.resourceId != db_content.resourceId)
            another_latest = query.all()
            if another_latest:
                raise AlreadyExistsException(
                    f"Another resource with latest tag exists: {another_latest[0].resourceName}")
        db_content.labels = resource.labels
    if resource.year:
        db_content.year = resource.year
    if resource.metaData:
        db_content.metaData = resource.metaData
    if resource.active is not None:
        db_content.active = resource.active
    db_content.updatedUser = user_id
    # db_.commit()
    # db_.refresh(db_content)
    if not resource.resourceName.split("_")[-1] == db_models.ResourceTypeName.GITLABREPO.value:
        db_models.dynamicTables[db_content.resourceName] = \
        db_models.dynamicTables[resource.resourceName]
        if resource.resourceName.split("_")[-1] == 'bible':
            db_models.dynamicTables[db_content.resourceName+'_cleaned'] = \
                db_models.dynamicTables[resource.resourceName+'_cleaned']
            db_models.dynamicTables[db_content.resourceName+'_audio'] = \
                db_models.dynamicTables[resource.resourceName+'_audio']
    return db_content

def delete_resource(db_: Session, delitem: int):
    '''delete particular resource, selected via resource id'''
    db_content = db_.query(db_models.Resource).get(delitem)
    db_.delete(db_content)
    return db_content

def get_bible_books(db_:Session, book_id=None, book_code=None, book_name=None,
    **kwargs):
    '''Fetches rows of bible_books_lookup, with pagination and various filters'''
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.BibleBook)
    if book_id:
        query = query.filter(db_models.BibleBook.bookId == book_id)
    if book_code:
        query = query.filter(db_models.BibleBook.bookCode == book_code.lower())
    if book_name is not None:
        query = query.filter(db_models.BibleBook.bookName == book_name.lower())
    return query.offset(skip).limit(limit).all()

def cleanup_database(db_: Session):
    '''Periodic cleanup of database'''
    metadata = MetaData(bind=engine)
    metadata.reflect()
    for table_name in metadata.tables:
        if table_name.startswith('table'):
            if table_name.endswith("audio"):
                tb_name = table_name.replace("_audio", "")
            elif table_name.endswith("cleaned"):
                tb_name = table_name.replace("_cleaned", "")
            else:
                tb_name = table_name
            if not  get_resources(db_, table_name = tb_name):
                with engine.connect() as conn:
                    conn.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
    deleteditem_count = db_.query(db_models.DeletedItem).delete()
    return deleteditem_count
