"""Basic test cases of features Register, Login, Logout, Role assignment"""
import json
import os
import pytest
from urllib.parse import quote

from app.schema import schema_auth
from . import assert_input_validation_error, client, check_skip, check_limit
from .conftest import initial_test_users

LOGIN_URL = '/v2/user/login'
REGISTER_URL = '/v2/user/register'
LOGOUT_URL = '/v2/user/logout'
GETUSERURL = '/v2/users'
USERROLE_URL = '/v2/user/role'
DELETE_URL = '/v2/user/delete-identity'
SUPER_USER = os.environ.get("VACHAN_SUPER_USERNAME")
SUPER_PASSWORD = os.environ.get("VACHAN_SUPER_PASSWORD")
ADMIN_BASE_URL = os.environ.get("VACHAN_KRATOS_ADMIN_URL")

headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

#Fixture for delete users from kratos created
@pytest.fixture
def create_user_fixture():
    """fixture for revoke created user Kratos"""
    try:
        create_user = []
        yield create_user
    finally:
        delete_user_identity(create_user)

#login check
def login(data):
    '''test for login feature'''
    #headers = {"contentType": "application/json", "accept": "application/json"}
    params = f"?user_email={quote(data['user_email'])}&password={quote(data['password'])}"
    response = client.get(LOGIN_URL+params)
    if response.status_code == 200:
        assert response.json()['message'] == "Login Succesfull"
        token =  response.json()['token']
        assert len(token) == 32
        assert "userId" in response.json()
    elif response.status_code == 401:
        assert response.json()['error'] == "Authentication Error"
        assert response.json()['details'] ==\
            "The provided credentials are invalid, check for spelling mistakes "+\
            "in your password or username, email address, or phone number."
    return response

#registration check
def register(data,apptype):
    """test for registration"""
    headers = {"contentType": "application/json", "accept": "application/json"}
    params = f"?app_type={apptype}"
    response = client.post(REGISTER_URL+params, headers=headers, json=data)
    if response.status_code == 200:
        assert response.json()["message"] == "Registration Successfull"
        assert isinstance(response.json()["registered_details"],dict)
        assert "id" in response.json()["registered_details"]
        assert "email" in response.json()["registered_details"]
        assert "Permissions" in response.json()["registered_details"]
        assert "token" in response.json()
        token =  response.json()['token']
        assert len(token) == 32
    return response

#appending roles to same user on duplicate registration
def register_role_appending(data,apptype):
    """test for appending roles for same user registration"""
    headers = {"contentType": "application/json", "accept": "application/json"}
    params = f"?app_type={apptype}"
    response = client.post(REGISTER_URL+params, headers=headers, json=data)
    if response.status_code == 200:
        assert response.json()["message"] == "User Already Registered, New Permission updated"
        assert isinstance(response.json()["registered_details"],dict)
        assert "id" in response.json()["registered_details"]
        assert "email" in response.json()["registered_details"]
        assert "Permissions" in response.json()["registered_details"]
        assert "token" in response.json()
        assert response.json()['token'] == 'null'
    return response

#delete created user with super admin authentication
def delete_user_identity(users_list):
    """delete a user identity"""
    data = {
        "user_email": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    response = login(data)
    token =  response.json()['token']

    for identity in users_list:
        data = {
            "userid": identity
        }
        headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token
                }
        response = client.delete(DELETE_URL, headers=headers, json=data)
        assert response.status_code == 200
        assert response.json()["message"] == \
            "deleted identity "+ str(identity)

#role assignment
def assign_roles(data,user_id,role_list):
    """assign roles to users"""
    response = login(data)
    token =  response.json()['token']

    role_data = {
        "userid": user_id,
        "roles": role_list
    }

    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }
    response = client.put(USERROLE_URL, headers=headers, json=role_data)
    return response

#logout user
def logout_user(token):
    """logout a user"""
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }
    response = client.get(LOGOUT_URL,headers=headers)
    return response

#--------------------------------------------test starts--------------------------------------

#test for super user login
def test_superuser_login():
    """test for super user login"""
    data = {
  "user_email": SUPER_USER,
  "password": SUPER_PASSWORD
}
    response =login(data)
    assert response.json()['message'] == "Login Succesfull"

#not passing the App type in the url params
def test_register_user_with_none_apptype(create_user_fixture):
    """register user with none type as app"""
    data = {
        "email": "ab@gmail.com",
        "password": "passwordab@1",
        "firstname": "user registration",
        "lastname": "AB Test"
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(REGISTER_URL, headers=headers, json=data)
    assert response.json()['message'] == "Registration Successfull"
    ab_id = response.json()["registered_details"]["id"]
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
    assert 'error' in  response.json()

    #register the user ABC
    data = {
        "email": "abc@gmail.com",
        "password": "passwordabc@1",
        "firstname": "user registration",
        "lastname": "ABC Test"
    }
    response = register(data,apptype=schema_auth.App.API.value)
    abc_id = response.json()["registered_details"]["id"]

    #test user ABC login after register
    data = {
        "user_email": "abc@gmail.com",
        "password": "passwordabc@1"
    }
    response = login(data)
    assert response.json()['message'] == "Login Succesfull"

    #register user ABC again with same credentials
    data = {
        "email": "abc@gmail.com",
        "password": "passwordabc@1",
        "firstname": "user registration",
        "lastname": "ABC Test"
    }
    response = register(data,apptype=schema_auth.App.API.value)
    assert response.status_code == 400
    assert response.json()['error'] == "HTTP Error"
    assert response.json()['details'] == \
      "An account with the same identifier (email, phone, username, ...) exists already."

    users_list = create_user_fixture
    users_list.append(abc_id)


#test for validate register data
def test_incorrect_email():
    """test for validation of incorrect email"""
    data = {
        "email": "incorrectemail",
        "password": "passwordabc@1"
    }
    response = register(data,apptype=schema_auth.App.API.value)
    assert response.status_code == 422
    assert response.json()['error'] == "Unprocessable Data"

#test for validate register data
def test_validate_password():
    """test for validation of password"""
    #short password
    data = {
        "email": "PQR@gmail.com",
        "password": "test"
    }
    response = register(data,apptype=schema_auth.App.API.value)
    assert response.status_code == 422
    assert response.json()['error'] == "Unprocessable Data"

    #less secure password
    data = {
        "email": "PQR@gmail.com",
        "password": "password"
    }
    response = register(data,apptype=schema_auth.App.API.value)
    assert response.status_code == 422
    assert response.json()['error'] == "Unprocessable Data"

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
    response = register(data,apptype=schema_auth.App.API.value)
    assert response.json()["registered_details"]["Permissions"] == \
        [schema_auth.App.API.value]
    abc_id = response.json()["registered_details"]["id"]

    #no first and last name, registration execute without error
    data = {
        "email": "abc1@gmail.com",
        "password": "passwordabc@1"
    }
    response1 = register(data,apptype=schema_auth.App.API.value)
    abc1_id = response1.json()["registered_details"]["id"]

    users_list = create_user_fixture
    users_list.append(abc_id)
    users_list.append(abc1_id)

#test register with missing field
def test_register_incorrectdatas():
    """wrong data type check"""
    data = {
  "firstname": "user registration",
  "lastname": "ABC Test"
}
    response = register(data,apptype=schema_auth.App.API.value)
    assert_input_validation_error(response)

    data = {
  "email": "abc@gmail.com"
}
    response = register(data,apptype=schema_auth.App.API.value)
    assert_input_validation_error(response)

    data = {
  "password": "passwordabc@1"
}
    response = register(data,apptype=schema_auth.App.API.value)
    assert_input_validation_error(response)


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
    response1 = register(data_xyz1,apptype=schema_auth.App.VACHAN.value)
    xyz1_id = response1.json()["registered_details"]["id"]
    assert response1.json()["registered_details"]["Permissions"] == \
            [schema_auth.App.VACHAN.value]

    data_xyz2 = {
        "email": "xyz2@gmail.com",
        "password": "passwordxyz2@1",
        "firstname": "user XYZ2",
        "lastname": "Ag role Test"
    }
    response2 = register(data_xyz2,apptype= schema_auth.App.AG.value)
    xyz2_id = response2.json()["registered_details"]["id"]
    assert response2.json()["registered_details"]["Permissions"] == \
        [ schema_auth.App.AG.value]
    data_xyz3 = \
        {
        "email": "xyz3@gmail.com",
        "password": "passwordxyz3@1",
        "firstname": "user XYZ3",
        "lastname": "No role Test"
    }
    response3 = register(data_xyz3,apptype=schema_auth.App.API.value)
    xyz3_id = response3.json()["registered_details"]["id"]
    assert response3.json()["registered_details"]["Permissions"] == [schema_auth.App.API.value]

    # data_xyz4 = {
    #     "email": "xyz4@gmail.com",
    #     "password": "passwordxyz4@1",
    #     "firstname": "user XYZ4",
    #     "lastname": "No role Test"
    # }
    # response4 = register(data_xyz4,apptype=schema_auth.App.VACHANADMIN.value)
    # xyz4_id = response4.json()["registered_details"]["id"]
    # assert response4.json()["registered_details"]["Permissions"] == \
    #     [schema_auth.App.VACHANADMIN.value]

    #login check for users
    data_xyz1 = {
        "user_email": "xyz1@gmail.com",
        "password": "passwordxyz1@1"
    }
    response = login(data_xyz1)
    assert response.json()['message'] == "Login Succesfull"

    data_xyz2 = {
        "user_email": "xyz2@gmail.com",
        "password": "passwordxyz2@1"
    }
    response2 = login(data_xyz2)
    assert response2.json()['message'] == "Login Succesfull"

    data_xyz3 = {
        "user_email": "xyz3@gmail.com",
        "password": "passwordxyz3@1"
    }
    response3 = login(data_xyz3)
    assert response3.json()['message'] == "Login Succesfull"

    # data_xyz4 = {
    #     "user_email": "xyz4@gmail.com",
    #     "password": "passwordxyz4@1"
    # }
    # response4 = login(data_xyz4)
    # assert response4.json()['message'] == "Login Succesfull"

    #Register same users xyz1, xyz2 & xyz3 as above with different app_info
    # and ensure that, their roles are appended

    #role changed vachan --> none
    data_xyz1 = {
        "email": "xyz1@gmail.com",
        "password": "passwordxyz1@1",
        "firstname": "user XYZ1",
        "lastname": "Vachan role Test",
    }
    response1 = register_role_appending(data_xyz1,apptype=schema_auth.App.API.value)
    assert response1.json()["registered_details"]["Permissions"] == \
        [schema_auth.App.VACHAN.value,schema_auth.App.API.value]

    # #role changed ag --> vachan
    data_xyz2 = {
        "email": "xyz2@gmail.com",
        "password": "passwordxyz2@1"
    }
    response2 = register_role_appending(data_xyz2,apptype=schema_auth.App.VACHAN.value)
    assert response2.json()["registered_details"]["Permissions"] ==\
        [schema_auth.App.AG.value,schema_auth.App.VACHAN.value]

    #role changed none --> ag
    data_xyz3 = {
        "email": "xyz3@gmail.com",
        "password": "passwordxyz3@1"
    }
    response3 = register_role_appending(data_xyz3,apptype=schema_auth.App.AG.value)
    assert response3.json()["registered_details"]["Permissions"] ==\
        [schema_auth.App.API.value,schema_auth.App.AG.value]

    # #role changed Vachan Admin --> ag
    # data_xyz4 = {
    #     "email": "xyz4@gmail.com",
    #     "password": "passwordxyz4@1"
    # }
    # response4 = register_role_appending(data_xyz4,apptype=schema_auth.App.AG.value)
    # assert response4.json()["registered_details"]["Permissions"] == \
    #     [schema_auth.App.VACHANADMIN.value,schema_auth.App.AG.value]

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
    response1 = register(user1,apptype=schema_auth.App.API.value)
    user1_id = response1.json()["registered_details"]["id"]
    assert response1.json()["registered_details"]["Permissions"] == [schema_auth.App.API.value]

    user2 = {
        "email": "ag@gmail.com",
        "password": "passwordag@1"
    }
    response2 = register(user2,apptype=schema_auth.App.API.value)
    user2_id = response2.json()["registered_details"]["id"]
    assert response2.json()["registered_details"]["Permissions"] == [schema_auth.App.API.value]

    #try to change user2 permision after login user1
    user1 = {
        "user_email": "vachan@gmail.com",
        "password": "passwordvachan@1"
    }

    role_list = [schema_auth.AdminRoles.VACHANADMIN.value]
    response = assign_roles(user1,user2_id,role_list)
    assert response.status_code == 403
    assert response.json()["details"] == "Access Permission Denied for the URL"

    #role assign with super user
    data = {
        "user_email": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    role_list = [schema_auth.AdminRoles.VACHANADMIN.value]
    response1 = assign_roles(data,user1_id,role_list)
    assert response1.status_code == 201
    assert response1.json()["role_list"] == \
        [schema_auth.AdminRoles.APIUSER.value, schema_auth.AdminRoles.VACHANADMIN.value]

    role_list = [schema_auth.AdminRoles.AGADMIN.value]
    response2 = assign_roles(data,user2_id,role_list)
    assert response2.status_code == 201
    assert response2.json()["role_list"] == \
        [schema_auth.AdminRoles.APIUSER.value, schema_auth.AdminRoles.AGADMIN.value]

    #assigning a wrong role that is not allowed
    role_list = ["AllAdmin"]
    response3 = assign_roles(data,user2_id,role_list)
    assert response3.status_code == 422
    assert response3.json()['error'] == "Input Validation Error"

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
    assert response.json()['message'] == "Login Succesfull"
    token =  response.json()['token']

    #logout user
    response = logout_user(token)
    assert response.status_code == 200

    #try change role with super user after logout
    user = {
        "email": "user@gmail.com",
        "password": "passworduser@1"
    }
    response2 = register(user,apptype=schema_auth.App.API.value)
    user_id = response2.json()["registered_details"]["id"]
    assert response2.json()["registered_details"]["Permissions"] == [schema_auth.App.API.value]

    role_data = {
        "userid": user_id,
        "roles": [schema_auth.AdminRoles.AGADMIN.value]
    }
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }
    response = client.put(USERROLE_URL, headers=headers, json=role_data)

    users_list = create_user_fixture
    users_list.append(user_id)

    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"

def test_get_put_users():
    """get users"""
    #get list of users
    #without auth
    params = f"?skip=0&limit=100"
    response = client.get(GETUSERURL+params)
    assert response.status_code == 401
    #with Auth
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert response.status_code == 200
    assert isinstance(response.json(),list)
    assert len(response.json()) >= len(initial_test_users)
    for item in response.json():
        assert "userId" in item
        assert "name" in item
        assert isinstance(item["name"],dict)

    #users created in initial test users-check pagination content
    check_skip(GETUSERURL,headers_auth)
    check_limit(GETUSERURL,headers_auth)

    #filter with name
    params = f"?name=api&roles={schema_auth.FilterRoles.ALL}"
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert len(response.json()) >= 2

    #filter with not available name in initial test user
    params = f"?name=aqsdwerfgtyuiolkj&roles={schema_auth.FilterRoles.ALL}"
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert len(response.json()) == 0

    #filter with roles
    params = f"?roles={schema_auth.FilterRoles.ALL}"
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert len(response.json()) >=8

    params = f"?roles={schema_auth.FilterRoles.API}"
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert len(response.json()) >=3

    params = f"?roles={schema_auth.FilterRoles.AG}"
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert len(response.json()) >=2

    params = f"?roles={schema_auth.FilterRoles.VACHAN}"
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert len(response.json()) >=2

    params = f"?roles={schema_auth.FilterRoles.VACHAN}&roles={schema_auth.FilterRoles.AG}"
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert len(response.json()) >=4

    #get user
    params = f"?user_id={initial_test_users['APIUser']['test_user_id']}"
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["userId"] == initial_test_users['APIUser']['test_user_id']
    assert response.json()[0]["name"]["first"] == initial_test_users['APIUser']['firstname']

    #wrong user id
    params = f"?user_id=hgtyr-1234-tthhh-6677-yyyyyy-67777-111"
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert response.status_code == 404
    assert response.json()["error"] == "Requested Content Not Available"

    #edit user
    #No auth
    data = {
    'firstname': 'API user',
    'lastname': 'Edited'
    }
    response = client.put(f"/v2/user/{initial_test_users['APIUser']['test_user_id']}",json=data)
    assert response.status_code == 401
    assert response.json()["error"] == 'Authentication Error'

    #with auth super admin
    data_SA = {
        "user_email": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    response = login(data_SA)
    token =  response.json()['token']

    #before update get data
    params = f"?user_id={initial_test_users['APIUser']['test_user_id']}"
    response = client.get(GETUSERURL+params,headers=headers_auth)
    assert response.json()[0]["userId"] == initial_test_users['APIUser']['test_user_id']
    assert response.json()[0]["name"]["first"] == initial_test_users['APIUser']['firstname']

    #SA
    headers_SA = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }
    response = client.put(f"/v2/user/{initial_test_users['APIUser']['test_user_id']}",json=data,headers=headers_SA)
    assert response.status_code == 201
    assert response.json()["message"] == "User details updated successfully"
    assert "userId" in response.json()["data"]
    assert "name" in response.json()["data"]
    assert response.json()["data"]["name"]["first"] == data["firstname"]
    assert response.json()["data"]["name"]["last"] == data["lastname"]  
    assert response.json()["data"]["name"]["first"] != initial_test_users['APIUser']['firstname']
    assert response.json()["data"]["name"]["last"] != initial_test_users['APIUser']['firstname']
    #Created User
    data = {
    'firstname': 'API',
    'lastname': 'Edited by createdUser'
    }

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    response1 = client.put(f"/v2/user/{initial_test_users['APIUser']['test_user_id']}",json=data,headers=headers_auth)
    assert response1.status_code == 201
    assert response.json()["message"] == "User details updated successfully"
    assert "userId" in response.json()["data"]
    assert "name" in response.json()["data"]
    assert response1.json()["data"]["name"]["first"] == data["firstname"]
    assert response1.json()["data"]["name"]["last"] == data["lastname"]
    assert response1.json()["data"]["name"]["first"] != response.json()["data"]["name"]["first"]
    assert response1.json()["data"]["name"]["last"] != response.json()["data"]["name"]["last"]

    #user otherthan created and SA
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response2 = client.put(f"/v2/user/{initial_test_users['APIUser']['test_user_id']}",json=data,headers=headers_auth)
    assert response2.status_code == 403
    assert response2.json()["error"] == "Permission Denied"
