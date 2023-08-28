''' Place to define all Database CRUD operations for table Roles'''
import re
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sqlalchemy.sql import text
import db_models
from custom_exceptions import NotAvailableException
from auth.auth_globals import generate_roles, APPS, generate_access_rules_dict,\
    generate_permission_map_table
from schema import schema_auth
from auth.authentication import get_all_or_one_kratos_users #pylint: disable=ungrouped-imports

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


def create_access_rules(db_: Session, details: schema_auth.AccessRuleCreateInput, user_id= None):
    '''Add a row to access rule table'''
    entitlement = db_.query(db_models.ResourceTypes).filter(
        func.lower(db_models.ResourceTypes.resourceTypeName) ==\
            func.lower(details.entitlement.strip())).first()
    if not entitlement:
        raise NotAvailableException(f"Entitlement, {details.entitlement.strip()},"+\
            " not found in Database")
    tag = db_.query(db_models.Permissions).filter(
        func.lower(db_models.Permissions.permissionName) == \
            func.lower(details.tag.strip())).first()
    if not tag:
        raise NotAvailableException(f"Tag, {details.tag.strip()},"+\
            " not found in Database")
    db_rules_list = []
    for role in details.roles:
        db_role = db_.query(db_models.Roles).filter(
            func.lower(db_models.Roles.roleName) == func.lower(role.strip())).first()
        if not db_role:
            raise NotAvailableException(f"Role, {role.strip()},"+\
                " not found in Database")
        db_rules_list.append(
            db_models.AccessRules(
                entitlementId=entitlement.resourceTypeId,
                tagId=tag.permissionId,
                roleId=db_role.roleId,
                createdUser= user_id,
                updatedUser=user_id,
                active=True)
        )
    db_.add_all(db_rules_list)
    response = {
        'db_content':db_rules_list,
        'refresh_auth_func':generate_access_rules_dict
    }
    return response


def update_access_rules(db_: Session, details: schema_auth.AccessRuleUpdateInput, user_id= None):
    '''update a row in access rule table'''
    db_content = db_.query(db_models.AccessRules).get(details.ruleId)
    if not db_content:
        raise NotAvailableException(f"Access rule of Id {details.ruleId},"+\
        " not found in Database")
    if details.entitlement:
        entitlement = db_.query(db_models.ResourceTypes).filter(
            func.lower(db_models.ResourceTypes.resourceTypeName) ==\
                func.lower(details.entitlement.strip())).first()
        if not entitlement:
            raise NotAvailableException(f"Entitlement, {details.entitlement.strip()},"+\
                " not found in Database")
        db_content.entitlementId = entitlement.resourceTypeId
    if details.tag:
        tag = db_.query(db_models.Permissions).filter(
            func.lower(db_models.Permissions.permissionName) ==\
            func.lower(details.tag.strip())).first()
        if not tag:
            raise NotAvailableException(f"Tag, {details.tag.strip()},"+\
            " not found in Database")
        db_content.tagId =tag.permissionId
    if details.role:
        db_role = db_.query(db_models.Roles).filter(
            func.lower(db_models.Roles.roleName) == func.lower(details.role.strip())).first()
        if not db_role:
            raise NotAvailableException(f"Role, {details.role.strip()},"+\
                " not found in Database")
        db_content.roleId=db_role.roleId

    db_content.updatedUser = user_id
    db_content.active = True
    response = {
        'db_content':db_content,
        'refresh_auth_func':generate_access_rules_dict
    }
    return response

def get_access_rules(db_: Session, entitlement=None, tag=None, role=None, **kwargs):
    '''get rows from auth permission table'''
    user_id = kwargs.get("user_id",None)
    rule_id = kwargs.get("rule_id",None)
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.AccessRules)
    if rule_id:
        query = query.filter(db_models.AccessRules.ruleId == rule_id)
    elif user_id:
        user_data = get_all_or_one_kratos_users(user_id)
        user_roles = user_data[0]["traits"]["userrole"]
        query = query.filter(db_models.AccessRules.role.has\
            (db_models.Roles.roleName.in_(user_roles)))
    else :
        if entitlement:
            query = query.filter(db_models.AccessRules.entitlement.has
            (resourceTypeName = entitlement.strip()))
        if tag:
            query = query.filter(db_models.AccessRules.tag.has
            (permissionName = tag.strip()))
        if role:
            query = query.filter(db_models.AccessRules.role.has
            (roleName = role.strip()))
        if active:
            query = query.filter(db_models.AccessRules.active)
        else:
            query = query.filter(db_models.AccessRules.active == False) #pylint: disable=singleton-comparison
    return query.offset(skip).limit(limit).all()


def create_permission_map(db_: Session, details: schema_auth.PermissionMapCreateInput,\
    user_id= None):
    '''Add a row to permission map table'''

    endpoint_row = db_.query(db_models.ApiEndpoints).filter(and_(
        (func.lower(db_models.ApiEndpoints.endpoint) ==\
        func.lower(details.apiEndpoint)),
        (func.lower(db_models.ApiEndpoints.method) ==\
         details.method.lower())
        )).first()

    if not endpoint_row:
        raise NotAvailableException(f"endpoint- method combination of ,\
            {details.apiEndpoint.strip()}"+\
            f"-{details.method}, is not found in Database")

    app_row = db_.query(db_models.Apps).filter(
        func.lower(db_models.Apps.appName) ==\
            func.lower(details.requestApp.strip())).first()
    if not app_row:
        raise NotAvailableException(f"requestApp, {details.requestApp.strip()},"+\
            " is not a registered app")

    resource = db_.query(db_models.ResourceTypes).filter(
        func.lower(db_models.ResourceTypes.resourceTypeName) ==\
            func.lower(details.resourceType.strip())).first()
    if not resource:
        raise NotAvailableException(f"resourceType, {details.resourceType.strip()},"+\
            " not found in Database")

    permission = db_.query(db_models.Permissions).filter(
        func.lower(db_models.Permissions.permissionName) == \
            func.lower(details.permission.strip())).first()
    if not permission:
        raise NotAvailableException(f"permission, {details.permission.strip()},"+\
            " not found in Database")

    db_content = db_models.ApiPermissionsMap(
        endpointId=endpoint_row.endpointId,
        requestAppId=app_row.appId,
        resourceTypeId=resource.resourceTypeId,
        permissionId=permission.permissionId,
        filterResults=details.filterResults,
        createdUser= user_id,
        updatedUser=user_id,
        active=True)
    db_.add(db_content)

    response = {
        'db_content':db_content,
        'refresh_auth_func':generate_permission_map_table
    }
    return response

def create_endpoint(db_: Session, details, user_id= None):
    '''Add a row to endpoint table'''
    db_content = db_models.ApiEndpoints(endpoint = details.endpoint.lower(),
        method = details.method.upper(),
        createdUser= user_id,
        updatedUser=user_id,
        active=True)
    db_.add(db_content)
    return db_content

def update_endpoint(db_: Session, details, user_id= None):
    '''update a row to endpoint table'''
    db_content = db_.query(db_models.ApiEndpoints).get(details.endpointId)
    if details.endpoint:
        db_content.endpoint = details.endpoint
    if details.method:
        db_content.method = details.method
    db_content.updatedUser = user_id
    return db_content

def get_endpoints(db_: Session, endpoint_id, endpoint_name, method, **kwargs):
    '''get rows from endpoint table'''
    search_word = kwargs.get("search_word",None)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)

    query = db_.query(db_models.ApiEndpoints)
    if endpoint_name:
        query = query.filter(db_models.ApiEndpoints.endpoint ==\
            endpoint_name.lower())
    if method is not None:
        query = query.filter(func.lower(db_models.ApiEndpoints.method) ==\
            method.value.lower())
    if search_word:
        search = f"%{search_word.lower()}%"
        query = query.filter(func.lower(db_models.ApiEndpoints.endpoint).like(search))
    if endpoint_id is not None:
        query = query.filter(db_models.ApiEndpoints.endpointId == endpoint_id)
    return query.offset(skip).limit(limit).all()


def update_permission_map(db_: Session, details: schema_auth.PermissionMapUpdateInput,\
    user_id= None):#pylint: disable=too-many-branches
    '''update a row in permission map table'''
    db_content = db_.query(db_models.ApiPermissionsMap).get(details.permissionMapId)
    if not db_content:
        raise NotAvailableException(f"Api Permission Map of Id {details.permissionMapId},"+\
        " not found in Database")

    if details.apiEndpoint and details.method:
        endpoint_row = db_.query(db_models.ApiEndpoints).filter(and_(
        (func.lower(db_models.ApiEndpoints.endpoint) ==\
        func.lower(details.apiEndpoint)),
        (func.lower(db_models.ApiEndpoints.method) ==\
         details.method.lower())
        )).first()

        if not endpoint_row:
            raise NotAvailableException(f"endpoint- method combination of ,\
                {details.apiEndpoint.strip()}"+\
                f"-{details.method}, is not found in Database")
        db_content.endpointId = endpoint_row.endpointId
    else:
        raise NotAvailableException("please provide endpoint-method combo")

    if details.requestApp:
        app_row = db_.query(db_models.Apps).filter(
            func.lower(db_models.Apps.appName) ==\
            func.lower(details.requestApp.strip())).first()
        if not app_row:
            raise NotAvailableException(f"requestApp, {details.requestApp.strip()},"+\
                " is not a registered app")
        db_content.requestAppId = app_row.appId

    if details.resourceType:
        resource = db_.query(db_models.ResourceTypes).filter(
            func.lower(db_models.ResourceTypes.resourceTypeName) ==\
                func.lower(details.resourceType.strip())).first()
        if not resource:
            raise NotAvailableException(f"resourceType, {details.resourceType.strip()},"+\
                " not found in Database")
        db_content.resourceTypeId = resource.resourceTypeId

    if details.permission:
        permission = db_.query(db_models.Permissions).filter(
            func.lower(db_models.Permissions.permissionName) == \
                func.lower(details.permission.strip())).first()
        if not permission:
            raise NotAvailableException(f"permission, {details.permission.strip()},"+\
                " not found in Database")
        db_content.permissionId = permission.permissionId

    if details.filterResults:
        db_content.filterResults = details.filterResults

    db_content.updatedUser = user_id
    db_content.active = True

    response = {
        'db_content':db_content,
        'refresh_auth_func':generate_permission_map_table
    }
    return response

def get_api_permission_map(db_: Session, permission_map_id, endpoint, method, **kwargs):
    '''get rows from api permission map table'''
    app_name = kwargs.get("app_name",None)
    entitlement = kwargs.get("entitlement",None)
    permission_name = kwargs.get("permission_name",None)
    filter_results = kwargs.get("filter_results",None)
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)

    query = db_.query(db_models.ApiPermissionsMap)

    if permission_map_id:
        query = query.filter(db_models.ApiPermissionsMap.permissionMapId == permission_map_id)
    else:
        if endpoint:
            query = query.filter(db_models.ApiPermissionsMap.endpoint.has
            (endpoint = endpoint.strip()))
        if method:
            query = query.filter(db_models.ApiPermissionsMap.endpoint.has
            (method = method.strip().upper()))
        if app_name:
            query = query.filter(db_models.ApiPermissionsMap.requestApp.has
            (appName = app_name.strip()))
        if entitlement:
            query = query.filter(db_models.ApiPermissionsMap.resourceType.has
            (resourceTypeName = entitlement.strip()))
        if permission_name:
            query = query.filter(db_models.ApiPermissionsMap.permission.has
            (permissionName = permission_name.strip()))
        if filter_results:
            query = query.filter(db_models.ApiPermissionsMap.filterResults == filter_results)
        if active:
            query = query.filter(db_models.ApiPermissionsMap.active)
        else:
            query = query.filter(db_models.AccessRules.active == False) #pylint: disable=singleton-comparison


    return query.offset(skip).limit(limit).all()
