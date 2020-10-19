from sqlalchemy.orm import Session

from . import db_models, schemas

def get_content_types_all(db: Session):
	return db.query(db_models.ContentType)

def get_content_types(db: Session, content_type: str):
	return db.query(db_models.ContentType).filter(db_models.ContentType.content_type == content_type)

def create_content_type(db: Session, content: schemas.ContentType):
    db_content = db_models.ContentType(content_type = content.contentType)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content