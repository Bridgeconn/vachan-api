from sqlalchemy.orm import Session
from sqlalchemy import func
import db_models
from custom_exceptions import NotAvailableException
from auth.auth_globals import generate_roles, APPS

def create_role(db_: Session, role_details, user_id=None):
    '''Adds a row to roles table'''
    if role_details.roleOfApp.lower() not in [app.lower() for app in APPS]:
        raise NotAvailableException(f"{role_details.roleOfApp} is not registered")

    db_content = db_models.Roles(roleName = role_details.roleName.lower(),
        roleOfApp = role_details.roleOfApp,
        roleDescription = role_details.roleDescription,
        createdUser= user_id,
        updatedUser=user_id,active=True)
    db_.add(db_content)
    # db_.commit()
    # db_.refresh(db_content)
    generate_roles()
    return db_content

def get_role(db_: Session, role_name = None, role_of_app = None, role_description=None,
    role_id = None, **kwargs):
    '''Fetches rows of role, with pagination and various filters'''
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.Roles)
    if role_name:
        query = query.filter(func.lower(db_models.Roles.roleName) == role_name.lower())
    if role_of_app:
        query = query.filter(func.lower(db_models.Roles.roleOfApp) == role_of_app.lower())
    if role_description:
        query = query.filter(func.lower(db_models.Roles.roleDescription) == role_name.lower())
    if role_id is not None:
        query = query.filter(db_models.Roles.roleId == role_id)
    return query.offset(skip).limit(limit).all()
