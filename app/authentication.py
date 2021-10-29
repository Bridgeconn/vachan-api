"""Authentication related functions"""
import os
import json
from functools import wraps
import requests
from fastapi import HTTPException, Security , Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer ,\
    OAuth2PasswordBearer
from sqlalchemy.orm import Session
import db_models
import schema_auth
from dependencies import log
from custom_exceptions import GenericException ,\
    AlreadyExistsException,NotAvailableException,UnAuthorizedException,\
    UnprocessableException, PermisionException
from api_permission_map import api_permission_map


PUBLIC_BASE_URL = os.environ.get("VACHAN_KRATOS_PUBLIC_URL"+"self-service/",
                                    "http://127.0.0.1:4433/self-service/")
ADMIN_BASE_URL = os.environ.get("VACHAN_KRATOS_ADMIN_URL", "http://127.0.0.1:4434/")
USER_SESSION_URL = os.environ.get("VACHAN_KRATOS_PUBLIC_URL"+ "sessions/whoami",
                                "http://127.0.0.1:4433/sessions/whoami")
SUPER_USER = os.environ.get("VACHAN_SUPER_USERNAME")
SUPER_PASSWORD = os.environ.get("VACHAN_SUPER_PASSWORD")

access_rules = {
    "meta-content":{
        "create": ["registeredUser"],
        "edit":["SuperAdmin", "resourceCreatedUser"],
        "read-via-api":["noAuthRequired"],
        "view-on-web":["noAuthRequired"],
        "refer-for-translation": ["registeredUser"],
    },
    "content":{  # default tag for all sources in the sources table ie bibles, commentaries, videos
        "read-via-api":["SuperAdmin", "VachanAdmin", "BcsDeveloper"],
        "read-via-vachanadmin":["SuperAdmin", "VachanAdmin"],
        "create": ["SuperAdmin", "VachanAdmin"],
        "edit": ["SuperAdmin", "resourceCreatedUser"]
    },
    "open-access":{
        "read-via-api":["noAuthRequired"],
        "view-on-web":["noAuthRequired"],
        "refer-for-translation": ["SuperAdmin", "AgAdmin", "AgUser"],
        "translate":["SuperAdmin", "AgAdmin", "AgUser"]
    },
    "publishable":{
        "read-via-api":["registeredUser"],
        "view-on-web":["noAuthRequired"],
        "refer-for-translation":["SuperAdmin", "AgAdmin", "AgUser"]
    },
    "downloadable":{
        "download-n-save":["SuperAdmin", "VachanAdmin", "VachanUser"]
    },
    "derivable":{
        "translate":["SuperAdmin", "AgAdmin", "AgUser"]
    },
    "translation-project":{ #default tag for all AG projects on cloud
        "create":["SuperAdmin", "AgAdmin", "AgUser"],
        "edit-Settings":["SuperAdmin", "AgAdmin", "projectOwner"],
        "read-settings":['SuperAdmin', "AgAdmin", 'projectOwner', "projectMember"],
        "edit-draft": ["SuperAdmin", "AgAdmin","projectOwner", "projectMember"],
        "read-draft":["SuperAdmin", "AgAdmin", "projectOwner", "projectMember", "BcsDeveloper"]
    },
    "research-use":{
        "read":["SuperAdmin", "BcsDeveloper"]
    },
    "user":{ #default tag for all users in our system(Kratos)
        "create":["noAuthRequired"],
        "edit-role":["SuperAdmin"],
       "edit-data":["SuperAdmin", "createdUser"],
        "view-profile":["SuperAdmin", "createdUser"],
       "login":['noAuthRequired'],
        'logout':["createdUser"],
        "detele/deactivate":["SuperAdmin"]
    }
}

#get current user data
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

#pylint: disable=unused-argument
def project_owner(db_:Session, db_resource, user_id):
    '''checks if the user is the owner of the given project'''
    project_id = db_resource.projectId
    project_owners = db_.query(db_models.TranslationProjectUser.userId).filter(
        db_models.TranslationProjectUser.projectId == project_id,
        db_models.TranslationProjectUser.userRole == "owner").all()
    if user_id in project_owners:
        return True
    return False

def project_member(db_:Session, db_resource, user_id):
    '''checks if the user is the memeber of the given project'''
    project_id = db_resource.projectId
    project_owners = db_.query(db_models.TranslationProjectUser.userId).filter(
        db_models.TranslationProjectUser.projectId == project_id,
        db_models.TranslationProjectUser.userRole == "member").all()
    if user_id in project_owners:
        return True
    return False

def get_accesstags_basedon_resourcetype(resource_type, method, db_resource):
    """check the type of resource and provide access tags"""
    if resource_type == schema_auth.ResourceType.METACONTENT:
        access_tags = ["meta-content","open-access"]
    elif resource_type == schema_auth.ResourceType.PROJECT:
        access_tags = ['translation-project']
    elif resource_type == schema_auth.ResourceType.USER:
        access_tags = ['user']
    elif resource_type == schema_auth.ResourceType.CONTENT:
        access_tags = []
        if method != 'GET':
            for perm in db_resource.metaData['accessPermissions']:
                # access_tags.append(perm.value)
                access_tags.append(perm)
        if method == 'GET':
            for i in range(len(db_resource)):#pylint: disable=consider-using-enumerate
                permissions = db_resource[i].metaData['accessPermissions']
                for perm in permissions:
                    if not perm in access_tags:
                        access_tags.append(perm)
    else:
        raise Exception("Unknown resource type")
    return access_tags

def get_accesstags_permission(request_context, resource_type, db_, db_resource , user_details):
    """get access_tag and permission"""
    endpoint = request_context['endpoint']
    method = request_context['method']
    requesting_app = request_context['app']
    if resource_type is None:
        if endpoint.split('/')[-1] in ["contents", "languages", "licenses", 'versions']:
            resource_type = schema_auth.ResourceType.METACONTENT
        elif endpoint.startswith('/v2/autographa/project'):
            resource_type = schema_auth.ResourceType.PROJECT
        elif endpoint.startswith('/v2/user'):
            resource_type = schema_auth.ResourceType.USER
        elif endpoint.startswith("/v2/translation"):
            resource_type = None
        else:
            resource_type = schema_auth.ResourceType.CONTENT

    required_permission = api_permission_map(endpoint, request_context ,
        requesting_app, resource_type, user_details)

    access_tags = get_accesstags_basedon_resourcetype(resource_type, method, db_resource)

    return access_tags, required_permission, resource_type

def role_check_has_right(db_, role, user_details, resource_type, db_resource, *args):#pylint: disable=too-many-locals
    """check the has right for roles"""
    request_context = args[0]
    user_id = user_details['user_id']
    def created_user_check(resource_type, db_, db_resource, user_id):
        """checks for createduser role"""
        has_rights = False
        created_user = db_resource.createdUser
        # print("created_user==>",created_user)
        # print("user_-=id===>",user_id)
        if user_id is not None and created_user == user_id:
            has_rights = True
        return has_rights

    def project_owner_check(resource_type, db_, db_resource, user_id):
        """checks for project owner role"""
        has_rights = False
        if role == "projectOwner" and resource_type == schema_auth.ResourceType.PROJECT:
            if project_owner(db_, db_resource, user_id):
                has_rights =  True
        return has_rights

    def project_member_check(resource_type, db_, db_resource, user_id):
        """checks for creaproject member role"""
        has_rights = False
        if role == "projectMember" and resource_type == schema_auth.ResourceType.PROJECT:
            if project_member(db_, db_resource, user_id):
                has_rights =  True
        return has_rights

    def registred_user_check(resource_type, db_, db_resource, user_id):
        """check registered user id is none or not"""
        has_rights =False
        if not user_id is None:
            has_rights = True
        return has_rights

    switcher = {
        "noAuthRequired" : True,
        "registeredUser" : registred_user_check,
        "resourceCreatedUser" : created_user_check,
        "projectOwner" : project_owner_check ,
        "projectMember" : project_member_check ,
    }
    has_rights =  switcher.get(role, False)

    if not isinstance(has_rights,bool):
        has_rights = has_rights(resource_type, db_, db_resource, user_id)

    if user_details['user_roles'] and role in user_details['user_roles']:
        #check for created user for content api post
        if not role == 'SuperAdmin' and  request_context['method'] == 'POST':
            endpoint = request_context['endpoint']
            source_contents_list = ['bibles','commentaries',
                'dictionaries','infographics','biblevideos']
            endpoint_split_list = endpoint.split('/')
            if endpoint_split_list[2] in source_contents_list:
                has_rights = created_user_check(resource_type, db_, db_resource, user_id)
            else:
                has_rights = True
        else:
            has_rights = True

    return has_rights

###############################################################################################
def filter_resource_content_get(db_resource, access_tags, required_permission, user_details):
    """filter the content for get request for resource type content"""
    has_rights = False
    filtered_content = []

    # if not recieve_token is None:
    #     user_details = get_current_user_data(recieve_token)
    #     if not 'error' in  user_details.keys():
    #         user_id = user_details['user_id'] #pylint: disable=W0612  #use in future
    #         user_roles = user_details['user_roles']
    #         if 'APIUser' in user_roles:
    #             user_roles.remove('APIUser')#pylint: disable=no-member #unwanted error
    #             user_roles.append('registeredUser')#pylint: disable=no-member
    if not 'error' in  user_details.keys():
        user_id = user_details['user_id'] #pylint: disable=W0612  #use in future
        user_roles = user_details['user_roles']
        if 'APIUser' in user_roles:
            user_roles.remove('APIUser')#pylint: disable=no-member #unwanted error
            user_roles.append('registeredUser')#pylint: disable=no-member
        if not user_id is None and not 'registeredUser' in user_roles:
            user_roles.append('registeredUser')
    else:
        user_id = None ##pylint: disable=W0612
        user_roles = []

    for source in db_resource:#pylint: disable=too-many-nested-blocks
        for tag in source.metaData['accessPermissions']:
            if required_permission in access_rules[tag].keys():
                allowed_users = access_rules[tag][required_permission]
                # print("ALLOWED USERS PERMISIONS=====>",tag,":=>",allowed_users)
                role = "noAuthRequired"
                if role in allowed_users:
                    filtered_content.append(source)
                else:
                    for role in user_roles:
                        if role in allowed_users and \
                                not any(source == dic for dic in filtered_content):
                            filtered_content.append(source)
    if len(filtered_content) > 0:
        has_rights = True
    return has_rights, filtered_content
##############################################################################################

def check_access_rights(db_:Session, required_params, db_resource=None):
    """check access right"""
    request_context = required_params.get('request_context',None)
    # user_id = required_params.get('user_',None)
    # user_roles = required_params.get('user_roles',None)
    user_details = required_params.get('user_details',None)
    resource_type = required_params.get('resource_type',None)
    allowed_users = []
    access_tags,required_permission, resource_type = \
        get_accesstags_permission(request_context, resource_type, db_ , db_resource ,user_details)
    # print("Access Tag==>>>",access_tags)
    # print("permission==>>>",required_permission)
    has_rights = False
    filtered_content = []
    # test function seperate permision check and filter for get of contents
    if resource_type == schema_auth.ResourceType.CONTENT and \
            request_context["method"] == 'GET':
        has_rights , filtered_content  = \
            filter_resource_content_get(db_resource,access_tags,required_permission, user_details)
    else:
        filtered_content = None
        for tag in access_tags:
            if required_permission in access_rules[tag].keys():
                allowed_users = access_rules[tag][required_permission]
            # print("Allowed User ==>>>>",allowed_users)
            if len(allowed_users) > 0:
                for role in allowed_users:
                    has_rights = role_check_has_right(db_, role, user_details, resource_type,
                        db_resource,request_context)
                    # has_rights = role_check_has_right(db_, role, user_roles, resource_type,
                    #     db_resource, user_id)
                    if has_rights:
                        break
                if has_rights:
                    break
    return has_rights , filtered_content

#####decorator function for auth and access rules ######
def verify_auth_decorator_params(kwargs):
    """check passed params to auth from router"""
    required_params = {
            "request_context":"",
            "db_":"",
            "user_details":"",
            # "user_id":"",
            # "user_roles":"",
            "resource_type":""
        }
    for param in required_params:
        if param in kwargs.keys():
            required_params[param] = kwargs[param]
        else:
            required_params[param] = None

    # if 'user_details' in kwargs.keys() and isinstance(kwargs['user_details'],dict):
    #     required_params['user_id'] = kwargs['user_details']["user_id"]
    #     required_params['user_roles'] = kwargs['user_details']['user_roles']
    if 'request' in kwargs.keys():
        request_context = {}
        request = kwargs['request']
        request_context['method'] = request.method
        request_context['endpoint'] = request.url.path
        request_context['path_params'] = request.path_params
        if 'app' in request.headers:
            request_context['app'] = request.headers['app']
        else:
            request_context['app'] = None
        required_params['request_context'] = request_context
    return required_params

#decorator for authentication and access check
def get_auth_access_check_decorator(func):
    """Decorator function for auth and access check for all routers"""
    @wraps(func)
    async def wrapper(*args, **kwargs):#pylint: disable=too-many-branches
        db_resource =None
        verified = False
        required_params = verify_auth_decorator_params(kwargs)
        db_ = required_params["db_"]

        if required_params['request_context']['endpoint'].startswith("/v2/user"):#pylint: disable=E1126
            verified , filtered_content = \
                check_access_rights(db_, required_params, db_resource)
            if not verified:
                raise PermisionException("Access Permission Denied for the URL")
            #calling router functions
            response = await func(*args, **kwargs)
        else:
            #calling router functions
            response = await func(*args, **kwargs)
            if len(response) > 0:
                #pylint: disable=E1126
                if required_params['request_context']['method'] != 'GET':
                    if isinstance(response['data'],dict) and \
                        'source_content' in response['data'].keys():
                        response['data']['source_content'].updatedUser = \
                            required_params['user_details']["user_id"]
                        db_resource = response['data']['source_content']
                        db_content = response['data']['db_content']
                        message = response['message']
                        response = {}
                        response['message'] = message
                        response['data'] = db_content

                    else:
                        db_resource = response['data']
                        if required_params['request_context']["method"] == 'POST':
                            response['data'].createdUser = \
                                required_params['user_details']["user_id"]
                        if required_params['request_context']["method"] == 'PUT' :
                            response['data'].updatedUser = \
                                required_params['user_details']["user_id"]

                    verified , filtered_content = \
                        check_access_rights(db_, required_params, db_resource)
                    if not verified:
                        raise PermisionException("Access Permission Denied for the URL")
                    db_.commit()#pylint: disable=E1101
                    db_.refresh(db_resource)#pylint: disable=E1101

                elif required_params['request_context']['method'] == 'GET':
                    if isinstance(response,dict) and \
                        'source_content' in response.keys():
                        db_resource = []
                        db_resource.append(response['source_content'])
                        verified , filtered_content  = \
                            check_access_rights(db_, required_params, db_resource)
                        # print("filtered content get===========>",filtered_content[0].sourceName)
                        # print("filtered content get===========>",verified)
                        if verified and db_resource[0].sourceName == filtered_content[0].sourceName:
                            response = response['db_content']
                    else:
                        db_resource = response
                        verified , filtered_content  = \
                            check_access_rights(db_, required_params, db_resource)
                        if not filtered_content is None:
                            response = filtered_content
                    if not verified:
                        raise PermisionException("Access Permission Denied for the URL")
        # print("response===>",response['data'].__dict__)
        return response
    return wrapper

######################################### Auth Functions ####################

#Class handles the session validation and logout
class AuthHandler():
    """Authentication class"""
    security = HTTPBearer()
    #pylint: disable=R0201
    def kratos_session_validation(self,auth:HTTPAuthorizationCredentials = Security(security)):
        """kratos session validity check"""
        recieve_token = auth.credentials
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
            raise UnAuthorizedException(detail=data["error"])

        elif user_data.status_code == 500:
            raise GenericException(data["error"])

        return user_details

    def kratos_logout(self,auth:HTTPAuthorizationCredentials= Security(security)):
        """logout function"""
        recieve_token = auth.credentials
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

#get all user details
def get_all_kratos_users():
    """get all user info"""
    base_url = ADMIN_BASE_URL+"identities/"

    response = requests.get(base_url)
    if response.status_code == 200:
        user_data = json.loads(response.content)
    else:
        raise UnAuthorizedException(detail=json.loads(response.content))
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
            "Permisions": reg_response["identity"]["traits"]["userrole"]
        },
        "token":reg_response["session_token"]
    }

    user_permision = data["registered_details"]['Permisions']
    switcher = {
        schema_auth.AdminRoles.AGUSER.value : schema_auth.App.AG.value,
        schema_auth.AdminRoles.VACHANUSER.value : schema_auth.App.VACHAN.value,
        schema_auth.AdminRoles.VACHANADMIN.value : schema_auth.App.VACHANADMIN.value
            }
    user_role =  switcher.get(user_permision[0], schema_auth.App.API.value)
    data["registered_details"]['Permisions'] = [user_role]
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
                        "message":"User Already Registered, New Permision updated",
                        "registered_details":{
                            "id":current_user_id,
                            "email":email,
                            "Permisions": return_data["role_list"]
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
            kratos_users = get_all_kratos_users()

            #update user role for exisiting user
            data = register_exist_update_user_role(kratos_users, email,
                user_role, reg_req, reg_response)
            user_permision = data["registered_details"]['Permisions']
            conv_permission = []
            for perm in user_permision:
                switcher = {
                    schema_auth.AdminRoles.AGUSER.value : schema_auth.App.AG.value,
                    schema_auth.AdminRoles.VACHANUSER.value : schema_auth.App.VACHAN.value,
                    schema_auth.AdminRoles.VACHANADMIN.value : schema_auth.App.VACHANADMIN.value
                    }
                role =  switcher.get(perm, schema_auth.App.API.value)
                conv_permission.append(role)
                data["registered_details"]['Permisions'] = conv_permission
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

        cred_data = {"password_identifier": user_email, "password": password.get_secret_value()
                    , "method": "password"}
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
            if SUPER_USER ==  identity["traits"]["email"]:
                found = True
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
                        "traits.userrole":"SuperAdmin",
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
