from sqlalchemy.orm import Session

import db_models, schemas

def get_content_types(db: Session, contentType: str =None, skip: int = 0, limit: int = 100):
	return db.query(db_models.ContentType).filter(db_models.ContentType.contentType.like('%{}%'.\
		format(contentType))).offset(skip).limit(limit).all()

def get_content_type(db: Session, contentType: str):
	return db.query(db_models.ContentType).filter(db_models.ContentType.contentType == contentType).first()

def create_content_type(db: Session, content: schemas.ContentType):
    db_content = db_models.ContentType(contentType = content.contentType)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content