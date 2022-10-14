"""Authentication related Global varaibles and functions"""
from enum import Enum
from database import SessionLocal
from collections import defaultdict
import db_models

# Global Varialbles
APIPERMISSIONTABLE = []
ACCESS_RULES = defaultdict(lambda:defaultdict())
RESOURCE_TYPE = dict()
APPS = dict()
INPUT_APPS = dict()
ROLES = []

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
                permisison_row.requestApp,
                permisison_row.filterResults,
                permisison_row.resourceType,
                permisison_row.permission]
            APIPERMISSIONTABLE.append(temp_row[:])
        print("APi permisison map  : ", len(APIPERMISSIONTABLE))
        if len(APIPERMISSIONTABLE) <= 0:
            raise 
        return APIPERMISSIONTABLE
    except Exception as e:
        print("Error Reading API permission table from DB :", e)
    finally:
        db_instance.close()

def generate_access_rules_dict():
    """get permisison map table from db"""
    try:
        db_instance = SessionLocal()
        ACCESS_RULES.clear()
        db_access_rule = db_instance.query(db_models.AccessRules).all()
        for rules_row in db_access_rule:
            ACCESS_RULES[rules_row.entitlement][rules_row.tag]= rules_row.roles
        print("access rules : ", len(ACCESS_RULES))
    except Exception as e:
        print("Error Generating Access Rules from DB :", e)
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
    except Exception as e:
        print("Error Generating resource types from DB :", e)
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
    except Exception as e:
        print("Error Generating app and input apps from DB :", e)
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
    except Exception as e:
        print("Error Generating roles from DB :", e)
    finally:
        db_instance.close()

# reference fun to get db data
# def auth_selection(selection = 'file'):
#     try:
#         db_instance = SessionLocal()
#         if selection == 'db':
#             # permisison map
#             db_apiPermisison = db_instance.query(db_models.ApiPermissionsMap).all()
#             for permisison_row in db_apiPermisison:
#                 temp_row = [
#                     permisison_row.apiEndpoint,
#                     permisison_row.method,
#                     permisison_row.requestApp,
#                     permisison_row.filterResults,
#                     permisison_row.resourceType,
#                     permisison_row.permission]
#                 APIPERMISSIONTABLE.append(temp_row[:])
#             #access rules json
#             from collections import defaultdict
#             ACCESS_RULES = defaultdict(lambda:defaultdict())
#             db_access_rule = db_instance.query(db_models.AccessRules).all()
#             for rules_row in db_access_rule:
#                 # print("rules list  : ", rules_row.__dict__)
#                 ACCESS_RULES[rules_row.entitlement][rules_row.tag]= rules_row.roles

#         elif selection == 'file':
#             ####################### Access control logics ######################################
#             with open('auth/access_rules.json','r') as file:
#                 ACCESS_RULES = json.load(file)
#                 log.warning("Startup event to read Access Rules")
#                 log.debug(ACCESS_RULES)

#             with open('auth/api-permissions.csv','r') as file:
#                 csvreader = csv.reader(file)
#                 header = next(csvreader)
#                 for table_row in csvreader:
#                     APIPERMISSIONTABLE.append(table_row)
#                 log.warning("Startup event to load permission table")
#                 log.debug(APIPERMISSIONTABLE)
#     finally:
#         db_instance.close()
#         return APIPERMISSIONTABLE, ACCESS_RULES
#         # print("permsision table in final : ", len(APIPERMISSIONTABLE))
#         # print("access rules dict in final: ", len(ACCESS_RULES))

# # --------------call map and rule function -------------------
