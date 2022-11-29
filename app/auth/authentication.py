"""Authentication related functions related to Kratos API accesses and our access control logics"""
import os
import json
# import csv
from functools import wraps
import requests
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import db_models
from auth import utils
from dependencies import log
from custom_exceptions import GenericException ,\
    AlreadyExistsException,NotAvailableException,UnAuthorizedException,\
    UnprocessableException, PermissionException, NotAcceptableException
from auth.auth_globals import APIPERMISSIONTABLE, ACCESS_RULES, ROLES, \
    RESOURCE_TYPE, APPS, INPUT_APPS#pylint: disable=ungrouped-imports, unused-import

PUBLIC_BASE_URL = os.environ.get("VACHAN_KRATOS_PUBLIC_URL",
                                    "http://127.0.0.1:4433/")+"self-service/"
ADMIN_BASE_URL = os.environ.get("VACHAN_KRATOS_ADMIN_URL", "http://127.0.0.1:4434/")
USER_SESSION_URL = os.environ.get("VACHAN_KRATOS_PUBLIC_URL",
                                "http://127.0.0.1:4433/")+ "sessions/whoami"
SUPER_USER = os.environ.get("VACHAN_SUPER_USERNAME")
SUPER_PASSWORD = os.environ.get("VACHAN_SUPER_PASSWORD")

def get_token_schema_type(recieve_token):
    """get current token is app or user"""
    headers = {}
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {recieve_token}"
    user_data = requests.get(USER_SESSION_URL, headers=headers, timeout=10)
    if user_data.status_code == 200:
        schema_type = json.loads(user_data.content)["identity"]["schema_id"]
    else:
        schema_type = None
    return schema_type

def get_current_user_data(recieve_token, app=False):
    """get current user details"""
    details = {}
    headers = {}
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {recieve_token}"
    user_data = requests.get(USER_SESSION_URL, headers=headers, timeout=10)
    data = json.loads(user_data.content)
    if user_data.status_code == 200 and not app:
        if data["identity"]["schema_id"] == "app":
            raise UnprocessableException("The User or token is not a valid type")
        details["user_id"] = data["identity"]["id"]
        if "userrole" in data["identity"]["traits"]:
            details["user_roles"] = data["identity"]["traits"]["userrole"]
        else:
            details["user_roles"] = ""
    elif user_data.status_code == 200 and app:
        if data["identity"]["schema_id"] != "app":
            raise UnprocessableException("The token is not a valid type")
        details["app_id"] = data["identity"]["id"]
        details["app_name"] = data["identity"]["traits"]["name"]
    elif user_data.status_code == 401:
        if app:
            raise UnAuthorizedException("Requesting app is not registered")
        details["user_id"] =None
        details["user_roles"] = ['noAuthRequired']
        details["error"] = UnAuthorizedException(detail=data["error"])
    elif user_data.status_code == 500:
        if app:
            raise UnAuthorizedException("Requesting app is not registered")
        details["user_id"] =None
        details["user_roles"] = ['noAuthRequired']
        details["error"] = GenericException(detail=data["error"])
    return details

#optional authentication with token or none
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
async def get_user_or_none(token: str = Depends(optional_oauth2_scheme)):
    """optional auth for getting token of logined user not raise error if no auth"""
    user_details = get_current_user_data(token)
    return user_details

#Get user or none for graphql
#get token for graphql requests
def get_user_or_none_graphql(info):
    """get token and user details for graphql"""
    req = info.context["request"]
    if 'Authorization' in req.headers:
        token = req.headers['Authorization']
        token = token.split(' ')[1]
    else:
        token = None
    user_details = get_current_user_data(token)
    return user_details, req

def get_default_role_for_app(app_key):
    """get defaulr user role for app"""
    client_app = get_current_user_data(app_key, app=True)["app_name"].lower()
    user_role = [(app, role) for app, role in INPUT_APPS.items()\
        if app.lower() == client_app.lower() ]
    if len(user_role) > 0:
        user_role = user_role[0][1]
    else:
        raise NotAcceptableException("The requested app Not allowed to register Users")
    return user_role

def api_resourcetype_map(endpoint, path_params=None):
    '''Default correlation between API endpoints and resource they act upon'''
    if endpoint.split('/')[2] in ["contents", "languages", "licenses", 'versions']:
        resource_type = 'meta-content'
    elif endpoint.startswith('/v2/autographa/project'):
        resource_type = 'project'
    elif endpoint.startswith('/v2/user'):
        resource_type = 'user'
    elif endpoint.startswith('/v2/app'):
        resource_type = 'app'
    elif endpoint.startswith("/v2/translation") or endpoint.startswith("/v2/nlp"):
        resource_type = 'translation'
    elif endpoint.startswith("/v2/lookup"):
        resource_type = 'lookup-content'
    elif endpoint.startswith("/v2/jobs"):
        resource_type = 'jobs'
    elif endpoint.startswith("/v2/media"):
        resource_type = 'media'
    elif endpoint.startswith("/v2/files"):
        resource_type = "file-ops"
    elif endpoint.startswith("/v2/sources") or (
        path_params is not None and "source_name" in path_params):
        resource_type = 'content'
    else:
        raise GenericException("Resource Type of API not defined")
    if not resource_type.lower() in [key.lower() for key in RESOURCE_TYPE]:
        raise GenericException("Resource Type not defined in DB")
    return resource_type


def search_api_permission_map(endpoint, method, client_app, path_params=None, resource=None):
    '''look up request params in the api-permission table loaded from CSV'''
    # log.debug("Looking up api permission map for\n>>>>endpoint:%s, \n>>>method:%s, client_app:%s",
    #     endpoint, method,client_app)
    req_url = endpoint
    if not req_url.endswith("/"):
        req_url += "/"
    for key in path_params:
        req_url = req_url.replace("/"+path_params[key]+"/", "/*/")
    if resource is None:
        resource = api_resourcetype_map(endpoint, path_params)
    # log.debug("\n>>>>resource:%s", resource)
    for row in APIPERMISSIONTABLE:
        table_url = row[0]
        if not table_url.endswith("/"):
            table_url += "/"
        for key in path_params:
            table_url = table_url.replace("{"+key+"}", "*")
        if table_url == req_url:
            if row[1].upper() == method.upper():
                if row[2].lower() == client_app.lower():
                    if row[4].lower() == resource.lower():
                        log.debug("API-Permission map:%s, resource:%s", row[5], resource)
                        return (resource, row[5])
    log.error("No permisions map found for:%s, %s, %s, %s", endpoint, method, client_app, resource)
    raise PermissionException("API-Permission map not defined for the request!")

def get_access_tag(db_, resource_type, path_params=None, kw_args = None, resource=None):
    '''obtain access tag based on resource-url direct link or value stored in DB'''
    db_resources = [key.lower() for key in RESOURCE_TYPE]
    resource_tag_map = {
        'user': ['user'],
        'app': ['app'],
        'project': ['translation-project'],
        'translation': ['generic-translation'],
        'lookup-content': ['lookup-content'],
        'meta-content': ["meta-content","open-access"],
        'research-use': ['content', 'research-use'],
        'jobs': ['jobs'],
        'media': ['media'],
        'file-ops': ['file-ops']
        # schema_auth.ResourceType.CONTENT: None # excluded to use item specific tags in db
    }
    if resource_type.lower() in resource_tag_map and resource_type.lower() in db_resources:
        return resource_tag_map[resource_type]
    if path_params is not None and "source_name" in path_params:
        db_entry = db_.query(db_models.Source.metaData['accessPermissions']).filter(
            db_models.Source.sourceName == path_params['source_name']).first()
        if db_entry is not None:
            return db_entry[0] if len([x for x in db_entry[0] if x.lower()\
                in db_resources]) > 0 else []
    if kw_args is not None and "source_name" in kw_args:
        db_entry = db_.query(db_models.Source.metaData['accessPermissions']).filter(
            db_models.Source.sourceName == kw_args['source_name']).first()
        if db_entry is not None:
            return db_entry[0] if len([x for x in db_entry[0] if x.lower()\
                in db_resources]) > 0 else []
    if resource:
        return resource.metaData['accessPermissions'] if len([x for x in \
            resource.metaData['accessPermissions']\
            if x.lower() in db_resources]) > 0 else []
    if resource_type == 'content':
        return ['content']
    return []

def is_project_owner(db_:Session, db_resource, user_id):
    '''checks if the user is the owner of the given project'''
    project_id = db_resource.projectId
    project_owners = db_.query(db_models.TranslationProjectUser.userId).filter(
        db_models.TranslationProjectUser.project_id == project_id,#pylint: disable=comparison-with-callable
        db_models.TranslationProjectUser.userRole == "projectOwner").all()
    project_owners = [id for id, in project_owners]
    if user_id in project_owners:
        return True
    return False

def is_project_member(db_:Session, db_resource, user_id):
    '''checks if the user is the memeber of the given project'''
    project_id = db_resource.projectId
    project_members = db_.query(db_models.TranslationProjectUser.userId).filter(
        db_models.TranslationProjectUser.project_id == project_id,#pylint: disable=comparison-with-callable
        db_models.TranslationProjectUser.userRole == "projectMember").all()
    project_members = [id for id, in project_members]
    if user_id in project_members:
        return True
    return False

def check_right(user_details, required_rights, resp_obj=None, db_=None):
    '''Use user details and info about requested action or resource to ensure right'''
    log.warning("In check_right with user_details: %s, required_rights:%s, resp_obj:%s",
        user_details, required_rights, resp_obj)
    valid = False
    if "noAuthRequired" in required_rights:
        valid =  True
    if "registeredUser" in required_rights and user_details["user_id"] is not None:
        valid =  True
    for role in user_details['user_roles']:
        if role in required_rights:
            valid =  True
    if valid:
        return True
    if resp_obj is not None and db_ is not None:
        try:
            if "resourceCreatedUser" in required_rights and \
                    user_details['user_id'] == resp_obj.createdUser:
                valid = True
            if "projectOwner" in required_rights and \
                is_project_owner(db_, resp_obj, user_details['user_id']):
                valid = True
            if "projectMember" in required_rights and \
                is_project_member(db_, resp_obj, user_details['user_id']):
                valid = True
            if valid:
                return True
        except Exception as exe: # pylint: disable=W0703
            log.warning("Error in check right")
            log.warning(exe)
    return False


def get_auth_access_check_decorator(func):#pylint:disable=too-many-statements
    """Decorator function for auth and access check for all routers"""
    @wraps(func)
    async def wrapper(*args, **kwargs):#pylint: disable=too-many-branches,too-many-statements, too-many-locals
        # log.debug("\n\n\n********New auth check, for a resource access or operation************")
        request = kwargs.get('request')
        db_ = kwargs.get("db_")
        endpoint = request.url.path
        method = request.method
        path_params = request.path_params
        user_details = kwargs.get('user_details')
        resource_type = kwargs.get("operates_on", None)
        requested_app_key = kwargs.get("app_key", None)
        filtering_required = kwargs.get("filtering_required", False)
        # checking Requested App
        if requested_app_key is not None and \
            requested_app_key.get_secret_value() not in ('None',''):
            print("app key ==============> ", requested_app_key.get_secret_value())
            client_app = get_current_user_data(requested_app_key.get_secret_value()\
                , app=True)['app_name']
            print("request from app name ---------->", client_app)
            if not client_app.lower() in [key.lower() for key in APPS]:
                print(" ERROR : -----> Not a Valid app , app is not registred ")
                raise UnAuthorizedException("Requesting app is not registered")
        else:
            if 'API-user' in APPS:
                print("app key in else ==============> ", "API User")
                client_app = 'API-user'
            else:
                raise NotAvailableException('Not a Valid app , app is not registred ')

        # Getting user details if no auth header and have token
        if not "authorization" in request.headers and \
            "access_token" in kwargs:
            user_details = get_current_user_data(kwargs.get("access_token"))
        # checking resource type  and permission requiered for request
        resource_type, permission = search_api_permission_map(
            endpoint, method, client_app, path_params, resource=resource_type)
        if not endpoint.startswith('/v2/user'):
            print("resource_type : ", resource_type, "| permisison : ",\
                permission, "endpoint : ", endpoint)

        required_rights = []
        access_tags = get_access_tag(db_, resource_type, path_params, kwargs)
        for tag in access_tags:
            if tag in ACCESS_RULES and permission in ACCESS_RULES[tag]:
                required_rights += ACCESS_RULES[tag][permission]
        if not endpoint.startswith('/v2/user'):
            print("req rights ==== : ", required_rights)
        authenticated = check_right(user_details, required_rights)
        if not endpoint.startswith('/v2/user'):
            print("AUTH DETAILS DICT : ----> ",{"required_rights":required_rights,\
                "| access_tags":access_tags,\
                "| permission":permission," | resource_type":resource_type," | endpoint":endpoint,"\
                | method":method," | path_params":path_params," | user_details":user_details,"\
                | resource_type":resource_type," | filtering_required":filtering_required," | \
                client_app":client_app,"| authenticated":authenticated})
        # if (resource_type == schema_auth.ResourceType.USER and not authenticated):
        if ('user' in RESOURCE_TYPE and resource_type == 'user' and not authenticated):
            # Need to raise error before function execution, as we cannot delay db commit
            # like we do in other cases as changes happen in Kratos db, not app db'''
            if user_details['user_id'] is None:
                raise UnAuthorizedException("Access token not provided or user not recognized")
            #check for created user
            if len(path_params)>0 :
                obj = utils.ConvertDictObj()
                obj['createdUser'] = path_params["user_id"]
                authenticated = check_right(user_details, required_rights, obj, db_)
                if not authenticated:
                    raise PermissionException("Access Permission Denied for the URL")
            else:
                raise PermissionException("Access Permission Denied for the URL")

        ###### Executing the API function #######
        response = await func(*args, **kwargs)
        #########################################
        obj = None
        if isinstance(response, dict):
            # separating out intended response and (source/project)object passed for auth check
            if "db_content" in response:
                if "source_content" in response:
                    obj = response['source_content']
                if "project_content" in response:
                    obj = response['project_content']
                response = response['db_content']
            elif "data" in response:
                if isinstance(response['data'], dict) and "db_content" in response['data']:
                    if "source_content" in response['data']:
                        obj = response['data']['source_content']
                    if "project_content" in response['data']:
                        obj = response['data']['project_content']
                    response['data'] = response['data']['db_content']
                else:
                    obj = response['data']
        # log.debug("authenticated:%s", authenticated)
        # log.debug("OBJ:%s",obj)
        if authenticated:
            # All no-auth and role based cases checked and appoved if applicable
            if db_:
                db_.commit()

        elif obj is not None:
            # Resource(item) specific checks
            if check_right(user_details, required_rights, obj, db_):
                if db_:
                    db_.commit()
            else:
                if user_details['user_id'] is None:
                    raise UnAuthorizedException("Access token not provided or user not recognized.")
                raise PermissionException("Access Permission Denied for the URL")
        elif isinstance(response, list) and filtering_required:
            filtered_response = []
            for item in response:
                required_rights_thisitem = required_rights.copy()
                access_tags = get_access_tag(db_, resource_type, path_params, kwargs, item)
                print("access_tags :: ======= > :: ", access_tags, "path params : ", \
                    path_params, "resource : ", resource_type, "item : ", item)
                for tag in access_tags:
                    if tag in ACCESS_RULES and permission in ACCESS_RULES[tag]:
                        required_rights_thisitem += ACCESS_RULES[tag][permission]
                if check_right(user_details, required_rights_thisitem, item, db_):
                    filtered_response.append(item)
            response = filtered_response
        else:
            log.error("Unable to Authenticate")
            if user_details['user_id'] is None:
                raise UnAuthorizedException("Access token not provided or user not recognized.")
            raise PermissionException("Access Permission Denied for the URL")
        return response
    return wrapper


######################################### Kratos Auth Functions ####################

#kratos Logout
def kratos_logout(recieve_token, app=False):
    """logout function"""
    # recieve_token = auth.credentials
    schema_type = get_token_schema_type(recieve_token=recieve_token)
    if (app and schema_type == 'app') or (not app and schema_type != 'app') :
        payload = {"session_token": recieve_token}
        headers = {}
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        logout_url = PUBLIC_BASE_URL + "logout/api"
        response = requests.delete(logout_url, headers=headers, json=payload, timeout=10)
        if response.status_code == 204:
            if schema_type == 'app':
                data = {"message":"Key deleted Successfully"}
            else:
                data = {"message":"Successfully Logged out"}
        elif response.status_code == 400:
            data = json.loads(response.content)
        elif response.status_code == 403:
            data = "The provided Session Token could not be found,"+\
                    "is invalid, or otherwise malformed"
            raise HTTPException(status_code=403, detail=data)
        elif response.status_code == 500:
            data = json.loads(response.content)
            raise GenericException(data["error"])
        return data
    raise UnprocessableException("Token is not the requiered type , malformed or Invalid")

#pylint: disable=R1703
def get_users_kratos_filter(base_url,name,roles,limit,skip):#pylint: disable=too-many-locals
    """v2/users filter block"""
    response = requests.get(base_url, timeout=10)
    if response.status_code == 200:#pylint: disable=too-many-nested-blocks
        user_data = []
        for data in json.loads(response.content):
            if not data["schema_id"] == 'app':
                name_status = True
                role_status = True
                kratos_user = {
                    "userId":data["id"],
                    "name":data["traits"]["name"]
                }
                kratos_user["name"]["fullname"] = data["traits"]["name"]["first"].capitalize() \
                    + " "+ data["traits"]["name"]["last"].capitalize()
                if not name is None:
                    if name.lower() == kratos_user["name"]["fullname"].lower() or\
                        name.lower() == kratos_user["name"]["last"].lower() or\
                            name.lower() == kratos_user["name"]["first"].lower():
                        name_status = True
                    else:
                        name_status = False

                if roles is not None and len(roles) > 0:
                    kratos_role = [x.lower() for x in data["traits"]["userrole"]]
                    role_status = False
                    for role in roles:
                        if role.lower() not in [db_role.lower() for db_role in  ROLES]:
                            raise NotAvailableException(f"Role {role} is not a valid one")
                        if role.lower() in kratos_role:
                            role_status = True
                            break
                if name_status and role_status:
                    user_data.append(kratos_user)
        user_data = user_data[skip:skip+limit] if skip>=0 and limit>=0 else []
        # user_data = user_data[skip:skip+limit]
        return user_data
    raise GenericException(detail=json.loads(response.content))

#get all or single user details
def get_all_or_one_kratos_users(rec_user_id=None,skip=None,limit=None,name=None,roles=None):
    """get all user info or a particular user details"""
    base_url = ADMIN_BASE_URL+"identities/"
    #all users
    if rec_user_id is None:
        if skip is None and limit is None:
            response = requests.get(base_url, timeout=10)
            if response.status_code == 200:
                user_data = json.loads(response.content)
            else:
                raise UnAuthorizedException(detail=json.loads(response.content))
        #v2/users
        else:
            user_data = get_users_kratos_filter(base_url,name,roles,limit,skip)
    #single user
    else:
        response = requests.get(base_url+rec_user_id, timeout=10)
        if response.status_code == 200:
            data = json.loads(response.content)
            user_data = [{
                "userId":data["id"],
                "name":data["traits"]["name"],
                "traits":""
            }]
            user_data[0]["name"]["fullname"] = data["traits"]["name"]["first"].capitalize() \
                + " "+ data["traits"]["name"]["last"].capitalize()
            user_data[0]["traits"] = data["traits"]
        else:
            raise NotAvailableException("User does not exist")
    return user_data

def update_kratos_user(rec_user_id,data):
    """update kratos user profile"""
    base_url = ADMIN_BASE_URL+"identities/"+rec_user_id
    #check valid user
    fetch_data = get_all_or_one_kratos_users(rec_user_id=rec_user_id)[0]["traits"]
    fetch_data["name"].pop("fullname")
    fetch_data["name"]["last"] = data.lastname
    fetch_data["name"]["first"] = data.firstname
    payload = json.dumps({"traits":fetch_data, "schema_id":"default"})
    headers = {'Content-Type': 'application/json'}
    response = requests.put(base_url, headers=headers, data=payload, timeout=10)
    if response.status_code == 200:
        response = json.loads(response.content)
        user_data = {
                    "userId":response["id"],
                    "name":response["traits"]["name"]}
        user_data["name"]["fullname"] = response["traits"]["name"]["first"].capitalize() \
                    + " "+ response["traits"]["name"]["last"].capitalize()
    elif response.status_code == 404:
        raise NotAvailableException(json.loads(response.content)["error"]["details"])
    elif response.status_code == 500:
        raise GenericException(json.loads(response.content)["error"]["details"])
    return user_data

#User registration with credentials
def register_check_success(reg_response):
    """register reqirement success"""
    name_path = reg_response["identity"]["traits"]["name"]
    name_path["first"] = '' if 'first' not in name_path else name_path["first"]
    name_path["last"] = '' if 'last' not in name_path else name_path["last"]
    data={
        "message":"Registration Successfull",
        "registered_details":{
            "id":reg_response["identity"]["id"],
            "email":reg_response["identity"]["traits"]["email"],
            "Name":str(name_path["first"]) + " " + str(name_path["last"]),
            "Permissions": reg_response["identity"]["traits"]["userrole"]
        },
        "token":reg_response["session_token"]
    }

    user_permision = data["registered_details"]['Permissions']
    # switcher = {
    #     schema_auth.AdminRoles.AGUSER.value : schema_auth.App.AG.value,
    #     schema_auth.AdminRoles.VACHANUSER.value : schema_auth.App.VACHAN.value,
    #         }
    # user_role =  switcher.get(user_permision[0], schema_auth.App.API.value)
    if user_permision[0] in list(INPUT_APPS.values()):
        user_role = list(INPUT_APPS.keys())[list(INPUT_APPS.values()).index(user_permision[0])]
    else:
        if "API-user" in list(INPUT_APPS.keys()):#pylint: disable=C0201
            user_role = "API-user"
        else:
            raise NotAvailableException('No app is associated to the role')
    data["registered_details"]['Permissions'] = [user_role]
    return data

def register_exist_update_user_role(kratos_users, email, user_role, reg_req, reg_response):
    """#existing account : - update user role"""
    data = {}
    for user in kratos_users:
        if email == user["traits"]["email"]:
            current_user_id = user["id"]
            if user_role not in user["traits"]["userrole"] and \
                'SuperAdmin' not in user["traits"]["userrole"]:
                role_list = [user_role]
                return_data = user_role_add(current_user_id,role_list)
                if return_data["Success"]:
                    data={
                        "message":"User Already Registered, New Permission updated",
                        "registered_details":{
                            "id":current_user_id,
                            "email":email,
                            "Permissions": return_data["role_list"]
                            }
                    }
            else:
                raise HTTPException(status_code=reg_req.status_code, \
                    detail=reg_response["ui"]["messages"][0]["text"])
    return data

def register_flow_fail(reg_response,email,user_role,reg_req):
    """register flow fails account already exist"""
    if "messages" in reg_response["ui"]:
        err_msg = \
    "An account with the same identifier (email, phone, username, ...) exists already."
        err_txt = reg_response["ui"]["messages"][0]["text"]
        if err_txt == err_msg:
            kratos_users = get_all_or_one_kratos_users()

            #update user role for exisiting user
            data = register_exist_update_user_role(kratos_users, email,
                user_role, reg_req, reg_response)
            user_permision = data["registered_details"]['Permissions']
            conv_permission = []
            for perm in user_permision:
                if perm in list(INPUT_APPS.values()):
                    role = list(INPUT_APPS.keys())[list(INPUT_APPS.values()).index(perm)]
                else:
                    if "API-user" in list(INPUT_APPS.keys()):#pylint: disable=C0201
                        role = "API-user"
                    else:
                        raise NotAvailableException('No app is associated to the role')
                conv_permission.append(role)
                data["registered_details"]['Permissions'] = conv_permission
        else:
            raise HTTPException(status_code=reg_req.status_code,\
                    detail=reg_response["ui"]["messages"][0]["text"])
    else:
        error_base = reg_response['ui']['nodes']
        for i in range(1,3):
            if error_base[i]['messages'] != []:
                raise UnprocessableException(error_base[i]['messages'][0]['text'])
    return data

def user_register_kratos(register_details, request, app_key=None):#pylint: disable=unused-argument
    """user registration kratos"""
    data = {}
    email = register_details.email
    password = register_details.password

    # get user role
    if app_key is not None and app_key.get_secret_value() not in ('None',''):
        user_role = get_default_role_for_app(app_key.get_secret_value())
    else:
        user_role = 'APIUser'

    register_url = PUBLIC_BASE_URL+"registration/api"
    reg_flow = requests.get(register_url, timeout=10)
    if reg_flow.status_code == 200:
        flow_res = json.loads(reg_flow.content)
        reg_flow_id = flow_res["ui"]["action"]
        reg_data = {"traits.email": email,
                     "traits.name.first": register_details.firstname,
                     "traits.name.last": register_details.lastname,
                     "password": password.get_secret_value(),
                     "traits.userrole":user_role,
                     "method": "password"}
        headers = {}
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        reg_req = requests.post(reg_flow_id,headers=headers,json=reg_data, timeout=10)
        reg_response = json.loads(reg_req.content)
        if reg_req.status_code == 200:
            data = register_check_success(reg_response)
            # print("in reg check success -->: ", data)
        elif reg_req.status_code == 400:
            data = register_flow_fail(reg_response,email,user_role,reg_req)
        else:
            log.error("Unexpected response from Kratos")
            log.error(reg_req.status_code)
            log.error(reg_req.json())
            raise GenericException("Got unexpected response from Kratos")
    return data


def login_kratos(user_email,password,from_app=False):#pylint: disable=R1710
    "kratos login"
    data = {"details":"","token":""}
    login_url = PUBLIC_BASE_URL+"login/api/"
    flow_res = requests.get(login_url, timeout=10)
    if flow_res.status_code == 200:
        flow_res = json.loads(flow_res.content)
        flow_id = flow_res["ui"]["action"]
        password = password.get_secret_value() if not isinstance(password, str) else password
        cred_data = {"password_identifier": user_email,
            "password": password, "method": "password"}
        login_req = requests.post(flow_id, json=cred_data, timeout=10)
        login_req_content = json.loads(login_req.content)
        if login_req.status_code == 200:
            session_id = login_req_content["session_token"]
            if (from_app and login_req_content["session"]["identity"]["schema_id"] == 'app') or \
                (not from_app and login_req_content["session"]["identity"]["schema_id"] != 'app'):
                if from_app:
                    data["message"] = "Key generated successfully"
                    data["key"] = session_id
                    data["appId"] = login_req_content["session"]["identity"]["id"]
                else:
                    data["message"] = "Login Succesfull"
                    data["token"] = session_id
                    data["userId"] = login_req_content["session"]["identity"]["id"]
            else:
                raise UnprocessableException\
                    ("can not perform operation, input is not expected type for the api")
        else:
            raise UnAuthorizedException(login_req_content["ui"]["messages"][0]["text"])
    return data

#delete an identity
def delete_identity(user_id, app=False):
    """delete identity"""
    base_url = ADMIN_BASE_URL+"identities/"+user_id
    get_details = requests.get(base_url, timeout=10)
    schema_type = json.loads(get_details.content)["schema_id"]
    if (app and schema_type == 'app') or (not app and schema_type != 'app') :
        response = requests.delete(base_url, timeout=10)
        if response.status_code == 404:
            raise NotAvailableException("Unable to locate the resource")
        # log.warning(response)
        # log.warning(response.content)
        return response
    raise UnprocessableException("can not perform operation, ID not the requiered type")

#user role add
def user_role_add(user_id,roles_list):
    """user role add from admin"""
    base_url = ADMIN_BASE_URL+"identities/"
    url = base_url + str(user_id)

    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        user_data = json.loads(response.content)

    else:
        raise NotAvailableException("Requested User Not Found")

    schema_id = user_data["schema_id"]
    state = user_data["state"]
    traits = user_data["traits"]
    exist_roles = []

    if '' in roles_list or len(roles_list) == 0 or None in roles_list:
        roles_list = ['']

    for role in roles_list:
        if role not in ROLES:
            raise NotAvailableException(f"Role {role} is not a valid one")
        if role in traits["userrole"]:
            exist_roles.append(role)
        else:
            traits["userrole"].append(role)
    roles_list = traits["userrole"]

    data = {
    "schema_id": schema_id,
    "state": state,
    "traits": traits
    }

    if len(exist_roles) > 0:
        raise AlreadyExistsException(f"Already Exist permisions {exist_roles}")

    headers = {}
    headers["Content-Type"] = "application/json"
    response = requests.put(url,headers=headers,json=data, timeout=10)

    if response.status_code == 200:
        resp_data = json.loads(response.content)
        #pylint: disable=R1705
        if roles_list == resp_data["traits"]["userrole"]:
            return {"Success":True,"message":"User Roles Updated",
                    "role_list": resp_data["traits"]["userrole"]
            }
        else:
            raise GenericException("User Role not updated properly.Check details provided")
    else:
        raise GenericException(response.content)


#Create Super User
def create_super_user():
    """function to create super user on startup"""
    super_user_url = ADMIN_BASE_URL+ "identities"
    found = False
    response = requests.get(super_user_url, timeout=10)
    if response.status_code == 200:
        identity_data = json.loads(response.content)
        for identity in identity_data:
            if "userrole" in  identity["traits"] and \
            "SuperAdmin" in identity["traits"]["userrole"]:
                found = True
                break
    else:
        raise HTTPException(status_code=401, detail=json.loads(response.content))
    if not found:
        register_url = PUBLIC_BASE_URL+"registration/api"
        reg_flow = requests.get(register_url, timeout=10)
        if reg_flow.status_code == 200:
            flow_res = json.loads(reg_flow.content)
            reg_flow_id = flow_res["ui"]["action"]
            reg_data = {"traits.email": SUPER_USER,
                        "traits.name.first": "Super",
                        "traits.name.last": "Admin",
                        "password": SUPER_PASSWORD,
                        "traits.userrole":"SuperAdmin",
                        "method": "password"}
            headers = {}
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            reg_req = requests.post(reg_flow_id,headers=headers,json=reg_data, timeout=10)
            if reg_req.status_code == 200:
                log.info('Super Admin created')
            elif reg_req.status_code == 400:
                #check for any error and throw from content
                for err_dict in json.loads(reg_req.content)["ui"]["nodes"]:
                    if len(err_dict["messages"]) > 0:
                        err_attribute = err_dict['attributes']['name']
                        error_detail = \
                            f"{err_attribute} error :{err_dict['messages'][0]['text']}"
                        log.error("Super User Creation Error :%s",error_detail)
                        raise HTTPException(status_code=400, detail=error_detail)
    else:
        log.info('Super Admin already exist')
