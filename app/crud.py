''' Place to define all Database CRUD operations'''

from sqlalchemy.orm import Session
import db_models
import schemas

def get_content_types_all(db_: Session):
    '''GET without any filter'''
    return db_.query(db_models.ContentType)

def get_content_types(db_: Session, content_type: str):
    '''GET one specific contentType'''
    res = db_.query(db_models.ContentType).filter(
        db_models.ContentType.content_type == content_type)
    return res

def create_content_type(db_: Session, content: schemas.ContentType):
    '''Add new content type to DB'''
    db_content = db_models.ContentType(content_type = content.contentType)
    db_.add(db_content)
    db_.commit()
    db_.refresh(db_content)
    return db_content
