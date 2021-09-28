"""Authentication related functions"""
import os
import json
import requests
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dependencies import log
from custom_exceptions import GenericException , PermisionException ,\
    AlreadyExistsException,NotAvailableException,UnAuthorizedException,\
    UnprocessableException

PUBLIC_BASE_URL = os.environ.get("VACHAN_KRATOS_PUBLIC_URL"+"self-service/",
                                    "http://127.0.0.1:4433/self-service/")
ADMIN_BASE_URL = os.environ.get("VACHAN_KRATOS_ADMIN_URL", "http://127.0.0.1:4434/")
USER_SESSION_URL = os.environ.get("VACHAN_KRATOS_PUBLIC_URL"+ "sessions/whoami",
                                "http://127.0.0.1:4433/sessions/whoami")
SUPER_USER = os.environ.get("VACHAN_SUPER_USERNAME")
SUPER_PASSWORD = os.environ.get("VACHAN_SUPER_PASSWORD")

access_roles = {
    "contentType" : ["SuperAdmin","VachanAdmin"],
    "licenses" : ["SuperAdmin","VachanAdmin"],
    "versions" : ["SuperAdmin","VachanAdmin"],
    "sources" : ["SuperAdmin","VachanAdmin"],
    "bibles" : ["SuperAdmin","VachanAdmin"],
    "commentaries" : ["SuperAdmin","VachanAdmin"],
    "dictionaries" : ["SuperAdmin","VachanAdmin"],
    "infographics" : ["SuperAdmin","VachanAdmin"],
    "bibleVideos" : ["SuperAdmin","VachanAdmin"],
    "userRole" :["SuperAdmin"],
    "delete_identity":["SuperAdmin"]
}

#check roles for api
def verify_role_permision(api_name,permision):
    """check the user roles for the requested api"""
    verified = False
    if api_name in access_roles:
        access_list = access_roles[api_name]
        if len(access_list) != 0 and len(permision) != 0:
            for role in permision:
                if role in access_list:
                    verified = True
        else:
            raise PermisionException("User have no permision to access API")
    else:
        raise GenericException("No permisions set for the API - %s"%api_name)
    return verified

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

    #check auto role assign
    user_role = app_type

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


def user_login_kratos(user_email,password):
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

    if "" in roles_list or len(roles_list) == 0:
        roles_list = ["None"]

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
