''' Place to define all Database CRUD operations for table Roles'''
from sqlalchemy.orm import Session
import db_models
from sqlalchemy import func
from custom_exceptions import AlreadyExistsException,NotAvailableException
from sqlalchemy.orm.attributes import flag_modified
from schema import schema_auth

def update_role(db_: Session, role: schema_auth.RoleEdit, user_id=None):
    '''update rows to roles table'''
    # print(role,user_id)
    db_content = db_.query(db_models.Roles).get(role.roleId)
    # print(db_content, "print the db_content")
    if role.roleName:
        db_content.roleName = role.roleName
    if role.roleOfApp:
        db_content.roleOfApp = role.roleOfApp
    if role.roleDescription:
        db_content.roleDescription = role.roleDescription   
    db_content.updatedUser = user_id
    # db_.commit()
    # db_.refresh(db_content)
    return db_content

# def update_auth_permission(db_: Session, details, user_id= None):
#     '''update a row to auth permission table'''
#     db_content = db_.query(db_models.Permissions).get(details.permissionId)
#     if details.permissionDescription:
#               db_content.permissionDescription = details.permissionDescription
#     db_content.updatedUser = user_id
#     return db_content


# def update_license(db_: Session, license_obj: schemas.LicenseEdit, user_id=None):
#     '''changes one or more fields of license, selected via license code'''
#     db_content = db_.query(db_models.License).filter(
#         db_models.License.code == license_obj.code.strip().upper()).first()
#     if not db_content:
#         raise NotAvailableException(f"License with code, {license_obj.code}, "+\
#             "not found in database")
#     if license_obj.name:
#         db_content.name = license_obj.name
#     if license_obj.license:
#         db_content.license = utils.normalize_unicode(license_obj.license)
#     if license_obj.permissions:
#         db_content.permissions = license_obj.permissions
#     if license_obj.active is not None:
#         db_content.active = license_obj.active
#     db_content.updatedUser = user_id
#     # db_.commit()
#     # db_.refresh(db_content)
#     return db_content


# def update_license(db_: Session, license_obj: schemas.LicenseEdit, user_id=None):
#     '''changes one or more fields of license, selected via license code'''
#     db_content = db_.query(db_models.License).filter(
#         db_models.License.code == license_obj.code.strip().upper()).first()
#     if not db_content:
#         raise NotAvailableException(f"License with code, {license_obj.code}, "+\
#             "not found in database")
#     if license_obj.name:
#         db_content.name = license_obj.name
#     if license_obj.license:
#         db_content.license = utils.normalize_unicode(license_obj.license)
#     if license_obj.permissions:
#         db_content.permissions = license_obj.permissions
#     if license_obj.active is not None:
#         db_content.active = license_obj.active
#     db_content.updatedUser = user_id
#     # db_.commit()
#     # db_.refresh(db_content)
#     return db_content
# def delete_license(db_: Session, content: schemas.DeleteIdentity):
#     '''delete particular license, selected via license id'''
#     db_content = db_.query(db_models.License).get(content.itemId)
#     db_.delete(db_content)
#     #db_.commit()
#     return db_content