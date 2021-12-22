'''returns the required permission name as per the access rules'''
#pylint: disable=E0401
import csv
from schema import schema_auth
from dependencies import log

APIPERMISSIONTABLE = []
#pylint: disable=too-many-locals,too-many-statements
def api_permission_map(endpoint, request_context, requesting_app, resource, user_details):
    '''returns the required permission name as per the access rules'''
    message = "API's required permission not defined"
    method = request_context['method']
    permission = None
    # check sourcename is present or not
    if not request_context['path_params'] == {} and\
        'source_name' in request_context['path_params'].keys():
        source_name = request_context['path_params']['source_name']
    else:
        source_name = None
    
    if requesting_app == schema_auth.App.AG:
        print("matched------------------->",schema_auth.App.AG)
    print("requesting_app--->",requesting_app)

    #Finding permission from table
    filtered_table = []
    for i in range(1,len(APIPERMISSIONTABLE)):
        if endpoint == APIPERMISSIONTABLE[i][schema_auth.TableHeading.ENDPOINT.value] and \
            method == APIPERMISSIONTABLE[i][schema_auth.TableHeading.METHOD.value]:
            requestapp_status = True
            resourcetype_status = True

            if not APIPERMISSIONTABLE[i][schema_auth.TableHeading.REQUESTAPP.value] == 'None':
                if not requesting_app == APIPERMISSIONTABLE[i][schema_auth.TableHeading.REQUESTAPP.value]:
                    requestapp_status = False
            if APIPERMISSIONTABLE[i][schema_auth.TableHeading.USERNEEDED.value] == "True":
                if 'error' in user_details.keys():
                    raise user_details['error']
            if not APIPERMISSIONTABLE[i][schema_auth.TableHeading.RESOURCETYPE.value] == 'None':
                if not resource.name == APIPERMISSIONTABLE[i][schema_auth.TableHeading.REQUESTAPP.value]:
                    resourcetype_status = False
            if requestapp_status and resourcetype_status:
                filtered_table.append(APIPERMISSIONTABLE[i])
    print("filtered-------------->",filtered_table)

#Initialize CSV Permissions
def initialize_apipermissions():
    """Function to read JSON file with access rules"""
    global APIPERMISSIONTABLE#pylint: disable=W0603
    if not len(APIPERMISSIONTABLE) > 0:
        with open('auth/api-permissions.csv','r') as file:
            csvreader = csv.reader(file)
            header = next(csvreader)
            APIPERMISSIONTABLE.append(header)
            for row in csvreader:
                APIPERMISSIONTABLE.append(row)
            log.warning("Startup event to load permission table")
            log.warning(APIPERMISSIONTABLE)
    return APIPERMISSIONTABLE