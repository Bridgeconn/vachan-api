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
from auth import utils
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
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
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
    for table_row in csvreader:
        APIPERMISSIONTABLE.append(table_row)
    log.warning("Startup event to load permission table")
    log.debug(APIPERMISSIONTABLE)

def api_resourcetype_map(endpoint, path_params=None):
    '''Default correlation between API endpoints and resource they act upon'''
    if endpoint.split('/')[2] in ["contents", "languages", "licenses", 'versions']:
        resource_type = schema_auth.ResourceType.METACONTENT.value
    elif endpoint.startswith('/v2/autographa/project'):
        resource_type = schema_auth.ResourceType.PROJECT.value
    elif endpoint.startswith('/v2/user'):
        resource_type = schema_auth.ResourceType.USER.value
    elif endpoint.startswith("/v2/translation") or endpoint.startswith("/v2/nlp"):
        resource_type = schema_auth.ResourceType.TRANSLATION.value
    elif endpoint.startswith("/v2/lookup"):
        resource_type = schema_auth.ResourceType.LOOKUP.value
    elif endpoint.startswith("/v2/jobs"):
        resource_type = schema_auth.ResourceType.JOBS.value
    elif endpoint.startswith("/v2/media"):
        resource_type = schema_auth.ResourceType.MEDIA.value
    elif endpoint.startswith("/v2/sources") or (
        path_params is not None and "source_name" in path_params):
        resource_type = schema_auth.ResourceType.CONTENT.value
    else:
        raise GenericException("Resource Type of API not defined")
    return resource_type


def search_api_permission_map(endpoint, method, client_app, path_params=None, resource=None):
    '''look up request params in the api-permission table loaded from CSV'''
    req_url = endpoint
    for key in path_params:
        req_url = req_url.replace(path_params[key], "*")
    if resource is None:
        resource = api_resourcetype_map(endpoint, path_params)
    for row in APIPERMISSIONTABLE:
        table_url = row[0]
        for key in path_params:
            table_url = table_url.replace("{"+key+"}", "*")
        if table_url == req_url:
            if row[1] == method:
                if row[2] == "None" or row[2] == client_app:
                    # print("url, method and app matched")
                    if row[4] == 'None' or row[4] == resource:
                        return (resource, row[5])
    log.error("No permisions map found for:%s, %s, %s, %s", endpoint, method, client_app, resource)
    raise PermissionException("API-Permission map not defined for the request!")

def get_access_tag(db_, resource_type, path_params=None, resource=None):
    '''obtain access tag based on resource-url direct link or value stored in DB'''
    resource_tag_map = {
        schema_auth.ResourceType.USER: ['user'],
        schema_auth.ResourceType.PROJECT: ['translation-project'],
        schema_auth.ResourceType.TRANSLATION: ['generic-translation'],
        schema_auth.ResourceType.LOOKUP: ['lookup-content'],
        schema_auth.ResourceType.METACONTENT: ["meta-content","open-access"],
        schema_auth.ResourceType.RESEARCH: ['content', 'research-use'],
        schema_auth.ResourceType.JOBS: ['jobs'],
        schema_auth.ResourceType.MEDIA: ['media']
        # schema_auth.ResourceType.CONTENT: None # excluded to use item specific tags in db
    }
    if resource_type in resource_tag_map:
        return resource_tag_map[resource_type]
    if path_params is not None and "source_name" in path_params:
        db_entry = db_.query(db_models.Source.metaData['accessPermissions']).filter(
            db_models.Source.sourceName == path_params['source_name']).first()
        if db_entry is not None:
            return db_entry[0]
    if resource:
        return resource.metaData['accessPermissions']
    if resource_type == schema_auth.ResourceType.CONTENT:
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
    log.debug("In check_right with user_details: %s, required_rights:%s, resp_obj:%s",
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
        request = kwargs.get('request')
        db_ = kwargs.get("db_")
        endpoint = request.url.path
        method = request.method
        path_params = request.path_params
        user_details = kwargs.get('user_details')
        resource_type = kwargs.get("operates_on", None)
        filtering_required = kwargs.get("filtering_required", False)
        if 'app' in request.headers:
            client_app = request.headers['app']
        else:
            client_app = schema_auth.App.API.value

        if not "authorization" in request.headers and \
            "access_token" in kwargs:
            user_details = get_current_user_data(kwargs.get("access_token"))

        resource_type, permission = search_api_permission_map(
            endpoint, method, client_app, path_params, resource=resource_type)
        required_rights = []
        access_tags = get_access_tag(db_, resource_type, path_params)
        for tag in access_tags:
            if tag in ACCESS_RULES and permission in ACCESS_RULES[tag]:
                required_rights += ACCESS_RULES[tag][permission]
        authenticated = check_right(user_details, required_rights)
        if (resource_type == schema_auth.ResourceType.USER and not authenticated):
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
        log.debug("authenticated:%s", authenticated)
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
                access_tags = get_access_tag(db_, resource_type, path_params, item)
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

#pylint: disable=R1703
def get_users_kratos_filter(base_url,name,roles,limit,skip):#pylint: disable=too-many-locals
    """v2/users filter block"""
    response = requests.get(base_url)
    if response.status_code == 200:
        user_data = []
        for data in json.loads(response.content):
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

            if not schema_auth.FilterRoles.ALL in roles:
                temp_role = []
                switcher = {
                    schema_auth.FilterRoles.AG.value : schema_auth.FilterRoles.AG,
                    schema_auth.FilterRoles.VACHAN.value : schema_auth.FilterRoles.VACHAN,
                    schema_auth.FilterRoles.API.value : schema_auth.FilterRoles.API
                        }
                for role in roles:
                    user_role =  switcher.get(role)
                    temp_role.append(user_role)
                role_list = [x.name.lower() for x in temp_role]
                kratos_role = [x.lower() for x in data["traits"]["userrole"]]
                for k_role in kratos_role:
                    res = list(filter(k_role.startswith, role_list)) != []
                    if res:
                        role_status = True
                        break
                    role_status = False
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
            response = requests.get(base_url)
            if response.status_code == 200:
                user_data = json.loads(response.content)
            else:
                raise UnAuthorizedException(detail=json.loads(response.content))
        #v2/users
        else:
            user_data = get_users_kratos_filter(base_url,name,roles,limit,skip)
    #single user
    else:
        response = requests.get(base_url+rec_user_id)
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
    response = requests.put(base_url, headers=headers, data=payload)
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
        # schema_auth.AdminRoles.VACHANADMIN.value : schema_auth.AdminRoles.VACHANADMIN.value
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
                    # schema_auth.AdminRoles.VACHANADMIN.value : schema_auth.App.VACHANADMIN.value
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
        # schema_auth.App.VACHANADMIN: schema_auth.AdminRoles.VACHANADMIN.value
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
        else:
            log.error("Unexpected response from Kratos")
            log.error(reg_req.status_code)
            log.error(reg_req.json())
            raise GenericException("Got unexpected response from Kratos")
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
            data["userId"] = login_req_content["session"]["identity"]["id"]
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
    # log.warning(response)
    # log.warning(response.content)
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
