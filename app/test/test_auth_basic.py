"""Basic test cases of features Register, Login, Logout, Role assignment"""
import os
from . import assert_input_validation_error, client

LOGIN_URL = '/login'
REGISTER_URL = '/register'
LOGOUT_URL = '/logout'
USERROLE_URL = '/userrole'
DELETE_URL = '/delete-identity'
SUPER_USER = os.environ.get("SUPER_USERNAME")
SUPER_PASSWORD = os.environ.get("SUPER_PASSWORD")
ADMIN_BASE_URL = os.environ.get("KRATOS_ADMIN_BASE_URL")

#login check
def login(data):
    '''test for login feature'''
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(LOGIN_URL, headers=headers, json=data)
    if response.status_code == 200:
        assert response.json()['details'] == "Login Succesfull"
        token =  response.json()['token']
        assert len(token) == 32
    elif response.status_code == 401:
        assert response.json()['error'] == "HTTP Error"
        assert response.json()['details'] == "Invalid Credential"
    return response

#registration check
def register(data):
    """test for registration"""
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(REGISTER_URL, headers=headers, json=data)
    if response.status_code == 200:
        assert response.json()["details"] == "Registration Successfull"
        assert isinstance(response.json()["registered_details"],dict)
        assert "id" in response.json()["registered_details"]
        assert "email" in response.json()["registered_details"]
        assert "Name" in response.json()["registered_details"]
        assert "Permisions" in response.json()["registered_details"]
        assert "token" in response.json()
        token =  response.json()['token']
        assert len(token) == 32
    return response

#appending roles to same user on duplicate registration
def register_role_appending(data):
    """test for appending roles for same user registration"""
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(REGISTER_URL, headers=headers, json=data)
    if response.status_code == 200:
        assert response.json()["details"] == "User Already Registered, New Permision updated"
        assert isinstance(response.json()["registered_details"],dict)
        assert "id" in response.json()["registered_details"]
        assert "email" in response.json()["registered_details"]
        assert "Permisions" in response.json()["registered_details"]
    return response

#delete created user with super admin authentication
def delete_user_identity(id):
    """delete a user identity"""
    data = {
        "username": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    response = login(data)
    token =  response.json()['token']
    data = {
        "userid": id
    }
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }
    response = client.delete(DELETE_URL, headers=headers, json=data)
    assert response.status_code == 200
    assert response.json()["success"] == \
        "deleted identity "+ id

#role assignemnt
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
    response = client.post(USERROLE_URL, headers=headers, json=role_data)
    return response

#logout user
def logout_user(token):
    """logout a user"""
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }
    response = client.post(LOGOUT_URL, headers=headers)
    return response
#--------------------------------------------test starts--------------------------------------

#test for super user login
def test_superuser_login():
    """test for super user login"""
    data = {
  "username": SUPER_USER,
  "password": SUPER_PASSWORD
}
    login(data)

#Try logging in user ABC before and after registration.
def test_login_register():
    """series of test based on login and register"""

    #login a non exisitng user ABC
    data = {
        "username": "abc@gmail.com",
        "password": "passwordabc@1"
    }
    login(data)

    #register the user ABC
    data = {
        "email": "abc@gmail.com",
        "password": "passwordabc@1",
        "firstname": "user registration",
        "lastname": "ABC Test",
        "appname": ""
    }
    response = register(data)
    ABC_id = response.json()["registered_details"]["id"]

    #test user ABC login after register
    data = {
        "username": "abc@gmail.com",
        "password": "passwordabc@1"
    }
    login(data)

    #register user ABC again with same credentials
    data = {
        "email": "abc@gmail.com",
        "password": "passwordabc@1",
        "firstname": "user registration",
        "lastname": "ABC Test",
        "appname": ""
    }
    response = register(data)
    assert response.status_code == 400
    assert response.json()['error'] == "HTTP Error"
    assert response.json()['details'] == \
      "An account with the same identifier (email, phone, username, ...) exists already."

    delete_user_identity(ABC_id)

#test register with missing field
def test_register_incorrectdatas():
    """wrong data type check"""
    data = {
  "email": "abc@gmail.com",
  "appname": ""
}
    response = register(data)
    assert_input_validation_error(response)

    data = {
  "firstname": "user registration",
  "lastname": "ABC Test",
  "appname": ""
}
    response = register(data)
    assert_input_validation_error(response)

    data = {
  "email": "abc@gmail.com",
  "password": "passwordabc@1",
}
    response = register(data)
    assert_input_validation_error(response)

#Register new users, xyz1, xyz2, xyz3 with app_info as "Vachan", "Ag" and None respectively.
#Check logins and their user roles
def test_register_roles():
    """check for expected roles on register"""
    data_xyz1 = {
        "email": "xyz1@gmail.com",
        "password": "passwordxyz1@1",
        "firstname": "user XYZ1",
        "lastname": "Vachan role Test",
        "appname": "vachan"
    }
    response1 = register(data_xyz1)
    XYZ1_id = response1.json()["registered_details"]["id"]
    assert response1.json()["registered_details"]["Permisions"] == ['vachanuser']

    data_xyz2 = {
        "email": "xyz2@gmail.com",
        "password": "passwordxyz2@1",
        "firstname": "user XYZ2",
        "lastname": "Ag role Test",
        "appname": "ag"
    }
    response2 = register(data_xyz2)
    XYZ2_id = response2.json()["registered_details"]["id"]
    assert response2.json()["registered_details"]["Permisions"] == ['aguser']

    data_xyz3 = {
        "email": "xyz3@gmail.com",
        "password": "passwordxyz3@1",
        "firstname": "user XYZ3",
        "lastname": "No role Test",
        "appname": ""
    }
    response3 = register(data_xyz3)
    XYZ3_id = response3.json()["registered_details"]["id"]
    assert response3.json()["registered_details"]["Permisions"] == ['None']

    #login check for users
    data_xyz1 = {
        "username": "xyz1@gmail.com",
        "password": "passwordxyz1@1"
    }
    login(data_xyz1)

    data_xyz2 = {
        "username": "xyz2@gmail.com",
        "password": "passwordxyz2@1"
    }
    login(data_xyz2)

    data_xyz3 = {
        "username": "xyz3@gmail.com",
        "password": "passwordxyz3@1"
    }
    login(data_xyz3)

    #Register same users xyz1, xyz2 & xyz3 as above with different app_info
    # and ensure that, their roles are appended

    #role changed vachan --> none
    data_xyz1 = {
        "email": "xyz1@gmail.com",
        "password": "passwordxyz1@1",
        "firstname": "user XYZ1",
        "lastname": "Vachan role Test",
        "appname": ""
    }
    response1 = register_role_appending(data_xyz1)
    assert response1.json()["registered_details"]["Permisions"] == ['vachanuser','None']

    # #role changed ag --> vachan
    data_xyz2 = {
        "email": "xyz2@gmail.com",
        "password": "passwordxyz2@1",
        "firstname": "user XYZ2",
        "lastname": "Ag role Test",
        "appname": "vachan"
    }
    response2 = register_role_appending(data_xyz2)
    assert response2.json()["registered_details"]["Permisions"] == ['aguser','vachanuser']

    #role changed none --> ag
    data_xyz3 = {
        "email": "xyz3@gmail.com",
        "password": "passwordxyz3@1",
        "firstname": "user XYZ3",
        "lastname": "No role Test",
        "appname": "ag"
    }
    response3 = register_role_appending(data_xyz3)
    assert response3.json()["registered_details"]["Permisions"] == ['None','aguser']

    delete_user_identity(XYZ1_id)
    delete_user_identity(XYZ2_id)
    delete_user_identity(XYZ3_id)

#Register two users with app_info=None
#and make them VachanAdmin and AgAdmin
#(ensure only SuperAdmin should be able to do this)
def test_role_assignment_superadmin():
    """test only super admin can assign roles"""

    #create 2 users
    user1 = {
        "email": "vachan@gmail.com",
        "password": "passwordvachan@1",
        "firstname": "user vachan",
        "lastname": "No role Test",
        "appname": ""
    }
    response1 = register(user1)
    user1_id = response1.json()["registered_details"]["id"]
    assert response1.json()["registered_details"]["Permisions"] == ['None']

    user2 = {
        "email": "ag@gmail.com",
        "password": "passwordag@1",
        "firstname": "user ag",
        "lastname": "No role Test",
        "appname": ""
    }
    response2 = register(user2)
    user2_id = response2.json()["registered_details"]["id"]
    assert response2.json()["registered_details"]["Permisions"] == ['None']

    #try to change user2 permision after login user1
    user1 = {
        "username": "vachan@gmail.com",
        "password": "passwordvachan@1"
    }

    role_list = ["VachanAdmin"]
    response = assign_roles(user1,user2_id,role_list)
    assert response.status_code == 403
    assert response.json()["details"] == "User have no permision to access API"

    #role assign with super user
    data = {
        "username": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    role_list = ["VachanAdmin"]
    response1 = assign_roles(data,user1_id,role_list)
    assert response1.status_code == 200
    assert response1.json()["Success"]
    assert response1.json()["role_list"] == ["None", "VachanAdmin"]

    role_list = ["AgAdmin"]
    response2 = assign_roles(data,user2_id,role_list)
    assert response2.status_code == 200
    assert response2.json()["Success"]
    assert response2.json()["role_list"] == ["None", "AgAdmin"]

    delete_user_identity(user1_id)
    delete_user_identity(user2_id)

#Login a user and then log him out.
#Then try using the old token and ensure it is expired
def test_toke_expiry():
    """checking the token expiry"""
    data = {
        "username": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    response = login(data)
    token =  response.json()['token']

    #logout user
    response = logout_user(token)
    assert response.status_code == 200

    #try change role with super user after logout
    user = {
        "email": "user@gmail.com",
        "password": "passworduser@1",
        "firstname": "user Normal",
        "lastname": "No role Test",
        "appname": ""
    }
    response2 = register(user)
    user_id = response2.json()["registered_details"]["id"]
    assert response2.json()["registered_details"]["Permisions"] == ['None']

    role_data = {
        "userid": user_id,
        "roles": ["AgAdmin"]
    }
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }
    response = client.post(USERROLE_URL, headers=headers, json=role_data)

    delete_user_identity(user_id)

    assert response.status_code == 401
    assert response.json()["error"] == "HTTP Error"
