''' Place to define all Database CRUD operations'''
import json
import sqlalchemy
from sqlalchemy.orm import Session, Load, noload, load_only, defer, joinedload

import db_models
import schemas
from database import engine
from custom_exceptions import NotAvailableException, TypeException
from logger import log
import pdb; 

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
        versionName = version.versionName.strip(),
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
        db_content.versionName = version.versionName
    if version.revision:
        db_content.revision = version.revision
    if version.metaData:
        db_content.metaData = version.metaData
    db_.commit()
    db_.refresh(db_content)
    return db_content

def get_sources(db_: Session, #pylint: disable=too-many-arguments, disable-msg=too-many-locals, disable=too-many-branches
    content_type=None, version_abbreviation=None, revision=None,
    language_code=None, metadata=None, active=True, latest_revision = True, table_name=None,
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

    db_content = db_models.Source(
        year = source.year,
        sourceName = table_name,
        contentId = content_type.contentId,
        versionId = version.versionId,
        languageId = language.languageId,
        metaData = source.metaData,
        active = True)
    if source.license is not None:
        db_content.license = source.license
    if user_id:
        db_content.created_user = user_id
    db_.add(db_content)
    db_models.create_dynamic_table(table_name, content_type.contentType)
    db_models.dynamicTables[db_content.sourceName].__table__.create(bind=engine, checkfirst=True)
    if content_type.contentType == 'bible':
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
    if source.year:
        db_content.year = source.year
    if source.license:
        db_content.license = source.license
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
        if db_content.contentType.contentType == 'bible':
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

def get_commentaries(db_:Session, source_name, book_code=None, chapter=None, #pylint: disable=too-many-arguments
    verse=None, last_verse=None, active=True, skip=0, limit=100):
    '''Fetches rows of commentries from the table specified by source_name'''
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('commentary'):
        raise TypeException('The operation is supported only on commentaries')
    model_cls = db_models.dynamicTables[source_name]
    query = db_.query(model_cls)
    if book_code:
        query = query.filter(model_cls.book.has(bookCode=book_code.lower()))
    if chapter is not None:
        query = query.filter(model_cls.chapter == chapter)
    if verse is not None:
        if last_verse is None:
            last_verse = verse
        query = query.filter(model_cls.verseStart <= verse, model_cls.verseEnd >= last_verse)
    query = query.filter(model_cls.active == active)
    return query.offset(skip).limit(limit).all()

def upload_commentaries(db_: Session, source_name, commentaries, user_id=None):
    '''Adds rows to the commentary table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'commentary':
        raise TypeException('The operation is supported only on commentaries')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    prev_book_code = None
    for item in commentaries:
        if item.bookCode != prev_book_code:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
            prev_book_code = item.bookCode
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database')
        if item.verseStart is not None and item.verseEnd is None:
            item.verseEnd = item.verseStart
        row = model_cls(
            book_id = book.bookId,
            chapter = item.chapter,
            verseStart = item.verseStart,
            verseEnd = item.verseEnd,
            commentary = item.commentary,
            active=item.active)
        db_content.append(row)
    db_.add_all(db_content)
    db_.commit()
    db_.expire_all()
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content

def update_commentaries(db_: Session, source_name, commentaries, user_id=None):
    '''Update rows, that matches book, chapter and verse range fields in the commentary table
    specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'commentary':
        raise TypeException('The operation is supported only on commentaries')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    prev_book_code = None
    for item in commentaries:
        if item.bookCode != prev_book_code:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
            prev_book_code = item.bookCode
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database')
        row = db_.query(model_cls).filter(
            model_cls.book_id == book.bookId,
            model_cls.chapter == item.chapter,
            model_cls.verseStart == item.verseStart,
            model_cls.verseEnd == item.verseEnd).first()
        if not row:
            raise NotAvailableException("Commentary row with bookCode:%s, chapter:%s, \
                verseStart:%s, verseEnd:%s, not found for %s"%(
                    item.bookCode, item.chapter, item.verseStart, item.verseEnd, source_name))
        if item.commentary:
            row.commentary = item.commentary
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    db_.commit()
    source_db_content.updatedUser = user_id
    db_.commit()
    db_.refresh(source_db_content)
    return db_content

def get_dictionary_words(db_:Session, source_name, search_word = None, details = None,  #pylint: disable=too-many-arguments
    exact_match=False, word_list_only=False, active=True, skip=0, limit=100):
    '''Fetches rows of dictionary from the table specified by source_name'''
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('dictionary'):
        raise TypeException('The operation is supported only on dictionaries')
    model_cls = db_models.dynamicTables[source_name]
    if word_list_only:
        query = db_.query(model_cls.word)
    else:
        query = db_.query(model_cls)
    if search_word and exact_match:
        query = query.filter(model_cls.word == search_word)
    elif search_word:
        query = query.filter(model_cls.word.like(search_word+"%"))
    if details:
        det = json.loads(details)
        for key in det:
            query = query.filter(model_cls.details.op('->>')(key) == det[key])
    query = query.filter(model_cls.active == active)
    res = query.offset(skip).limit(limit).all()
    return res

def upload_dictionary_words(db_: Session, source_name, dictionary_words, user_id=None):
    '''Adds rows to the dictionary table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'dictionary':
        raise TypeException('The operation is supported only on dictionaries')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in dictionary_words:
        row = model_cls(
            word = item.word,
            details = item.details,
            active = item.active)
        db_content.append(row)
    db_.add_all(db_content)
    db_.commit()
    db_.expire_all()
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content

def update_dictionary_words(db_: Session, source_name, dictionary_words, user_id=None):
    '''Update rows, that matches the word field in the dictionary table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'dictionary':
        raise TypeException('The operation is supported only on dictionaries')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in dictionary_words:
        row = db_.query(model_cls).filter(model_cls.word == item.word).first()
        if not row:
            raise NotAvailableException("Dictionary row with word:%s, not found for %s"%(
                    item.word, source_name))
        if item.details:
            row.details = item.details
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    db_.commit()
    source_db_content.updatedUser = user_id
    db_.commit()
    db_.refresh(source_db_content)
    return db_content

def get_infographics(db_:Session, source_name, book_code=None, title=None, #pylint: disable=too-many-arguments
    active=True, skip=0, limit=100):
    '''Fetches rows of infographics from the table specified by source_name'''
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('infographics'):
        raise TypeException('The operation is supported only on infographics')
    model_cls = db_models.dynamicTables[source_name]
    query = db_.query(model_cls)
    if book_code:
        query = query.filter(model_cls.book.has(bookCode=book_code.lower()))
    if title:
        query = query.filter(model_cls.title == title.strip())
    query = query.filter(model_cls.active == active)
    return query.offset(skip).limit(limit).all()

def upload_infographics(db_: Session, source_name, infographics, user_id=None):
    '''Adds rows to the infographics table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'infographics':
        raise TypeException('The operation is supported only on infographics')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    prev_book_code = None
    for item in infographics:
        if item.bookCode != prev_book_code:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
            prev_book_code = item.bookCode
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database'
                    %item.bookCode)
        row = model_cls(
            book_id = book.bookId,
            title = item.title.strip(),
            infographicLink = item.infographicLink,
            active=item.active)
        db_content.append(row)
    db_.add_all(db_content)
    db_.commit()
    db_.expire_all()
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content

def update_infographics(db_: Session, source_name, infographics, user_id=None):
    '''Update rows, that matches book, and title in the infographic table
    specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'infographics':
        raise TypeException('The operation is supported only on infographics')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    prev_book_code = None
    for item in infographics:
        if item.bookCode != prev_book_code:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
            prev_book_code = item.bookCode
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database'
                    %item.bookCode)
        row = db_.query(model_cls).filter(
            model_cls.book_id == book.bookId,
            model_cls.title == item.title.strip()).first()
        if not row:
            raise NotAvailableException("Infographics row with bookCode:%s, title:%s, \
                not found for %s"%(
                    item.bookCode, item.title, source_name))
        if item.infographicLink:
            row.infographicLink = item.infographicLink
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    db_.commit()
    source_db_content.updatedUser = user_id
    db_.commit()
    db_.refresh(source_db_content)
    return db_content

def get_bible_videos(db_:Session, source_name, book_code=None, title=None, theme=None, active=True, #pylint: disable=too-many-arguments
    skip=0, limit=100):
    '''fetches rows of bible videos as per provided source_name and filters'''
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('bible_video'):
        raise TypeException('The operation is supported only on bible_video')
    model_cls = db_models.dynamicTables[source_name]
    query = db_.query(model_cls)
    if book_code:
        query = query.filter(model_cls.books.any(book_code.lower()))
    if title:
        query = query.filter(model_cls.title == title.strip())
    if theme:
        query = query.filter(model_cls.theme == theme.strip())
    query = query.filter(model_cls.active == active)
    return query.offset(skip).limit(limit).all()



def upload_bible_videos(db_: Session, source_name, videos, user_id=None):
    '''Adds rows to the bible videos table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'bible_video':
        raise TypeException('The operation is supported only on bible_video')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in videos:
        for book_code in item.books:
            # verifying if the book codes are valid as we dont use FK for this field
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == book_code.lower() ).first()
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database'%book_code)
        row = model_cls(
            title = item.title.strip(),
            theme = item.theme.strip(),
            description = item.description.strip(),
            active = item.active,
            books = item.books,
            videoLink = item.videoLink)
        db_content.append(row)
    db_.add_all(db_content)
    db_.commit()
    db_.expire_all()
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content


def update_bible_videos(db_: Session, source_name, videos, user_id=None):
    '''Update rows, that matches title in the bible videos table
    specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'bible_video':
        raise TypeException('The operation is supported only on bible_video')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in videos:
        row = db_.query(model_cls).filter(model_cls.title == item.title.strip()).first()
        if not row:
            raise NotAvailableException("Bible Video row with title:%s, \
                not found for %s"%(
                    item.title, source_name))
        if item.books:
            for book_code in item.books:
                # verifying if the book codes are valid as we dont use FK for this field
                book = db_.query(db_models.BibleBook).filter(
                    db_models.BibleBook.bookCode == book_code.lower() ).first()
                if not book:
                    raise NotAvailableException('Bible Book code, %s, not found in database'
                        %book_code )
            row.books = item.books
        if item.theme:
            row.theme = item.theme.strip()
        if item.description:
            row.description = item.description.strip()
        if item.active is not None:
            row.active = item.active
        if item.videoLink:
            row.videoLink = item.videoLink
        db_.flush()
        db_content.append(row)
    db_.commit()
    source_db_content.updatedUser = user_id
    db_.commit()
    db_.refresh(source_db_content)
    return db_content

def upload_bible_books(db_: Session, source_name, books, user_id=None):
    '''Adds rows to the bible table and corresponding bible_cleaned specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'bible':
        raise TypeException('The operation is supported only on bible')
    model_cls = db_models.dynamicTables[source_name]
    model_cls_2 = db_models.dynamicTables[source_name+'_cleaned']
    db_content = []
    db_content2 = []
    for item in books:
        book_code = item.JSON['book']['bookCode']
        book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == book_code.lower() ).first()
        if not book:
            raise NotAvailableException('Bible Book code, %s, not found in database'
                %book_code)
        row = model_cls(
            book_id=book.bookId,
            USFM=item.USFM,
            JSON=item.JSON,
            active=True)
        db_.flush()
        db_content.append(row)
        for chapter in item.JSON["chapters"]:
            chapter_number = int(chapter['chapterNumber'])
            for content in chapter['contents']:
                if 'verseNumber' in content:
                    row_other = model_cls_2(
                        book_id = book.bookId,
                        chapter = chapter_number,
                        verseNumber = content['verseNumber'],
                        verseText = content['verseText'].strip())
                    db_content2.append(row_other)
    db_.add_all(db_content)
    db_.add_all(db_content2)
    source_db_content.updatedUser = user_id
    db_.commit()
    for item in db_content:
        print(item.__dict__)
    return db_content

def update_bible_books(db_: Session, source_name, books, user_id=None):
    '''change values of bible books already uploaded'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'bible':
        raise TypeException('The operation is supported only on bible')
    # update the bible table
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in books:
        book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
        row = db_.query(model_cls).filter(model_cls.book_id == book.bookId).first()
        if not row:
            raise NotAvailableException("Bible book, %s, not found in Database"%item.bookCode)
        if item.USFM:
            row.USFM = item.USFM
            row.JSON = item.JSON
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    # update bible cleaned table
    db_content2 = []
    model_cls_2 = db_models.dynamicTables[source_name+'_cleaned']
    for item in books:
        book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
        if item.USFM: # delete all verses and add them again
            db_.query(model_cls_2).filter(
                model_cls_2.book_id == book.bookId).delete()
            for chapter in item.JSON["chapters"]:
                chapter_number = int(chapter['chapterNumber'])
                for content in chapter['contents']:
                    if 'verseNumber' in content:
                        row_other = model_cls_2(
                            book_id = book.bookId,
                            chapter = chapter_number,
                            verseNumber = content['verseNumber'],
                            verseText = content['verseText'].strip())
                        db_content2.append(row_other)
            db_.add_all(db_content2)
        if item.active is not None: # set all the verse rows' active flag accordingly
            rows = db_.query(model_cls_2).filter(
                model_cls_2.book_id == book.bookId).all()
            for row in rows:
                row.active = item.active
    db_.commit()
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content


def upload_bible_audios(db_:Session, source_name, audios, user_id=None):
    '''Add audio bible related contents to _bible_audio table'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'bible':
        raise TypeException('The operation is supported only on bible')
    model_cls_audio = db_models.dynamicTables[source_name+'_audio']
    model_cls_bible = db_models.dynamicTables[source_name]
    db_content = []
    db_content2 = []
    for item in audios:
        for buk in item.books:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == buk.strip().lower()).first()
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database')
            bible_table_row = db_.query(model_cls_bible).filter(
                model_cls_bible.book_id == book.bookId).first()
            if not bible_table_row:
                bible_table_row = model_cls_bible(
                    book_id=book.bookId
                    )
                db_content2.append(bible_table_row)
            row = model_cls_audio(
                name=item.name.strip(),
                url=item.url.strip(),
                book_id=book.bookId,
                format=item.format.strip(),
                active=item.active)
            db_content.append(row)
    db_.add_all(db_content)
    db_.add_all(db_content2)
    db_.commit()
    for item in db_content:
        print(item.__dict__)
    return db_content

def update_bible_audios(db_: Session, source_name, audios, user_id=None):
    '''Update any details of a bible Auido row. 
    Use name as row-identifier, which cannot be changed'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'bible':
        raise TypeException('The operation is supported only on bible')
    model_cls = db_models.dynamicTables[source_name+'_audio']
    db_content = []
    for item in audios:
        for buk in item.books:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == buk.strip().lower()).first()
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database')
            row = db_.query(model_cls).filter(model_cls.book_id == book.bookId).first()
            if not row:
                raise NotAvailableException("Bible audio for, %s, not found in database"%item.name)
            if item.name:
                row.name = item.name.strip()
            if item.url:
                row.url = item.url.strip()
            if item.format:
                row.format = item.format.strip()
            if item.active is not None:
                row.active = item.active
            db_content.append(row)
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content

    
    
def get_bible_versification(db_, source_name, book_code, active=True):
    '''select the reference list from bible_cleaned table'''
    model_cls = db_models.dynamicTables[source_name+"_cleaned"]
    query = db_.query(model_cls).prefix_with(
        "'"+source_name+"' as bible, ")
    query = query.options(defer(model_cls.verseText))
    query = query.filter(model_cls.book.has(bookCode = book_code.lower()),
        model_cls.active == active )
    return query.all()


def get_available_bible_books(db_, source_name, book_code=None, content_type=None, #pylint: disable=too-many-arguments
    versification=False, active=True, skip=0, limit=100):
    '''fetches the contents of .._bible table based of provided source_name and other options'''
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('_bible'):
        raise TypeException('The operation is supported only on bible')
    model_cls = db_models.dynamicTables[source_name]
    # model_cls_audio = db_models.dynamicTables[source_name+"_audio"]
    query = db_.query(model_cls).options(joinedload(model_cls.book))
    if content_type == "usfm":
        query = query.options(defer(model_cls.JSON))
    elif content_type == "json":
        query = query.options(defer(model_cls.USFM))
    elif content_type == "all":
        query = query.join(model_cls.audio).filter(
            model_cls.audio.has(active=active))
    elif content_type == "audio":
        query = query.options(joinedload(model_cls.audio),
            defer(model_cls.JSON), defer(model_cls.USFM)).filter(
            model_cls.audio.has(active=active))
    elif content_type is None:
        print("comes in None to exclude USFM and JSON")
        query = query.options(defer(model_cls.JSON), defer(model_cls.USFM))
    if book_code:
        query = query.filter(model_cls.book.has(bookCode=book_code.lower()))
    fetched = query.filter(model_cls.active == active).offset(skip).limit(limit).all()
    results = [res.__dict__ for res in fetched]
    for res in results:
        print(res)
    if versification:
        added_results = []
        for res in results:
            ref_list = get_bible_versification(db_, source_name, res.book.bookCode, active)
            added_res = res
            added_res['versification'] = ref_list
            added_results.append(added_res)
        return added_results
    return results


def get_bible_verses(db_, source_name, book_code, chapter, verse, lastVerse,
            searchPhrase, active=True, skip=0, limit=100):
    return []