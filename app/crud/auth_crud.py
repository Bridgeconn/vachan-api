''' Place to define all Database CRUD operations for table Roles'''
from sqlalchemy.orm import Session
import db_models

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
    # db_.refresh(db_content)
    return db_content
