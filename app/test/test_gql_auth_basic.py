"""Basic test cases of features Register, Login, Logout, Role assignment, delete identity"""
import os
import pytest
from urllib.parse import quote

from graphql_api import types
from . import gql_request

SUPER_USER = os.environ.get("VACHAN_SUPER_USERNAME")
SUPER_PASSWORD = os.environ.get("VACHAN_SUPER_PASSWORD")
ADMIN_BASE_URL = os.environ.get("VACHAN_KRATOS_ADMIN_URL")

#Fixture for delete users from kratos created
@pytest.fixture
def create_user_fixture():
    """fixture for revoke created user Kratos"""
    try:
        create_user = []
        yield create_user
    finally:
        delete_user_identity(create_user)

#GraphQl Login
def login(data):
    """login function for graphql"""
    login_qry = """
            query login($email:String! , $password:String!){
        login(userEmail:$email,password:$password){
            message
            token
        }
        }
    """
    login_var = {
    "email": data['user_email'],
    "password": data['password']
    }
    executed = gql_request(query=login_qry, variables=login_var)
    return executed

#registration check
def register(data,apptype):
    """test for registration"""
    reg_qry = """
            mutation register($app:AppInput,$object:RegisterInput){
    register(registrationArgs:$object,appType:$app){
        message
    registeredDetails{
      id
      email
      permissions
    }
    token
  }
    }
    """
    reg_var = {
        "app": apptype,
        "object": {
            "email": data['email'],
            "password": data['password']
        }
    }
    reg_var["object"]["firstname"] = data['firstname'] if 'firstname' in data else ''
    reg_var["object"]["lastname"] = data["lastname"] if 'lastname' in data else ''

    executed = gql_request(query=reg_qry, operation="mutation", variables=reg_var)
    return executed

#delete created user with super admin authentication
def delete_user_identity(users_list):
    """delete a user identity"""
    data = {
        "user_email": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    response = login(data)
    token =  response["data"]["login"]["token"]

    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token
                }

    del_qry = """
        mutation($identity:UserIdentity){
  deleteIdentity(identity:$identity){
    message
  }
}
    """
    for identity in users_list:
        del_var ={
        "identity": {
        "userid": identity
            }
        }
        executed = gql_request(query=del_qry, operation="mutation",
            variables=del_var, headers=headers)
        assert executed["data"]['deleteIdentity']["message"] ==\
            "deleted identity "+ str(identity)

#role assignment
def assign_roles(data,user_id,role_list):
    """assign roles to users"""
    response = login(data)
    token =  response["data"]["login"]["token"]
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }

    user_role_qry = """
        mutation userrole($object:UserroleInput){
    updateUserrole(userRolesArgs:$object){
        message
    roleList
  }
    }
    """
    user_role_var = {
    "object": {
        "userid": user_id,
        "roles": role_list
    }
    }
    executed = gql_request(query=user_role_qry, operation="mutation",
            variables=user_role_var, headers=headers)
    return executed

#logout user
def logout_user(token):
    """logout a user"""
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }
    logout_qry = """
        {
    logout
    }
    """
    executed = gql_request(query=logout_qry,headers=headers)
    return executed

#--------------------------------------------test starts--------------------------------------

#test for super user login
def test_superuser_login():
    """test for super user login"""
    data = {
  "user_email": SUPER_USER,
  "password": SUPER_PASSWORD
}
    response =login(data)
    data = response["data"]["login"]
    assert data["message"] == "Login Succesfull"
    assert len(data["token"]) == 32

#Register user wihtout passing the App type
def test_register_user_with_none_apptype(create_user_fixture):
    """register user with none type as app"""

    reg_qry = """
            mutation register($app:AppInput,$object:RegisterInput){
    register(registrationArgs:$object,appType:$app){
        message
    registeredDetails{
      id
      email
      permissions
    }
    token
  }
    }
    """
    reg_var = {
        "object": {
        "email": "ab@gmail.com",
        "password": "passwordab@1",
        "firstname": "user registration",
        "lastname": "AB Test"
        }
    }
    executed = gql_request(query=reg_qry, operation="mutation", variables=reg_var)
    data = executed["data"]["register"]
    assert data["message"] == "Registration Successfull"
    assert data['registeredDetails']["permissions"] == [types.App.API.name]
    ab_id = data["registeredDetails"]["id"]
    users_list = create_user_fixture
    users_list.append(ab_id)

#Try logging in user ABC before and after registration.
def test_login_register(create_user_fixture):
    """series of test based on login and register"""
    #login a non exisitng user ABC
    data = {
        "user_email": "abc@gmail.com",
        "password": "passwordabc@1"
    }
    response = login(data)
    assert 'errors' in  response

    #register the user ABC
    data = {
        "email": "abc@gmail.com",
        "password": "passwordabc@1",
        "firstname": "user registration",
        "lastname": "ABC Test"
    }
    executed = register(data,apptype=types.App.API.name)
    data = executed["data"]["register"]
    assert data["message"] == "Registration Successfull"
    abc_id = data["registeredDetails"]["id"]

    #test user ABC login after register
    data = {
        "user_email": "abc@gmail.com",
        "password": "passwordabc@1"
    }
    response =login(data)
    data = response["data"]["login"]
    assert data["message"] == "Login Succesfull"
    assert len(data["token"]) == 32

    #register user ABC again with same credentials
    data = {
        "email": "abc@gmail.com",
        "password": "passwordabc@1",
        "firstname": "user registration",
        "lastname": "ABC Test"
    }
    executed = register(data,apptype=types.App.API.name)
    assert "errors" in executed

    users_list = create_user_fixture
    users_list.append(abc_id)

#test for validate register data
def test_incorrect_email():
    """test for validation of incorrect email"""
    data = {
        "email": "incorrectemail",
        "password": "passwordabc@1"
    }
    executed = register(data,apptype=types.App.API.name)
    assert "errors" in executed

#test for validate register data
def test_validate_password():
    """test for validation of password"""
    #short password
    data = {
        "email": "PQR@gmail.com",
        "password": "test"
    }
    executed = register(data,apptype=types.App.API.name)
    assert "errors" in executed

    #less secure password
    data = {
        "email": "PQR@gmail.com",
        "password": "password"
    }
    executed = register(data,apptype=types.App.API.name)
    assert "errors" in executed

#test for optional params in registration
def test_optional_register_params(create_user_fixture):
    """test for optional params in the registration"""
    #app type is none
    data = {
        "email": "abc@gmail.com",
        "password": "passwordabc@1",
        "firstname": "user registration",
        "lastname": "ABC Test"
    }
    executed = register(data,apptype=types.App.API.name)
    data = executed["data"]["register"]
    assert data["message"] == "Registration Successfull"
    abc_id = data["registeredDetails"]["id"]

    #no first and last name, registration execute without error
    data = {
        "email": "abc1@gmail.com",
        "password": "passwordabc@1"
    }
    executed1 = register(data,apptype=types.App.API.name)
    data = executed1["data"]["register"]
    assert data["message"] == "Registration Successfull"
    abc1_id = data["registeredDetails"]["id"]

    users_list = create_user_fixture
    users_list.append(abc_id)
    users_list.append(abc1_id)

#Register new users, xyz1, xyz2, xyz3 with app_info as "Vachan-online or vachan-app", 
# "Autographa" and API-user respectively.
#Check logins and their user roles
def test_register_roles(create_user_fixture):
    """check for expected roles on register"""
    data_xyz1 = {
        "email": "xyz1@gmail.com",
        "password": "passwordxyz1@1",
        "firstname": "user XYZ1",
        "lastname": "Vachan role Test"
    }
    executed1 = register(data_xyz1,apptype=types.App.VACHAN.name)
    data = executed1["data"]["register"]
    assert data["message"] == "Registration Successfull"
    assert data['registeredDetails']["permissions"] == [types.App.VACHAN.name]
    xyz1_id = data["registeredDetails"]["id"]

    data_xyz2 = {
        "email": "xyz2@gmail.com",
        "password": "passwordxyz2@1",
        "firstname": "user XYZ2",
        "lastname": "Ag role Test"
    }
    executed2 = register(data_xyz2,apptype=types.App.AG.name)
    data = executed2["data"]["register"]
    assert data["message"] == "Registration Successfull"
    assert data['registeredDetails']["permissions"] == [types.App.AG.name]
    xyz2_id = data["registeredDetails"]["id"]

    data_xyz3 = {
        "email": "xyz3@gmail.com",
        "password": "passwordxyz3@1",
        "firstname": "user XYZ3",
        "lastname": "No role Test"
    }
    executed3 = register(data_xyz3,apptype=types.App.API.name)
    data = executed3["data"]["register"]
    assert data["message"] == "Registration Successfull"
    assert data['registeredDetails']["permissions"] == [types.App.API.name]
    xyz3_id = data["registeredDetails"]["id"]

    data_xyz4 = {
        "email": "xyz4@gmail.com",
        "password": "passwordxyz4@1",
        "firstname": "user XYZ4",
        "lastname": "No role Test"
    }
    # executed4 = register(data_xyz4,apptype=types.App.VACHANADMIN.name)
    # data = executed4["data"]["register"]
    # assert data["message"] == "Registration Successfull"
    # assert data['registeredDetails']["permissions"] == [types.App.VACHANADMIN.name]
    # xyz4_id = data["registeredDetails"]["id"]

    #login check for users
    data_xyz1 = {
        "user_email": "xyz1@gmail.com",
        "password": "passwordxyz1@1"
    }
    response = login(data_xyz1)
    data = response["data"]["login"]
    assert data["message"] == "Login Succesfull"
    assert len(data["token"]) == 32

    data_xyz2 = {
        "user_email": "xyz2@gmail.com",
        "password": "passwordxyz2@1"
    }
    response2 = login(data_xyz2)
    data = response2["data"]["login"]
    assert data["message"] == "Login Succesfull"
    assert len(data["token"]) == 32

    data_xyz3 = {
        "user_email": "xyz3@gmail.com",
        "password": "passwordxyz3@1"
    }
    response3 = login(data_xyz3)
    data = response3["data"]["login"]
    assert data["message"] == "Login Succesfull"
    assert len(data["token"]) == 32

    # data_xyz4 = {
    #     "user_email": "xyz4@gmail.com",
    #     "password": "passwordxyz4@1"
    # }
    # response4 = login(data_xyz4)
    # data = response4["data"]["login"]
    # assert data["message"] == "Login Succesfull"
    # assert len(data["token"]) == 32

    #Register same users xyz1, xyz2 & xyz3 as above with different app_info
    # and ensure that, their roles are appended

    #role changed vachan --> API
    data_xyz1 = {
        "email": "xyz1@gmail.com",
        "password": "passwordxyz1@1",
        "firstname": "user XYZ1",
        "lastname": "Vachan role Test",
    }
    response1 = register(data_xyz1,apptype=types.App.API.name)
    data = response1["data"]["register"]
    assert data["message"] == "User Already Registered, New Permission updated"
    assert data['registeredDetails']["permissions"] == \
        [types.App.VACHAN.name, types.App.API.name]

    # #role changed ag --> vachan
    data_xyz2 = {
        "email": "xyz2@gmail.com",
        "password": "passwordxyz2@1"
    }
    response2 = register(data_xyz2,apptype=types.App.VACHAN.name)
    data = response2["data"]["register"]
    assert data["message"] == "User Already Registered, New Permission updated"
    assert data['registeredDetails']["permissions"] == \
        [types.App.AG.name, types.App.VACHAN.name]

    #role changed none --> ag
    data_xyz3 = {
        "email": "xyz3@gmail.com",
        "password": "passwordxyz3@1"
    }
    response3 = register(data_xyz3,apptype=types.App.AG.name)
    data = response3["data"]["register"]
    assert data["message"] == "User Already Registered, New Permission updated"
    assert data['registeredDetails']["permissions"] == \
        [types.App.API.name, types.App.AG.name]

    # #role changed Vachan Admin --> ag
    # data_xyz4 = {
    #     "email": "xyz4@gmail.com",
    #     "password": "passwordxyz4@1"
    # }
    # response4 = register(data_xyz4,apptype=types.App.AG.name)
    # data = response4["data"]["register"]
    # assert data["message"] == "User Already Registered, New Permission updated"
    # assert data['registeredDetails']["permissions"] == \
    #     [types.App.VACHANADMIN.name, types.App.AG.name]

    users_list = create_user_fixture
    users_list.append(xyz1_id)
    users_list.append(xyz2_id)
    users_list.append(xyz3_id)
    # users_list.append(xyz4_id)

#Register two users with app_info=API
#and make them VachanAdmin and AgAdmin
#(ensure only SuperAdmin should be able to do this)
def test_role_assignment_superadmin(create_user_fixture):
    """test only super admin can assign roles"""

    #create 2 users
    user1 = {
        "email": "vachan@gmail.com",
        "password": "passwordvachan@1"
    }
    response1 = register(user1,apptype=types.App.API.name)
    data = response1["data"]["register"]
    assert data["message"] == "Registration Successfull"
    assert data['registeredDetails']["permissions"] == [types.App.API.name]
    user1_id = data["registeredDetails"]["id"]

    user2 = {
        "email": "ag@gmail.com",
        "password": "passwordag@1"
    }
    response2 = register(user2,apptype=types.App.API.name)
    data = response2["data"]["register"]
    assert data["message"] == "Registration Successfull"
    assert data['registeredDetails']["permissions"] == [types.App.API.name]
    user2_id = data["registeredDetails"]["id"]

    #try to change user2 permision after login user1
    user1 = {
        "user_email": "vachan@gmail.com",
        "password": "passwordvachan@1"
    }

    role_list = [types.AdminRoles.VACHANADMIN.name]
    response = assign_roles(user1,user2_id,role_list)
    assert "errors" in response

    #role assign with super user
    data_SA = {
        "user_email": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    role_list = [types.AdminRoles.VACHANADMIN.name]
    response1 = assign_roles(data_SA,user1_id,role_list)
    data = response1["data"]["updateUserrole"]
    assert data["message"] == "User Roles Updated"
    assert data["roleList"] ==\
        [types.AdminRoles.APIUSER.name, types.AdminRoles.VACHANADMIN.name]

    role_list = [types.AdminRoles.AGADMIN.name]
    response2 = assign_roles(data_SA,user2_id,role_list)
    data = response2["data"]["updateUserrole"]
    assert data["message"] == "User Roles Updated"
    assert data["roleList"] ==\
        [types.AdminRoles.APIUSER.name, types.AdminRoles.AGADMIN.name]

    #assigning a wrong role that is not allowed
    role_list = ["AllAdmin"]
    response3 = assign_roles(data_SA,user2_id,role_list)
    assert 'errors' in response3

    users_list = create_user_fixture
    users_list.append(user1_id)
    users_list.append(user2_id)

#Login a user and then log him out.
#Then try using the old token and ensure it is expired
def test_token_expiry(create_user_fixture):
    """checking the token expiry"""
    data = {
        "user_email": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    response = login(data)
    data = response["data"]["login"]
    assert data["message"] == "Login Succesfull"
    assert len(data["token"]) == 32
    token = data['token']

    #logout user
    response = logout_user(token)
    assert response["data"]["logout"] == "Successfully Logged out"

    #try change role with super user after logout
    user = {
        "email": "user@gmail.com",
        "password": "passworduser@1"
    }
    response2 = register(user,apptype=types.App.API.name)
    data = response2["data"]["register"]
    assert data["message"] == "Registration Successfull"
    assert data['registeredDetails']["permissions"] == [types.App.API.name]
    user_id = data["registeredDetails"]["id"]
    
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }

    user_role_qry = """
        mutation userrole($object:UserroleInput){
    updateUserrole(userRolesArgs:$object){
        message
    roleList
  }
    }
    """
    user_role_var = {
    "object": {
        "userid": user_id,
        "roles": [types.AdminRoles.AGADMIN.name]
    }
    }
    executed = gql_request(query=user_role_qry, operation="mutation",
            variables=user_role_var, headers=headers)

    users_list = create_user_fixture
    users_list.append(user_id)

    assert "errors" in executed