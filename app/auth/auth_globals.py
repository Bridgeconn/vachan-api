"""Authentication related Global varaibles and functions"""
from collections import defaultdict
from database import SessionLocal
import db_models
from dependencies import log
from custom_exceptions import GenericException

# Global Varialbles
APIPERMISSIONTABLE = []
ACCESS_RULES = defaultdict(lambda:defaultdict())#pylint: disable=unnecessary-lambda
#pylint: disable=use-dict-literal
RESOURCE_TYPE = dict()
APPS = dict()
INPUT_APPS = dict()
ROLES = []

#pylint: disable=broad-except, inconsistent-return-statements

# Functions
def generate_permission_map_table():
    """get permisison map table from db"""
    try:
        APIPERMISSIONTABLE.clear()
        db_instance = SessionLocal()
        db_api_permisison = db_instance.query(db_models.ApiPermissionsMap).all()
        for permisison_row in db_api_permisison:
            temp_row = [
                permisison_row.apiEndpoint,
                permisison_row.method,
                permisison_row.requestApp.appName,
                permisison_row.filterResults,
                permisison_row.resourceType.resourceTypeName,
                permisison_row.permission.permissionName
                ]
            APIPERMISSIONTABLE.append(temp_row[:])
        print("APi permisison map  : ", len(APIPERMISSIONTABLE))
        if len(APIPERMISSIONTABLE) <= 0:
            raise GenericException("Permission table loaded as empty")
        return APIPERMISSIONTABLE
    except Exception as err:
        print("Error Reading API permission table from DB :", err)
    finally:
        db_instance.close()

def generate_access_rules_dict():
    """get permisison map table from db"""
    try:
        db_instance = SessionLocal()
        ACCESS_RULES.clear()
        db_access_rule = db_instance.query(db_models.AccessRules).all()
        for rules_row in db_access_rule:
            ACCESS_RULES[rules_row.entitlement.resourceTypeName]\
                [rules_row.tag.permissionName]= rules_row.roles
        print("access rules : ", len(ACCESS_RULES))
        print(ACCESS_RULES)
        return ACCESS_RULES
    except Exception as err:
        # print("Error Generating Access Rules from DB :", e)
        log.error("Error Generating Access Rules from DB:%s", err)
    finally:
        db_instance.close()

def generate_resource_types():
    """get resource types from db"""
    try:
        db_instance = SessionLocal()
        RESOURCE_TYPE.clear()
        db_resource_type = db_instance.query(db_models.ResourceTypes).all()
        print()
        for resource_row in db_resource_type:
            RESOURCE_TYPE[resource_row.resourceTypeName]= resource_row.resourceTypeDescription
        print("resource type : ", len(RESOURCE_TYPE))
        return RESOURCE_TYPE
    except Exception as err:
        # print("Error Generating resource types from DB :", err)
        log.error("Error Generating resource types from DB:%s", err)
    finally:
        db_instance.close()

def generate_apps():
    """get apps from db"""
    try:
        db_instance = SessionLocal()
        APPS.clear()
        INPUT_APPS.clear()
        db_apps = db_instance.query(db_models.Apps).all()
        for app in db_apps:
            APPS[app.appName]= app.defaultRole
            if app.useForRegistration:
                INPUT_APPS[app.appName]= app.defaultRole
        print("Apps : ", len(APPS))
        print("Input Apps : ", len(INPUT_APPS))
        return APPS, INPUT_APPS
    except Exception as err:
        # print("Error Generating app and input apps from DB :", err)
        log.error("Error Generating app and input apps from DB:%s", err)
    finally:
        db_instance.close()

def generate_roles():
    """get roles from db"""
    try:
        db_instance = SessionLocal()
        ROLES.clear()
        db_roles = db_instance.query(db_models.Roles).all()
        for role in db_roles:
            ROLES.append(role.roleName)
        print("Roles : ", len(ROLES))
        return ROLES
    except Exception as err:
        # print("Error Generating roles from DB :", err)
        log.error("Error Generating roles from DB:%s", err)
    finally:
        db_instance.close()
