"""Authentication related functions"""
import os
import json
import requests
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
#pylint: disable=E0401
#pylint gives import error if not relative import is used. But app(uvicorn) doesn't accept it
import db_models
import schema_auth
from dependencies import log
from custom_exceptions import GenericException ,\
    AlreadyExistsException,NotAvailableException,UnAuthorizedException,\
    UnprocessableException
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

def metacontent_creator(db_:Session, resource_type, resource_id, user_id):
    '''checks if the user is the creator of the given item'''
    if resource_type == 'contents':
        model_cls = db_models.ContentType
    elif resource_type == "languages":
        model_cls = db_models.Language
    elif resource_type == "versions":
        model_cls = db_models.Version
    elif resource_type == "licenses":
        model_cls = db_models.License
    created_user = db_.query(model_cls.createdUser).get(resource_id)
    if user_id == created_user:
        return True
    return False

def resource_creator(db_:Session, source_id, user_id):
    '''checks if the user is the creator of the given source'''
    created_user =  db_.query(db_models.Source.createdUser).get(source_id).first()
    if user_id == created_user:
        return True
    return False

def project_owner(db_:Session, project_id, user_id):
    '''checks if the user is the owner of the given project'''
    project_owners = db_.query(db_models.TranslationProjectUser.userId).filter(
        db_models.TranslationProjectUser.projectId == project_id,
        db_models.TranslationProjectUser.userRole == "owner").all()
    if user_id in project_owners:
        return True
    return False

def project_member(db_:Session, project_id, user_id):
    '''checks if the user is the memeber of the given project'''
    project_owners = db_.query(db_models.TranslationProjectUser.userId).filter(
        db_models.TranslationProjectUser.projectId == project_id,
        db_models.TranslationProjectUser.userRole == "member").all()
    if user_id in project_owners:
        return True
    return False

# def api_permission_map(endpoint, method, requesting_app, resource):
#     '''returns the required permission name as per the access rules'''
#     permission = None
#     if requesting_app == schema_auth.App.ag and method == "GET":
#         permission = "refer-for-translation"
#     elif requesting_app == schema_auth.App.vachan and method == "GET":
#         permission = "view-on-web"
#     elif requesting_app == schema_auth.App.vachanAdmin and method == "GET":
#         permission = "view-on-vachan-admin"
#     elif requesting_app is None and method == "GET":
#         permission = "read-via-api"
#     elif (endpoint == "/v2/autographa/projects" and method == "PUT"
#         and resource==schema_auth.ResourceType.content):
#         permission = "translate"
#     elif (endpoint == "/v2/autographa/projects" and method == "PUT"
#         and resource==schema_auth.ResourceType.project):
#         permission = "edit-Settings"
#     elif endpoint in ["/v2/autographa/project/tokens",
#             "/v2/autographa/project/token-translations",
#         "/v2/autographa/project/token-sentences"]:
#         permission = "edit-draft"
#     elif method == "PUT" and resource==schema_auth.ResourceType.content:
#         permission = "edit"
#     elif method == "PUT" and resource==schema_auth.ResourceType.metaContent:
#         permission = "edit"
#     elif method == "PUT" and resource==schema_auth.ResourceType.user:
#         permission = "edit-role"
#     elif method == "POST":
#         permission = "create"
#     else:
#         raise Exception("API's required permission not defined")
#     return permission

def get_accesstags_permission(request_context, resource_type, db_, resource_id):
    """get access_tag and permission"""
    endpoint = request_context['endpoint']
    method = request_context['method']
    requesting_app = request_context['app']
    if resource_type is None:
        if endpoint.split('/')[-1] in ["contents", "languages", "licenses", 'versions']:
            resource_type = schema_auth.ResourceType.metaContent
        elif endpoint.startswith('/v2/autographa/project'):
            resource_type = schema_auth.ResourceType.project
        elif endpoint.startswith('/v2/user'):
            resource_type = schema_auth.ResourceType.user
        elif endpoint.startswith("/v2/translation"):
            resource_type = None
        else:
            resource_type = schema_auth.ResourceType.content
    required_permission = api_permission_map(endpoint, method,requesting_app, resource_type)

    if resource_type == schema_auth.ResourceType.metaContent:
        access_tags = ["open-access"]
    elif resource_type == schema_auth.ResourceType.project:
        access_tags = ['translation-project']
    elif resource_type == schema_auth.ResourceType.user:
        access_tags = ['user']
    elif resource_type == schema_auth.ResourceType.content:
        source_content = db_.query(db_models.Source.Metadata).get(resource_id)
        access_tags = source_content['access-tags']
    else:
        raise Exception("Unknown resource type")

    return access_tags,required_permission

def role_check_has_right(db_, role, user_roles, resource_type, resource_id, *args):
    """check the has right for roles"""
    user_id = args[0]
    endpoint = args[1]
    def created_user_check(resource_type, db_, resource_id, user_id, endpoint):
        """checks for createduser role"""
        if resource_type == schema_auth.ResourceType.content:
            if resource_creator(db_, resource_id, user_id):
                has_rights = True
        if resource_type == schema_auth.ResourceType.metaContent:
            rsc_type = endpoint.split('/')[-1]
            if metacontent_creator(db_, rsc_type, resource_id, user_id):
                has_rights =  True
        return has_rights

    def project_owner_check(resource_type,db_, resource_id, user_id):
        """checks for project owner role"""
        has_rights = False
        if role == "projectOwner" and resource_type == schema_auth.ResourceType.project:
            if project_owner(db_, resource_id, user_id):
                has_rights =  True
        return has_rights

    def project_member_check(db_, resource_id, user_id, resource_type):
        """checks for creaproject member role"""
        has_rights = False
        if role == "projectMember" and resource_type == schema_auth.ResourceType.project:
            if project_member(db_, resource_id, user_id):
                has_rights =  True
        return has_rights

    switcher = {
        "noAuthRequired" : True,
        "registeredUser" : True,
        "createdUser" : created_user_check,
        "projectOwner" : project_owner_check ,
        "projectMember" : project_member_check ,
    }
    has_rights =  switcher.get(role, False)

    if not isinstance(has_rights,bool):
        has_rights = has_rights(resource_type, db_, resource_id, user_id, endpoint)

    if user_roles and role in user_roles:
        has_rights = True

    return has_rights


def check_access_rights(db_:Session, resource_id, *args, user_id=None, user_roles=None,
    resource_type: schema_auth.ResourceType=None):
    """check access right"""
    request_context = args[0]
    endpoint = request_context['endpoint']

    access_tags,required_permission = \
        get_accesstags_permission(request_context,resource_type,db_,resource_id)

    has_rights = False
    for tag in access_tags:
        allowed_users = access_rules[tag][required_permission]
        for role in allowed_users:
            # if role == "noAuthRequired":
            #     has_rights = True
            #     break
            # if role == "registeredUser" and user_id is not None:
            #     has_rights = True
            #     break
            # if user_roles and role in user_roles:
            #     has_rights = True
            #     break
            # if role == "createdUser":
            #     if resource_type == schema_auth.ResourceType.content:
            #         if resource_creator(db_, resource_id, user_id):
            #             has_rights = True
            #             break
            #     if resource_type == schema_auth.ResourceType.metaContent:
            #         rsc_type = endpoint.split('/')[-1]
            #         if metacontent_creator(db_, rsc_type, resource_id, user_id):
            #             has_rights = True
            #             break
            # if role == "projectOwner" and resource_type == schema_auth.ResourceType.project:
            #     if project_owner(db_, resource_id, user_id):
            #         has_rights = True
            #         break
            # if role == "projectMember" and resource_type == schema_auth.ResourceType.project:
            #     if project_member(db_, resource_id, user_id):
            #         has_rights = True
            #         break
            has_rights = role_check_has_right(db_, role, user_roles, resource_type,
                 resource_id, user_id, endpoint)
            if has_rights:
                break
        if has_rights:
            break
    return has_rights


# #check roles for api
# def verify_role_permision(api_name,permision):
#     """check the user roles for the requested api"""
#     verified = False
#     if api_name in access_rules:#changed acces_role to access rule
#         access_list = access_rules[api_name]
#         if len(access_list) != 0 and len(permision) != 0:
#             for role in permision:
#                 if role in access_list:
#                     verified = True
#         else:
#             raise PermisionException("User have no permision to access API")
#     else:
#         raise GenericException("No permisions set for the API - %s"%api_name)
#     return verified

#Class handles the session validation and logout
class AuthHandler():
    """Authentication class"""
    security = HTTPBearer()
    #pylint: disable=R0201
    def kratos_session_validation(self,auth:HTTPAuthorizationCredentials = Security(security)):
        """kratos session validity check"""
        recieve_token = auth.credentials
        headers = {}
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {recieve_token}"

        user_data = requests.get(USER_SESSION_URL, headers=headers)
        data = json.loads(user_data.content)
        roles = []
        if user_data.status_code == 200:
            if "userrole" in data["identity"]["traits"]:
                roles = data["identity"]["traits"]["userrole"]

        elif user_data.status_code == 401:
            raise UnAuthorizedException(detail=data["error"])

        elif user_data.status_code == 500:
            raise GenericException(data["error"])

        return roles

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
def user_register_kratos(register_details,app_type):#pylint: disable=too-many-locals,R1710,too-many-branches
    """user registration kratos"""
    email = register_details.email
    password = register_details.password
    firstname = register_details.firstname
    lastname = register_details.lastname

    #check auto role assign
    if app_type is None:
        user_role = schema_auth.App.api
    else:
        user_role = app_type

    register_url = PUBLIC_BASE_URL+"registration/api"
    reg_flow = requests.get(register_url)
    #pylint: disable=R1702
    if reg_flow.status_code == 200:
        flow_res = json.loads(reg_flow.content)
        reg_flow_id = flow_res["ui"]["action"]
        reg_data = {"traits.email": email,
                     "traits.name.first": firstname,
                     "traits.name.last": lastname,
                     "password": password.get_secret_value(),
                     "traits.userrole":user_role,
                     "method": "password"}
        headers = {}
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        reg_req = requests.post(reg_flow_id,headers=headers,json=reg_data)
        reg_response = json.loads(reg_req.content)
        #pylint: disable=R1705
        if reg_req.status_code == 200:
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
            return data
        elif reg_req.status_code == 400:
            if "messages" in reg_response["ui"]:
                err_msg = \
        "An account with the same identifier (email, phone, username, ...) exists already."
                err_txt = reg_response["ui"]["messages"][0]["text"]
                if err_txt == err_msg:
                    kratos_users = get_all_kratos_users()
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
                                    return data
                            else:
                                raise HTTPException(status_code=reg_req.status_code, \
                                    detail=reg_response["ui"]["messages"][0]["text"])
                else:
                    raise HTTPException(status_code=reg_req.status_code,\
                         detail=reg_response["ui"]["messages"][0]["text"])
            else:
                error_base = reg_response['ui']['nodes']
                for i in range(1,3):
                    if error_base[i]['messages'] != []:
                        raise UnprocessableException(error_base[i]['messages'][0]['text'])

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
    #pylint: disable=R1720
    if len(exist_roles) > 0:
        raise AlreadyExistsException("Already Exist permisions %s"%exist_roles)
    else:
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
