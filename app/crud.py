''' Place to define all Database CRUD operations'''

from sqlalchemy.orm import Session
import db_models
import schemas

def get_content_types(db_: Session, content_type: str =None, skip: int = 0, limit: int = 100):
    '''Fetches all content types, with pagination'''
    if content_type:
        return db_.query(db_models.ContentType).filter(
            db_models.ContentType.contentType == content_type).offset(skip).limit(limit).all()
    return db_.query(db_models.ContentType).offset(skip).limit(limit).all()

def create_content_type(db_: Session, content: schemas.ContentTypeCreate):
    '''Adds a row to table'''
    db_content = db_models.ContentType(contentType = content.contentType)
    db_.add(db_content)
    db_.commit()
    db_.refresh(db_content)
    return db_content

def get_languages(db_: Session, language_code = None, language_name = None, #pylint: disable=too-many-arguments
    language_id = None, skip: int = 0, limit: int = 100):
    '''Fetched all rows, with pagination'''
    if language_code and language_name:
        return db_.query(db_models.Language).filter(
            db_models.Language.code == language_code.lower(),
            db_models.Language.language == language_name.lower()).all()
    if language_name:
        return db_.query(db_models.Language).filter(
            db_models.Language.language == language_name.lower()).all()
    if language_code:
        return db_.query(db_models.Language).filter(
            db_models.Language.code == language_code.lower()).all()
    if language_id is not None:
        return db_.query(db_models.Language).filter(
            db_models.Language.languageId == language_id).all()
    return db_.query(db_models.Language).offset(skip).limit(limit).all()

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
