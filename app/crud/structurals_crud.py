''' Place to define all Database CRUD operations for tables
Content_types, Languages, Licenses, versions, sources and bible_book_loopup'''

import json
import sqlalchemy
from sqlalchemy.orm import Session

#pylint: disable=E0401
#pylint gives import error if not relative import is used. But app(uvicorn) doesn't accept it

import db_models
import schemas
from crud import normalize_unicode
from custom_exceptions import NotAvailableException
from database import engine
from logger import log

def get_content_types(db_: Session, content_type: str =None, skip: int = 0, limit: int = 100):
    '''Fetches all content types, with pagination'''
    if content_type:
        return db_.query(db_models.ContentType).filter(
            db_models.ContentType.contentType == content_type).offset(skip).limit(limit).all()
    return db_.query(db_models.ContentType).offset(skip).limit(limit).all()

def create_content_type(db_: Session, content: schemas.ContentTypeCreate):
    '''Adds a row to content_types table'''
    db_content = db_models.ContentType(contentType = content.contentType)
    db_.add(db_content)
    db_.commit()
    db_.refresh(db_content)
    return db_content

def get_languages(db_: Session, language_code = None, language_name = None, #pylint: disable=too-many-arguments
    language_id = None, skip: int = 0, limit: int = 100):
    '''Fetches rows of language, with pagination and various filters'''
    query = db_.query(db_models.Language)
    if language_code:
        query = query.filter(db_models.Language.code == language_code.lower())
    if language_name:
        query = query.filter(db_models.Language.language == language_name.lower())
    if language_id is not None:
        query = query.filter(db_models.Language.languageId == language_id)
    return query.offset(skip).limit(limit).all()

def create_language(db_: Session, lang: schemas.LanguageCreate):
    '''Adds a row to languages table'''
    db_content = db_models.Language(code = lang.code.lower(),
        language = lang.language.lower(),
        scriptDirection = lang.scriptDirection)
    db_.add(db_content)
    db_.commit()
    db_.refresh(db_content)
    return db_content

def update_language(db_: Session, lang: schemas.LanguageEdit):
    '''changes one or more fields of language, selected via language id'''
    db_content = db_.query(db_models.Language).get(lang.languageId)
    if lang.code:
        db_content.code = lang.code
    if lang.language:
        db_content.language = lang.language
    if lang.scriptDirection:
        db_content.scriptDirection = lang.scriptDirection
    db_.commit()
    db_.refresh(db_content)
    return db_content

def get_licenses(db_: Session, license_code = None, license_name = None, #pylint: disable=too-many-arguments
    permission = None, active=True, skip: int = 0, limit: int = 100):
    '''Fetches rows of licenses, with pagination and various filters'''
    query = db_.query(db_models.License)
    if license_code:
        query = query.filter(db_models.License.code == license_code.upper())
    if license_name:
        query = query.filter(db_models.License.name == license_name.strip())
    if permission is not None:
        query = query.filter(db_models.License.permissions.any(permission))
    return query.filter(db_models.License.active == active).offset(skip).limit(limit).all()

def create_license(db_: Session, license_obj: schemas.LicenseCreate, user_id=None):
    '''Adds a new license to Database'''
    db_content = db_models.License(code = license_obj.code.upper(),
        name = license_obj.name.strip(),
        license = normalize_unicode(license_obj.license),
        permissions = license_obj.permissions,
        active=True,
        createdUser=user_id)
    db_.add(db_content)
    db_.commit()
    db_.refresh(db_content)
    return db_content

def update_license(db_: Session, license_obj: schemas.LicenseEdit, user_id=None):
    '''changes one or more fields of license, selected via license code'''
    db_content = db_.query(db_models.License).filter(
        db_models.License.code == license_obj.code.strip().upper()).first()
    if not db_content:
        raise NotAvailableException("License with code, %s, not found in database"%license_obj.code)
    if license_obj.name:
        db_content.name = license_obj.name
    if license_obj.license:
        db_content.license = normalize_unicode(license_obj.license)
    if license_obj.permissions:
        db_content.permissions = license_obj.permissions
    if license_obj.active is not None:
        db_content.active = license_obj.active
    db_content.updatedUser = user_id
    db_.commit()
    db_.refresh(db_content)
    return db_content

def get_versions(db_: Session, version_abbr = None, version_name = None, revision = None, #pylint: disable=too-many-arguments
    metadata = None, version_id = None, skip: int = 0, limit: int = 100):
    '''Fetches rows of versions table, with various filters and pagination'''
    query = db_.query(db_models.Version)
    if version_abbr:
        query = query.filter(db_models.Version.versionAbbreviation == version_abbr.upper().strip())
    if version_name:
        query = query.filter(db_models.Version.versionName == version_name.strip())
    if revision:
        query = query.filter(db_models.Version.revision == revision)
    if metadata:
        meta = json.loads(metadata)
        for key in meta:
            query = query.filter(db_models.Version.metaData.op('->>')(key) == meta[key])
    if version_id:
        query = query.filter(db_models.Version.versionId == version_id)
    return query.offset(skip).limit(limit).all()

def create_version(db_: Session, version: schemas.VersionCreate):
    '''Adds a row to versions table'''
    db_content = db_models.Version(
        versionAbbreviation = version.versionAbbreviation.upper().strip(),
        versionName = normalize_unicode(version.versionName.strip()),
        revision = version.revision,
        metaData = version.metaData)
    db_.add(db_content)
    db_.commit()
    db_.refresh(db_content)
    return db_content

def update_version(db_: Session, version: schemas.VersionEdit):
    '''changes one or more fields of versions, selected via version id'''
    db_content = db_.query(db_models.Version).get(version.versionId)
    if version.versionAbbreviation:
        db_content.versionAbbreviation = version.versionAbbreviation
    if version.versionName:
        db_content.versionName = normalize_unicode(version.versionName)
    if version.revision:
        db_content.revision = version.revision
    if version.metaData:
        db_content.metaData = version.metaData
    db_.commit()
    db_.refresh(db_content)
    return db_content

def get_sources(db_: Session, #pylint: disable=too-many-arguments, disable-msg=too-many-locals, disable=too-many-branches
    content_type=None, version_abbreviation=None, revision=None, language_code=None,
    license_abbreviation=None, metadata=None, latest_revision=True, active=True, table_name=None,
    skip: int = 0, limit: int = 100):
    '''Fetches the rows of sources table'''
    query = db_.query(db_models.Source)
    if content_type:
        query = query.filter(db_models.Source.contentType.has(contentType = content_type.strip()))
    if version_abbreviation:
        query = query.filter(
            db_models.Source.version.has(versionAbbreviation = version_abbreviation.strip()))
    if revision:
        query = query.filter(
            db_models.Source.version.has(revision = revision))
    if license_abbreviation:
        query = query.filter(db_models.Source.license.has(code = license_abbreviation.strip()))
    if language_code:
        query = query.filter(db_models.Source.language.has(code = language_code.strip()))
    if metadata:
        meta = json.loads(metadata)
        for key in meta:
            query = query.filter(db_models.Source.metaData.op('->>')(key) == meta[key])
    if active:
        query = query.filter(db_models.Source.active)
    else:
        query = query.filter(db_models.Source.active == False) #pylint: disable=singleton-comparison
    if table_name:
        query = query.filter(db_models.Source.sourceName == table_name)

    res = query.join(db_models.Version).order_by(db_models.Version.revision.desc()
        ).offset(skip).limit(limit).all()
    if not latest_revision or revision:
        return res

    # sub_qry = query.join(db_models.Version, func.max(db_models.Version.revision).label(
    #     "latest_rev")).group_by(
    #     db_models.Source.contentId, db_models.Source.languageId,
    #     db_models.Version.versionAbbreviation
    #     ).subquery('sub_qry')
    # latest_res = query.filter(db_models.Source.contentId == sub_qry.c.contentType.contentId,
    #     db_models.Source.languageId == sub_qry.c.language.languageId,
    #     db_models.Source.version.has(versionAbbreviation = sub_qry.c.version.versionAbbreviation),
    #     db_models.Source.version.has(revision = sub_qry.c.latest_rev)
    #     ).offset(skip).limit(limit).all()

    # Filtering out the latest versions here from the query result.
    # Had tried to include that into the query, but it seemed very difficult.
    latest_res = []
    for res_item in res:
        exculde = False
        x_parts = res_item.sourceName.split('_')
        for latest_item in latest_res:
            y_parts = latest_item.sourceName.split('_')
            if x_parts[:1]+x_parts[-1:] == y_parts[:1]+y_parts[-1:]:
                if x_parts[2] < y_parts[3]:
                    exculde = True
                    break
        if not exculde:
            latest_res.append(res_item)
    return latest_res

def create_source(db_: Session, source: schemas.SourceCreate, table_name, user_id = None):
    '''Adds a row to sources table'''
    content_type = db_.query(db_models.ContentType).filter(
        db_models.ContentType.contentType == source.contentType.strip()).first()
    if not content_type:
        raise NotAvailableException("ContentType, %s, not found in Database"
            %source.contentType.strip())
    version = db_.query(db_models.Version).filter(
        db_models.Version.versionAbbreviation == source.version,
        db_models.Version.revision == source.revision).first()
    if not version:
        raise NotAvailableException("Version, %s %s, not found in Database"%(source.version,
            source.revision))
    language = db_.query(db_models.Language).filter(
        db_models.Language.code == source.language).first()
    if not language:
        raise NotAvailableException("Language code, %s, not found in Database"%source.language)
    license_obj = db_.query(db_models.License).filter(
        db_models.License.code == source.license).first()
    if not license_obj:
        raise NotAvailableException("License code, %s, not found in Database"%source.license)

    db_content = db_models.Source(
        year = source.year,
        sourceName = table_name,
        contentId = content_type.contentId,
        versionId = version.versionId,
        languageId = language.languageId,
        licenseId = license_obj.licenseId,
        metaData = source.metaData,
        active = True)
    if user_id:
        db_content.created_user = user_id
    db_.add(db_content)
    db_models.create_dynamic_table(table_name, content_type.contentType)
    db_models.dynamicTables[db_content.sourceName].__table__.create(bind=engine, checkfirst=True)
    if content_type.contentType == db_models.ContentTypeName.bible.value:
        db_models.dynamicTables[db_content.sourceName+'_cleaned'].__table__.create(
            bind=engine, checkfirst=True)
        log.warning("User %s, creates a new table %s", user_id, db_content.sourceName+'_cleaned')
        db_models.dynamicTables[db_content.sourceName+'_audio'].__table__.create(
            bind=engine, checkfirst=True)
        log.warning("User %s, creates a new table %s", user_id, db_content.sourceName+'_audio')
    log.warning("User %s, creates a new table %s", user_id, db_content.sourceName)
    db_.commit()
    db_.refresh(db_content)
    return db_content

def update_source(db_: Session, source: schemas.SourceEdit, user_id = None): #pylint: disable=too-many-branches
    '''changes one or more fields of sources, selected via sourceName or table_name'''
    db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source.sourceName).first()
    if source.version or source.revision:
        if source.version:
            ver = source.version
        else:
            ver = db_content.version.versionAbbreviation
        if source.revision:
            rev = source.revision
        else:
            rev = db_content.version.revision
        version = db_.query(db_models.Version).filter(
            db_models.Version.versionAbbreviation == ver,
            db_models.Version.revision == rev).first()
        if not version:
            raise NotAvailableException("Version, %s %s, not found in Database"%(ver,
                rev))
        db_content.versionId = version.versionId
        table_name_parts = db_content.sourceName.split("_")
        db_content.sourceName = "_".join([table_name_parts[0],ver, rev, table_name_parts[-1]])

    if source.language:
        language = db_.query(db_models.Language).filter(
            db_models.Language.code == source.language).first()
        if not language:
            raise NotAvailableException("Language code, %s, not found in Database"%source.language)
        db_content.languageId = language.languageId
        table_name_parts = db_content.sourceName.split("_")
        db_content.sourceName = "_".join([source.language]+table_name_parts[1:])
    if source.license:
        license_obj = db_.query(db_models.License).filter(
            db_models.License.code == source.license).first()
        if not license_obj:
            raise NotAvailableException("License code, %s, not found in Database"%source.license)
        db_content.licenseId = license_obj.licenseId
    if source.year:
        db_content.year = source.year
    if source.metaData:
        db_content.metaData = source.metaData
    if source.active is not None:
        db_content.active = source.active
    if user_id:
        db_content.updatedUser = user_id
    db_.commit()
    db_.refresh(db_content)
    if source.sourceName != db_content.sourceName:
        sql_statement = sqlalchemy.text("ALTER TABLE IF EXISTS %s RENAME TO %s"%(
            source.sourceName, db_content.sourceName))
        db_.execute(sql_statement)
        log.warning("User %s, renames table %s to %s", user_id, db_content.sourceName,
            db_content.sourceName)
        if db_content.contentType.contentType == db_models.ContentTypeName.bible.value:
            sql_statement = sqlalchemy.text("ALTER TABLE IF EXISTS %s RENAME TO %s"%(
                source.sourceName+"_cleaned", db_content.sourceName+"_cleaned"))
            db_.execute(sql_statement)
            log.warning("User %s, renames table %s to %s", user_id, source.sourceName+"_cleaned",
                db_content.sourceName+"_cleaned")
    db_models.create_dynamic_table(db_content.sourceName, db_content.contentType.contentType)
    return db_content

def get_bible_books(db_:Session, book_id=None, book_code=None, book_name=None, #pylint: disable=too-many-arguments
    skip=0, limit=100):
    '''Fetches rows of bible_books_lookup, with pagination and various filters'''
    query = db_.query(db_models.BibleBook)
    if book_id:
        query = query.filter(db_models.BibleBook.bookId == book_id)
    if book_code:
        query = query.filter(db_models.BibleBook.bookCode == book_code.lower())
    if book_name is not None:
        query = query.filter(db_models.BibleBook.bookName == book_name.lower())
    return query.offset(skip).limit(limit).all()
