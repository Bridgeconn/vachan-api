''' Place to define all Database CRUD operations for tables
Content_types, Languages, Licenses, versions, sources and bible_book_loopup'''

import json
import re
from datetime import datetime
import jsonpickle
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import array
import db_models
from schema import schemas
from custom_exceptions import NotAvailableException, TypeException, AlreadyExistsException
from database import engine
from dependencies import log
from crud import utils

def get_content_types(db_: Session, content_type: str =None, content_id: int = None,
    skip: int = 0, limit: int = 100):
    '''Fetches all content types, with pagination'''
    query = db_.query(db_models.ContentType)
    if content_type:
        query = query.filter(db_models.ContentType.contentType == content_type)
    if content_id is not None:
        query = query.filter(db_models.ContentType.contentId == content_id)
    return query.offset(skip).limit(limit).all()

def create_content_type(db_: Session, content: schemas.ContentTypeCreate,user_id=None):
    '''Adds a row to content_types table'''
    db_content = db_models.ContentType(contentType = content.contentType,createdUser= user_id)
    db_.add(db_content)
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

def delete_content(db_: Session, content: schemas.DeleteIdentity):
    '''delete particular content, selected via content id'''
    db_content = db_.query(db_models.ContentType).get(content.itemId)
    db_.delete(db_content)
    #db_.commit()
    return db_content

def get_languages(db_: Session, language_code = None, language_name = None, search_word=None,
    language_id = None, **kwargs):
    '''Fetches rows of language, with pagination and various filters'''
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
    if lang.metaData:
        db_content.metaData = lang.metaData
        flag_modified(db_content, "metaData")
    db_content.updatedUser = user_id
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

def add_deleted_data(db_: Session, del_content, table_name : str = None,\
    source = None,deleting_user=None):
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
        deletedTime = datetime.now(),
        deletedFrom = table_name)
    db_.add(db_content)

    if source is not None:
        response =  {
            'db_content':db_content,
            'source_content': source
                }
    else:
        response =  {
        'db_content':db_content,
        'source_content':del_content
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
        "content_types": db_models.ContentType,
        "sources":db_models.Source,
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
            if not  get_sources(db_, table_name = renamed_table):
                raise NotAvailableException('Source not found in database')
        elif db_restore.deletedFrom.endswith("cleaned"):
            renamed_table = db_restore.deletedFrom.replace("_cleaned", "")
            if not  get_sources(db_, table_name = renamed_table):
                raise NotAvailableException('Source not found in database')
        if db_restore.deletedFrom.endswith(("audio","cleaned")) is False:
            if not  get_sources(db_, table_name=db_restore.deletedFrom):
                raise NotAvailableException('Source not found in database')
            source = get_sources(db_, table_name=db_restore.deletedFrom)[0]
            source_name = source.sourceName
            if source_name.endswith("bible") is False:
                model_cls = db_models.dynamicTables[source.sourceName]
            else:
                model_cls = db_models.dynamicTables[source.sourceName]
                source_table = db_restore.deletedFrom.replace("_cleaned", "")
                source = get_sources(db_, table_name=source_table)[0]
                model_cls2 = db_models.dynamicTables[source.sourceName+'_cleaned']
                # cleanedtable_itemid = db_content.itemId + 1
                db_restore2 = db_.query(db_models.DeletedItem).get(db_content.itemId + 1)
                db_content2=db_restore2
                json_string2 = db_content2.deletedData
                db_content2 = utils.convert_dict_to_sqlalchemy(json_string2, model_cls2)
                db_.add(db_content2)
                db_.delete(db_restore2)
        else:
            source_table = db_restore.deletedFrom.replace("_audio", "")
            source = get_sources(db_, table_name=source_table)[0]
            model_cls = db_models.dynamicTables[source.sourceName+'_audio']
    db_content = utils.convert_dict_to_sqlalchemy(json_string, model_cls)
    db_.add(db_content)
    db_.delete(db_restore)
    #db_.commit()
    return db_content

def delete_language(db_: Session, lang: schemas.DeleteIdentity):
    '''delete particular language, selected via language id'''
    db_content = db_.query(db_models.Language).get(lang.itemId)
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

def delete_license(db_: Session, content: schemas.DeleteIdentity):
    '''delete particular license, selected via license id'''
    db_content = db_.query(db_models.License).get(content.itemId)
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
    '''converts [2022, 1, 11, 0] to "2022.1.11". Used for naming source and response'''
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

def delete_version(db_: Session, ver: schemas.DeleteIdentity):
    '''delete particular version, selected via version id'''
    db_content = db_.query(db_models.Version).get(ver.itemId)
    db_.delete(db_content)
    #db_.commit()
    return db_content

def get_sources(db_: Session,#pylint: disable=too-many-locals,too-many-branches,too-many-nested-blocks, too-many-statements,too-many-arguments
    content_type=None, version_abbreviation=None, version_tag=None, language_code=None,
    source_id=None, **kwargs):
    '''Fetches the rows of sources table'''
    license_abbreviation = kwargs.get("license_abbreviation",None)
    metadata = kwargs.get("metadata",None)
    access_tags = kwargs.get("access_tag",None)
    latest_revision = kwargs.get("latest_revision",True)
    labels = kwargs.get("labels", [])
    active = kwargs.get("active",True)
    source_name = kwargs.get("source_name",None)
    table_name = kwargs.get("table_name",None)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.Source)
    if source_id:
        query = query.filter(db_models.Source.sourceId == source_id)
    if content_type:
        query = query.filter(db_models.Source.contentType.has
        (contentType = content_type.strip()))
    if version_abbreviation:
        query = query.filter(
            db_models.Source.version.has(versionAbbreviation = version_abbreviation.strip()))
    if version_tag:
        version_array = version_tag_to_array(version_tag)
        query = query.filter(
            db_models.Source.version.has(versionTag = version_array))
    if license_abbreviation:
        query = query.filter(db_models.Source.license.has(code = license_abbreviation.strip()))
    if language_code:
        query = query.filter(db_models.Source.language.has(code = language_code.strip()))
    if metadata:
        meta = json.loads(metadata)
        for key in meta:
            query = query.filter(db_models.Source.metaData.op('->>')(key) == meta[key])
    if labels:
        for label in labels:
            query = query.filter(db_models.Source.labels.contains(label.value()))
    if active:
        query = query.filter(db_models.Source.active)
    else:
        query = query.filter(db_models.Source.active == False) #pylint: disable=singleton-comparison
    if source_name:
        query = query.filter(db_models.Source.sourceName == source_name)
    if table_name:
        query = query.filter(db_models.Source.tableName == table_name)
    if access_tags:
        query = query.filter(db_models.Source.metaData.contains(
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
        version_tags.append((res_item.contentType.contentType, res_item.language.language,
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
            item.contentType.contentType])
        if key_name not in latest_res:
            latest_res[key_name] = item
        elif item.labels and schemas.SourceLabel.LATEST in item.labels:
            latest_res[key_name] = item
    filtered_res = list(latest_res.values())
    filtered_res = filtered_res[skip:]
    if limit < len(filtered_res):
        filtered_res = filtered_res[:limit]

    return filtered_res

def create_source(db_: Session, source: schemas.SourceCreate, user_id):
    '''Adds a row to sources table'''
    version_array = version_tag_to_array(source.versionTag)
    source_name = "_".join([source.language, source.version,
        version_array_to_tag(version_array), source.contentType])
    if len(get_sources(db_, source_name = source_name)) > 0:
        raise AlreadyExistsException(f"{source_name} already present")
    content_type = db_.query(db_models.ContentType).filter(
        db_models.ContentType.contentType == source.contentType.strip()).first()
    if not content_type:
        raise NotAvailableException(f"ContentType, {source.contentType.strip()},"+\
            " not found in Database")
    version = db_.query(db_models.Version).filter(
        db_models.Version.versionAbbreviation == source.version,
        db_models.Version.versionTag == version_array).first()
    if not version:
        raise NotAvailableException(f"Version, {source.version} {source.versionTag},"+\
            " not found in Database")
    language = db_.query(db_models.Language).filter(
        db_models.Language.code == source.language).first()
    if not language:
        raise NotAvailableException(f"Language code, {source.language}, not found in Database")
    license_obj = db_.query(db_models.License).filter(
        db_models.License.code == source.license).first()
    if not license_obj:
        raise NotAvailableException(f"License code, {source.license}, not found in Database")
    if source.labels and schemas.SourceLabel.LATEST in source.labels:
        query = db_.query(db_models.Source).join(db_models.Version).filter(
            db_models.Source.version.has(versionAbbreviation = source.version),
            db_models.Source.contentId == content_type.contentId,
            db_models.Source.labels.op('&&')(array(schemas.SourceLabel.LATEST.value)))
        another_latest = query.all()
        if another_latest:
            raise AlreadyExistsException(
                f"Another source with latest tag exists: {another_latest[0].sourceName}")
    table_name_count = 0
    dynamic_tablename_pattern = re.compile(r"table_\d+$")
    for table_name in engine.table_names():
        if (re.match(dynamic_tablename_pattern, table_name) and
            int(table_name.split("_")[-1]) > table_name_count):
            table_name_count = int(table_name.split("_")[-1])
    table_name = "table_"+str(table_name_count+1)
    if content_type.contentType == db_models.ContentTypeName.GITLABREPO.value:
        table_name = source.metaData["repo"]
    db_content = db_models.Source(
        year = source.year,
        labels = source.labels,
        sourceName = source_name,
        tableName = table_name,
        contentId = content_type.contentId,
        versionId = version.versionId,
        languageId = language.languageId,
        licenseId = license_obj.licenseId,
        metaData = source.metaData,
        active = True,
        )
    db_content.createdUser = user_id
    db_.add(db_content)
    if not content_type.contentType == db_models.ContentTypeName.GITLABREPO.value:
        db_models.create_dynamic_table(source_name, table_name, content_type.contentType)
        db_models.dynamicTables[db_content.sourceName].\
            __table__.create(bind=engine, checkfirst=True)
    if content_type.contentType == db_models.ContentTypeName.BIBLE.value:
        db_models.dynamicTables[db_content.sourceName+'_cleaned'].__table__.create(
            bind=engine, checkfirst=True)
        log.warning("User %s, creates a new table %s", user_id, db_content.sourceName+'_cleaned')
        db_models.dynamicTables[db_content.sourceName+'_audio'].__table__.create(
            bind=engine, checkfirst=True)
        log.warning("User %s, creates a new table %s", user_id, db_content.sourceName+'_audio')
    log.warning("User %s, creates a new table %s", user_id, db_content.sourceName)
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

def update_source_sourcename(db_, source, db_content):
    """update sourcename of source table"""
    if source.version:
        ver = source.version
    else:
        ver = db_content.version.versionAbbreviation
    if source.versionTag:
        version_array = version_tag_to_array(source.versionTag)
    else:
        version_array = db_content.version.versionTag
    rev = version_array_to_tag(version_array)
    version = db_.query(db_models.Version).filter(
        db_models.Version.versionAbbreviation == ver,
        db_models.Version.versionTag == version_array).first()
    if not version:
        raise NotAvailableException(f"Version, {ver} {rev}, not found in Database")
    db_content.versionId = version.versionId
    table_name_parts = db_content.sourceName.split("_")
    db_content.sourceName = "_".join([table_name_parts[0],ver, rev, table_name_parts[-1]])
    return db_content

def update_source(db_: Session, source: schemas.SourceEdit, user_id = None):
    '''changes one or more fields of sources, selected via sourceName or table_name'''
    db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source.sourceName).first()
    if source.version or source.versionTag:
        db_content =  update_source_sourcename(db_, source, db_content)

    if source.language:
        language = db_.query(db_models.Language).filter(
            db_models.Language.code == source.language).first()
        if not language:
            raise NotAvailableException(f"Language code, {source.language}, not found in Database")
        db_content.languageId = language.languageId
        source_name_parts = db_content.sourceName.split("_")
        db_content.sourceName = "_".join([source.language]+source_name_parts[1:])
    if source.license:
        license_obj = db_.query(db_models.License).filter(
            db_models.License.code == source.license).first()
        if not license_obj:
            raise NotAvailableException(f"License code, {source.license}, not found in Database")
        db_content.licenseId = license_obj.licenseId
    if source.labels is not None:
        if schemas.SourceLabel.LATEST in source.labels:
            query = db_.query(db_models.Source).join(db_models.Version).filter(
                db_models.Source.version.has(
                    versionAbbreviation = db_content.version.versionAbbreviation),
                db_models.Source.contentId == db_content.contentId,
                db_models.Source.labels.op('&&')(array(schemas.SourceLabel.LATEST.value)),
                db_models.Source.sourceId != db_content.sourceId)
            another_latest = query.all()
            if another_latest:
                raise AlreadyExistsException(
                    f"Another source with latest tag exists: {another_latest[0].sourceName}")
        db_content.labels = source.labels
    if source.year:
        db_content.year = source.year
    if source.metaData:
        db_content.metaData = source.metaData
    if source.active is not None:
        db_content.active = source.active
    db_content.updatedUser = user_id
    # db_.commit()
    # db_.refresh(db_content)
    if not source.sourceName.split("_")[-1] == db_models.ContentTypeName.GITLABREPO.value:
        db_models.dynamicTables[db_content.sourceName] = db_models.dynamicTables[source.sourceName]
    return db_content

def delete_source(db_: Session, delitem: schemas.DeleteIdentity):
    '''delete particular source, selected via source id'''
    db_content = db_.query(db_models.Source).get(delitem.itemId)
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
