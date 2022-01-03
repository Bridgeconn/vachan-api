"""Authentication related functions related to Kratos API accesses and our access control logics"""
import os
import json
import csv
from functools import wraps
import requests
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import db_models
# from auth.api_permission_map import api_permission_map
from schema import schema_auth
from dependencies import log
from custom_exceptions import GenericException ,\
    AlreadyExistsException,NotAvailableException,UnAuthorizedException,\
    UnprocessableException, PermissionException

PUBLIC_BASE_URL = os.environ.get("VACHAN_KRATOS_PUBLIC_URL",
                                    "http://127.0.0.1:4433/")+"self-service/"
ADMIN_BASE_URL = os.environ.get("VACHAN_KRATOS_ADMIN_URL", "http://127.0.0.1:4434/")
USER_SESSION_URL = os.environ.get("VACHAN_KRATOS_PUBLIC_URL",
                                "http://127.0.0.1:4433/")+ "sessions/whoami"
SUPER_USER = os.environ.get("VACHAN_SUPER_USERNAME")
SUPER_PASSWORD = os.environ.get("VACHAN_SUPER_PASSWORD")

def get_current_user_data(recieve_token):
    """get current user details"""
    user_details = {"user_id":"", "user_roles":""}
    headers = {}
    headers["Accept"] = "application/json"
    headers["Authorization"] = f"Bearer {recieve_token}"
    user_data = requests.get(USER_SESSION_URL, headers=headers)
    data = json.loads(user_data.content)
    if user_data.status_code == 200:
        user_details["user_id"] = data["identity"]["id"]
        if "userrole" in data["identity"]["traits"]:
            user_details["user_roles"] = data["identity"]["traits"]["userrole"]
    elif user_data.status_code == 401:
        # raise UnAuthorizedException(detail=data["error"])
        user_details["user_id"] =None
        user_details["user_roles"] = ['noAuthRequired']
        user_details["error"] = UnAuthorizedException(detail=data["error"])
    elif user_data.status_code == 500:
        # raise GenericException(data["error"])
        user_details["user_id"] =None
        user_details["user_roles"] = ['noAuthRequired']
        user_details["error"] = GenericException(detail=data["error"])
    return user_details

#optional authentication with token or none
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth", auto_error=False)
async def get_user_or_none(token: str = Depends(optional_oauth2_scheme)):
    """optional auth for getting token of logined user not raise error if no auth"""
    # print("token===>",token)
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


####################### Access control logics ######################################
with open('auth/access_rules.json','r') as file:
    ACCESS_RULES = json.load(file)
    log.warning("Startup event to read Access Rules")
    log.debug(ACCESS_RULES)

APIPERMISSIONTABLE = []
with open('auth/api-permissions.csv','r') as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    for row in csvreader:
        APIPERMISSIONTABLE.append(row)
    log.warning("Startup event to load permission table")
    log.debug(APIPERMISSIONTABLE)

def api_resourcetype_map(endpoint, path_params={}):
    if endpoint.split('/')[2] in ["contents", "languages", "licenses", 'versions']:
        resource_type = schema_auth.ResourceType.METACONTENT
    elif endpoint.startswith('/v2/autographa/project'):
        resource_type = schema_auth.ResourceType.PROJECT
    elif endpoint.startswith('/v2/user'):
        resource_type = schema_auth.ResourceType.USER
    elif endpoint.startswith("/v2/translation"):
        resource_type = schema_auth.ResourceType.TRANSLATION
    elif endpoint.startswith("/v2/lookup"):
        resource_type = schema_auth.ResourceType.LOOKUP
    elif endpoint.startswith("/v2/sources") or "sourceName" in path_params:
        resource_type = schema_auth.ResourceType.CONTENT
    else:
        raise GenericException("Resource Type of API not defined")
    return resource_type


def search_api_permission_map(endpoint, method, client_app, path_params={}):
    res_perm_list = []
    req_url = endpoint
    for key in path_params:
        req_url = req_url.replace(path_params[key], "*")
    for row in APIPERMISSIONTABLE:
        table_url = row[0]
        for key in path_params:
            table_url = req_url.replace(key, "*")
        if table_url == req_url:
            # print("url matched")
            if row[1] == method:
                # print("method matched")
                # print(row[2])
                # print(client_app.value)
                if row[2] == "None" or row[2] == client_app.value:
                    # print("app matched")
                    res = row[4]
                    if res == 'None':
                        res = api_resourcetype_map(req_url, path_params)
                    res_perm_list.append((res, row[5]))
    if len(res_perm_list) == 0:
        log.error("No permisions map found for:(%s, %s, %s)"%(endpoint, method, client_app))
        raise GenericException("API-Permission map not defined for the request!")
    # print(res_perm_list)
    return res_perm_list

def get_access_tag(db_, resource_type, path_params={}, resource=None):
    resource_tag_map = {
        schema_auth.ResourceType.USER: ['user'],
        schema_auth.ResourceType.PROJECT: ['translation-project'],
        schema_auth.ResourceType.TRANSLATION: ['generic-translation'],
        schema_auth.ResourceType.LOOKUP: ['lookup-content'],
        schema_auth.ResourceType.METACONTENT: ["meta-content","open-access"],
        # schema_auth.ResourceType.CONTENT: None
    }
    if resource_type in resource_tag_map:
        return resource_tag_map[resource_type]
    if "source_name" in path_params:
        db_entry = db_.query(db_models.Source.metaData['accessPermissions']).filter(
            db_models.Source.sourceName == source_name).first()
        return db_entry[0]
    if resource:
        return resource.metaData['accessPermissions']
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
        # print(user_details, required_rights)
        if "noAuthRequired" in required_rights:
            return True
        if "registeredUser" in required_rights and user_details["user_id"] is not None:
            return True
        # print("user_details:", user_details)
        for role in user_details['user_roles']:
            if role in required_rights:
                return True
        if resp_obj is not None and db_ is not None:
            # print("resp_obj:", resp_obj.__dict__)
            if "resourceCreatedUser" in required_rights and \
                user_details['user_id'] == resp_obj.createdUser:
                # print("matched created user")
                return True
            if "projectOwner" in required_rights and \
                is_project_owner(db_, resp_obj, user_details['user_id']):
                return True
            if "projectMember" in required_rights and \
                is_project_member(db_, resp_obj, user_details['user_id']):
                return True
        return False


def get_auth_access_check_decorator(func):#pylint:disable=too-many-statements
    """Decorator function for auth and access check for all routers"""
    @wraps(func)
    async def wrapper(*args, **kwargs):#pylint: disable=too-many-branches,too-many-statements
        request = kwargs.get('request')
        db_ = kwargs.get("db_")
        endpoint = request.url.path
        method = request.method
        path_params = request.path_params
        user_details = kwargs.get('user_details')
        if 'app' in request.headers:
            client_app = request.headers['app']
        else:
            client_app = schema_auth.App.API
        required_permissions = search_api_permission_map(
            endpoint, method, client_app, path_params)

        required_rights = []
        for resourceType, permission in required_permissions:
            access_tags = get_access_tag(db_, resourceType, path_params)
            for tag in access_tags:
                if tag in ACCESS_RULES and permission in ACCESS_RULES[tag]:
                    required_rights += ACCESS_RULES[tag][permission]

        print("required_rights:", required_rights)
        Authenticated = check_right(user_details, required_rights)    
        print("Authenticated:", Authenticated)

        if (schema_auth.ResourceType.USER in [tup[0] for tup in required_permissions] 
            and not Authenticated):
                if user_details['user_id'] is None:
                    raise UnAuthorizedException("Access token not provided or user not recognized")
                raise PermissionException("Access Permission Denied for the URL")

        ###### Executing the API function #######
        response = await func(*args, **kwargs)
        #########################################

        # All no-auth and role based cases checked and appoved if applicable
        if Authenticated:
            db_.commit()
        # Resource(item) specific checks
        elif isinstance(response, dict) and "data" in response:
            if check_right(user_details, required_rights, response['data'], db_):
                db_.commit()
            else:
                if user_details['user_id'] is None:
                    raise UnAuthorizedException("Access token not provided or user not recognized.")
                raise PermissionException("Access Permission Denied for the URL")
        elif isinstance(response, list):
            filtered_response = []
            for item in response:
                if check_right(user_details, required_rights, item, db_):
                    filtered_response.append(item)
            response = filtered_response
        print("returning response:", response)
        return response
    return wrapper


######################################### Kratos Auth Functions ####################


#kratos Logout
def kratos_logout(recieve_token):
    """logout function"""
    # recieve_token = auth.credentials
    payload = {"session_token": recieve_token}
    headers = {}
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    logout_url = PUBLIC_BASE_URL + "logout/api"
    response = requests.delete(logout_url, headers=headers, json=payload)
    if response.status_code == 204:
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

#get all or single user details
def get_all_or_one_kratos_users(rec_user_id=None):
    """get all user info or a particular user details"""
    base_url = ADMIN_BASE_URL+"identities/"

    if rec_user_id is None:
        response = requests.get(base_url)
        if response.status_code == 200:
            user_data = json.loads(response.content)
        else:
            raise UnAuthorizedException(detail=json.loads(response.content))
    else:
        response = requests.get(base_url+rec_user_id)
        if response.status_code == 200:
            user_data = json.loads(response.content)
        else:
            raise NotAvailableException("User does not exist")
    return user_data

#User registration with credentials
def register_check_success(reg_response):
    """register reqirement success"""
    name_path = reg_response["identity"]["traits"]["name"]
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
    switcher = {
        schema_auth.AdminRoles.AGUSER.value : schema_auth.App.AG.value,
        schema_auth.AdminRoles.VACHANUSER.value : schema_auth.App.VACHAN.value,
        schema_auth.AdminRoles.VACHANADMIN.value : schema_auth.App.VACHANADMIN.value
            }
    user_role =  switcher.get(user_permision[0], schema_auth.App.API.value)
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
                switcher = {
                    schema_auth.AdminRoles.AGUSER.value : schema_auth.App.AG.value,
                    schema_auth.AdminRoles.VACHANUSER.value : schema_auth.App.VACHAN.value,
                    schema_auth.AdminRoles.VACHANADMIN.value : schema_auth.App.VACHANADMIN.value
                    }
                role =  switcher.get(perm, schema_auth.App.API.value)
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

def user_register_kratos(register_details,app_type):
    """user registration kratos"""
    data = {}
    email = register_details.email
    password = register_details.password

    switcher = {
        schema_auth.App.AG : schema_auth.AdminRoles.AGUSER.value,
        schema_auth.App.VACHAN: schema_auth.AdminRoles.VACHANUSER.value,
        schema_auth.App.VACHANADMIN: schema_auth.AdminRoles.VACHANADMIN.value
            }
    user_role =  switcher.get(app_type, schema_auth.AdminRoles.APIUSER.value)

    register_url = PUBLIC_BASE_URL+"registration/api"
    reg_flow = requests.get(register_url)
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
        reg_req = requests.post(reg_flow_id,headers=headers,json=reg_data)
        reg_response = json.loads(reg_req.content)
        if reg_req.status_code == 200:
            data = register_check_success(reg_response)

        elif reg_req.status_code == 400:
            data = register_flow_fail(reg_response,email,user_role,reg_req)
    return data


def user_login_kratos(user_email,password):#pylint: disable=R1710
    "kratos login"
    data = {"details":"","token":""}
    login_url = PUBLIC_BASE_URL+"login/api/"
    flow_res = requests.get(login_url)
    if flow_res.status_code == 200:
        flow_res = json.loads(flow_res.content)
        flow_id = flow_res["ui"]["action"]
        password = password.get_secret_value() if not isinstance(password, str) else password
        cred_data = {"password_identifier": user_email,
            "password": password, "method": "password"}
        login_req = requests.post(flow_id, json=cred_data)
        login_req_content = json.loads(login_req.content)
        if login_req.status_code == 200:
            session_id = login_req_content["session_token"]
            data["message"] = "Login Succesfull"
            data["token"] = session_id
        else:
            raise UnAuthorizedException(login_req_content["ui"]["messages"][0]["text"])
    return data

#delete an identity
def delete_identity(user_id):
    """delete identity"""
    base_url = ADMIN_BASE_URL+"identities/"+user_id
    response = requests.delete(base_url)
    if response.status_code == 404:
        raise NotAvailableException("Unable to locate the resource")
    log.warning(response)
    log.warning(response.content)
    return response

#user role add
def user_role_add(user_id,roles_list):
    """user role add from admin"""
    base_url = ADMIN_BASE_URL+"identities/"
    url = base_url + str(user_id)

    response = requests.get(url)
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
        raise AlreadyExistsException("Already Exist permisions %s"%exist_roles)

    headers = {}
    headers["Content-Type"] = "application/json"
    response = requests.put(url,headers=headers,json=data)

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
    response = requests.get(super_user_url)
    if response.status_code == 200:
        identity_data = json.loads(response.content)
        for identity in identity_data:
            if schema_auth.AdminRoles.SUPERADMIN.value in identity["traits"]["userrole"]:
                found = True
                break
    else:
        raise HTTPException(status_code=401, detail=json.loads(response.content))

    if not found:
        register_url = PUBLIC_BASE_URL+"registration/api"
        reg_flow = requests.get(register_url)
        if reg_flow.status_code == 200:
            flow_res = json.loads(reg_flow.content)
            reg_flow_id = flow_res["ui"]["action"]
            reg_data = {"traits.email": SUPER_USER,
                        "traits.name.first": "Super",
                        "traits.name.last": "Admin",
                        "password": SUPER_PASSWORD,
                        "traits.userrole":schema_auth.AdminRoles.SUPERADMIN.value,
                        "method": "password"}
            headers = {}
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            reg_req = requests.post(reg_flow_id,headers=headers,json=reg_data)
            if reg_req.status_code == 200:
                log.info('Super Admin created')
            elif reg_req.status_code == 400:
                log.error(reg_req.content)
                raise HTTPException(status_code=400, detail="Error on creating Super Admin")
    else:
        log.info('Super Admin already exist')

