''' Place to define all Database CRUD operations for Auth Tables'''
import re
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql import text
import db_models

def get_auth_permission(db_: Session, permission_name=None, permission_id=None, **kwargs):
    '''get rows from auth permission table'''
    search_word = kwargs.get("search_word",None)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.Permissions)
    if permission_name:
        query = query.filter(func.lower(db_models.Permissions.permissionName) ==\
            permission_name.lower())
    if search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text("to_tsvector('simple', permission_name || ' ' ||"+\
            " permission_description || ' ' ) "+\
            " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))
    if permission_id is not None:
        query = query.filter(db_models.Permissions.permissionId == permission_id)
    return query.offset(skip).limit(limit).all()


def create_auth_permission(db_: Session, details, user_id= None):
    '''Add a row to auth permission table'''
    db_content = db_models.Permissions(permissionName = details.permissionName.lower(),
        permissionDescription = details.permissionDescription,
        createdUser= user_id,
        updatedUser=user_id,
        active=True)
    db_.add(db_content)
    return db_content

def update_auth_permission(db_: Session, details, user_id= None):
    '''update a row to auth permission table'''
    db_content = db_.query(db_models.Permissions).get(details.permissionId)
    if details.permissionDescription:
        db_content.permissionDescription = details.permissionDescription
    db_content.updatedUser = user_id
    return db_content
