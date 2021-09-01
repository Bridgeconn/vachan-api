from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from custom_exceptions import GenericException , PermisionException , AlreadyExistsException
import requests
import json
import os

PUBLIC_BASE_URL = os.environ.get("KRATOS_PUBLIC_BASE_URL", "http://127.0.0.1:4433/self-service/")
ADMIN_BASE_URL = os.environ.get("KRATOS_ADMIN_BASE_URL", "http://127.0.0.1:4434/")
USER_SESSION_URL = os.environ.get("KRATOS_USER_SESSION_URL", "http://127.0.0.1:4433/sessions/whoami")


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
    "userRole" :["SuperAdmin"]
}

#Roles based on app
app_based_role = {
    "ag":"aguser",
    "vachan":"vachanuser"
}

#check roles for api
def verify_role_permision(api_name,permision):
    """check the user roles for the requested api"""
    if api_name in access_roles:
        access_list = access_roles[api_name]

        if len(access_list) != 0 or len(permision) != 0:
            verified = False
            for role in permision:
                if role in access_list:
                    verified = True
            return verified    
        else:
            raise PermisionException("User have no permision to access API")

    else:
        raise GenericException("No permisions set for the API - %s",api_name)

#Class handles the session validation and logout
class AuthHandler():
    """Authentication class"""
    security = HTTPBearer()

    def kratos_session_validation(self,auth:HTTPAuthorizationCredentials = Security(security)):
        """kratos session validity check"""
        recieve_token = auth.credentials
        headers = {}
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {recieve_token}"

        user_data = requests.get(USER_SESSION_URL, headers=headers)
        data = json.loads(user_data.content)

        if user_data.status_code == 200:
            if "userrole" in data["identity"]["traits"]:
                roles = data["identity"]["traits"]["userrole"]
                return roles
            else:
                return []    

        elif user_data.status_code == 401:
            raise HTTPException(status_code=401, detail=data["error"])

        elif user_data.status_code == 500:
            raise GenericException(data["error"])

    def kratos_logout(self,auth:HTTPAuthorizationCredentials= Security(security)):
        recieve_token = auth.credentials
        payload = {"session_token": recieve_token}
        headers = {}
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        logout_url = PUBLIC_BASE_URL + "logout/api"
        response = requests.delete(logout_url, headers=headers, json=payload)
        if response.status_code == 204:
            data = {"message":"Successfully Logged out"}
            return data
        elif response.status_code == 400:
            data = json.loads(response.content)
            raise HTTPException(status_code=401, detail=data["error"])
        elif response.status_code == 500:
            data = json.loads(response.content)
            raise GenericException(data["error"])
            #raise HTTPException(status_code=500, detail=data["error"])

#get all user details
def get_all_kratos_users():
    """get all user info"""
    base_url = ADMIN_BASE_URL+"identities/"

    response = requests.get(base_url)
    if response.status_code == 200:
        user_data = json.loads(response.content)
        return user_data

    else:
        raise HTTPException(status_code=401, detail=json.loads(response.content))

#User registration with credentials
def user_register_kratos(register_details):
    """user registration kratos"""
    email = register_details.email
    password = register_details.password
    firstname = register_details.firstname
    lastname = register_details.lastname
    appname = register_details.appname

    appname = appname.lower()
    #check auto role assign
    if appname in app_based_role:
        user_role = app_based_role[appname]
    else:
        user_role = "None"

    register_url = PUBLIC_BASE_URL+"registration/api"
    reg_flow = requests.get(register_url)
    if reg_flow.status_code == 200:
        flow_res = json.loads(reg_flow.content)
        reg_flow_id = flow_res["ui"]["action"]
        reg_data = {"traits.email": email,
                     "traits.name.first": firstname,
                     "traits.name.last": lastname,
                     "password": password,
                     "traits.userrole":user_role,
                     "method": "password"}
        headers = {}
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        reg_req = requests.post(reg_flow_id,headers=headers,json=reg_data)
        reg_response = json.loads(reg_req.content)
        if reg_req.status_code == 200:
            name_path = reg_response["identity"]["traits"]["name"]
            data={
                "details":"Registration Successfull",
                "registered_detials":{
                    "id":reg_response["identity"]["id"],
                    "email":reg_response["identity"]["traits"]["email"],
                    "Name":str(name_path["first"]) + " " + str(name_path["last"]) 
                },
                "token":reg_response["session_token"]
            }
            return data
        elif reg_req.status_code == 400:
            if "messages" in reg_response["ui"]:
                err_msg = "An account with the same identifier (email, phone, username, ...) exists already."
                err_txt = reg_response["ui"]["messages"][0]["text"]
                if err_txt == err_msg:
                    kratos_users = get_all_kratos_users()
                    for user in kratos_users:
                        if email == user["traits"]["email"]:
                            current_user_id = user["id"]
                            if user_role not in user["traits"]["userrole"]:
                                role_list = user["traits"]["userrole"]
                                role_list.append(user_role)
                                return_data = user_role_add(current_user_id,role_list)
                                if return_data["Success"]:
                                    data={
                                        "details":"User Already Registered, New Permision updated",
                                        "registered_detials":{
                                            "id":current_user_id,
                                            "email":email,
                                            "Permisions": role_list
                                            }
                                    }
                                    return data
                                else:
                                    return return_data
                            else:
                                raise HTTPException(status_code=reg_req.status_code, detail=reg_response["ui"]["messages"][0]["text"])
                else:                    
                    raise HTTPException(status_code=reg_req.status_code, detail=reg_response["ui"]["messages"][0]["text"])

def user_login_kratos(auth_details):
    "kratos login"
    username = auth_details.username
    password =  auth_details.password
    data = {"details":"","token":""}

    login_url = PUBLIC_BASE_URL+"login/api/"
    flow_res = requests.get(login_url)
    if flow_res.status_code == 200:
        flow_res = json.loads(flow_res.content)
        flow_id = flow_res["ui"]["action"]

        cred_data = {"password_identifier": username, "password": password, "method": "password"}
        login_req = requests.post(flow_id, json=cred_data)
        if login_req.status_code == 200:
            login_req = json.loads(login_req.content)
            session_id = login_req["session_token"]
            data["details"] = "Login Succesfull"
            data["token"] = session_id
            return data
        else:
            raise HTTPException(status_code=401, detail="Invalid Credential")

def user_role_add(user_id,roles_list):
    """user role add from admin"""
    base_url = ADMIN_BASE_URL+"identities/"
    url = base_url + str(user_id)

    response = requests.get(url)
    if response.status_code == 200:
        user_data = json.loads(response.content)

    else:
        raise HTTPException(status_code=401, detail=json.loads(response.content))

    schema_id = user_data["schema_id"]
    state = user_data["state"]
    traits = user_data["traits"]
    exist_roles = []

    if "" in roles_list or len(roles_list) == 0:
        roles_list = ["None"]

    for list in roles_list:
        if list in traits["userrole"]:
            exist_roles.append(list)
        else:
            traits["userrole"].append(list)
    roles_list = traits["userrole"]

    data = {
    "schema_id": schema_id,
    "state": state,
    "traits": traits
    }

    if len(exist_roles) > 0:
        raise AlreadyExistsException("Already Exist permisions %s"%exist_roles)
    else:
        headers = {}
        headers["Content-Type"] = "application/json"
        Response = requests.put(url,headers=headers,json=data)
        
        if Response.status_code == 200:
            resp_data = json.loads(Response.content)
            if roles_list == resp_data["traits"]["userrole"]:
                return {"Success":True,"details":"User Roles Updated"}
            else:
                return {"Success":False,"details":"Something went wrong .. Try again!"}    
        else:
            raise HTTPException(status_code=401, detail=json.loads(Response.content))

#Create Super User 
def create_super_user():
    """function to create super user on startup"""
    super_user_url = ADMIN_BASE_URL+ "identities"

    #need to add in env
    super_username = "superadmin@gmail.com"
    super_password = "adminpassword@1"

    found = False
    response = requests.get(super_user_url)
    if response.status_code == 200:
        identity_data = json.loads(response.content)
        for identity in identity_data:
            if super_username ==  identity["traits"]["email"]:
                found = True
    else:
        raise HTTPException(status_code=401, detail=json.loads(response.content))      

    if not found:
        register_url = PUBLIC_BASE_URL+"registration/api"
        reg_flow = requests.get(register_url)
        if reg_flow.status_code == 200:
            flow_res = json.loads(reg_flow.content)
            reg_flow_id = flow_res["ui"]["action"]
            reg_data = {"traits.email": super_username,
                        "traits.name.first": "Super",
                        "traits.name.last": "Admin",
                        "password": super_password,
                        "traits.userrole":"SuperAdmin",
                        "method": "password"}
            headers = {}
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            reg_req = requests.post(reg_flow_id,headers=headers,json=reg_data)
            reg_response = json.loads(reg_req.content)
            if reg_req.status_code == 200:
                print("Super Admin Created")
            elif reg_req.status_code == 400:
                raise HTTPException(status_code=401, detail="Error on creating SUper Admin")
    else:
        print("Super Admin already exist")        

