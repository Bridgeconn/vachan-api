''' Place to define all Database CRUD operations for table Roles'''
import re
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql import text
import db_models
from custom_exceptions import NotAvailableException
from auth.auth_globals import generate_roles, APPS

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
    if details.permissionName:
        db_content.permissionName = details.permissionName
    if details.permissionDescription:
        db_content.permissionDescription = details.permissionDescription
    db_content.updatedUser = user_id
    return db_content

def create_role(db_: Session, role_details,user_id=None):
    '''Adds a row to roles table'''
    if role_details.roleOfApp.lower() not in [app.lower() for app in APPS]:
        raise NotAvailableException(f"{role_details.roleOfApp} is not registered")
    db_content = db_models.Roles(roleName = role_details.roleName.lower(),
        roleOfApp = role_details.roleOfApp,
        roleDescription = role_details.roleDescription,
        createdUser= user_id,
        updatedUser=user_id,
        active=True)
    db_.add(db_content)
    # db_.commit()
    response = {
        'db_content':db_content,
        'refresh_auth_func':generate_roles
        }
    return response

def get_role(db_: Session,role_name =None,role_of_app =None,role_id=None,**kwargs):
    '''Fetches rows of role, with pagination and various filters'''
    search_word = kwargs.get("search_word",None)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.Roles)
    if role_name:
        query = query.filter(func.lower(db_models.Roles.roleName) == role_name.lower())
    if role_of_app:
        query = query.filter(func.lower(db_models.Roles.roleOfApp) == role_of_app.lower())
    if search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text("to_tsvector('simple', role_description || ' ' )"+\
            " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))
    if role_id is not None:
        query = query.filter(db_models.Roles.roleId == role_id)
    return query.offset(skip).limit(limit).all()

def update_role(db_: Session, role_details, user_id=None):
    '''update rows to roles table'''
    db_content = db_.query(db_models.Roles).get(role_details.roleId)
    if role_details.roleName:
        db_content.roleName = role_details.roleName
    if role_details.roleOfApp:
        db_content.roleOfApp = role_details.roleOfApp
    if role_details.roleDescription:
        db_content.roleDescription = role_details.roleDescription
    db_content.updatedUser = user_id
    # db_.commit()
    response = {
        'db_content':db_content,
        'refresh_auth_func':generate_roles
        }
    return response
