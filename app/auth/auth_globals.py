"""Authentication related Global varaibles and functions"""
from database import SessionLocal
from collections import defaultdict
import db_models

# Global Varialbles
APIPERMISSIONTABLE = []
ACCESS_RULES = defaultdict(lambda:defaultdict())


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
    except:
        print("Error Reading API permission table from DB")
    finally:
        db_instance.close()

# Get Access Rules Table
def generate_access_rules_dict():
    """get permisison map table from db"""
    try:
        db_instance = SessionLocal()
        ACCESS_RULES.clear()
        db_access_rule = db_instance.query(db_models.AccessRules).all()
        for rules_row in db_access_rule:
            ACCESS_RULES[rules_row.entitlement][rules_row.tag]= rules_row.roles
        print("access rules : ", len(ACCESS_RULES))
    except:
        print("Error Generating Access Rules from DB")
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
