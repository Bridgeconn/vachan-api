"""Basic test cases of features Register, Login, Logout, Role assignment"""
import json
import os
import pytest
from urllib.parse import quote

from app.schema import schema_auth
from . import assert_input_validation_error, client, check_skip, check_limit, TEST_APPS_LIST, TEST_ROLE_LIST
from .conftest import initial_test_users, default_app_keys
from .test_auth_basic import login

LOGIN_URL = '/v2/app/key'
REGISTER_URL = '/v2/app/register'
LOGOUT_URL = '/v2/app/delete-key'
DELETE_URL = '/v2/app/delete-app'
SUPER_USER = os.environ.get("VACHAN_SUPER_USERNAME")
SUPER_PASSWORD = os.environ.get("VACHAN_SUPER_PASSWORD")
ADMIN_BASE_URL = os.environ.get("VACHAN_KRATOS_ADMIN_URL")

headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

#Fixture for delete users from kratos created
# @pytest.fixture
# def create_user_fixture():
#     """fixture for revoke created user Kratos"""
#     try:
#         create_user = []
#         yield create_user
#     finally:
#         delete_user_identity(create_user)

#app register
def register_app(data, app_key=None, user_token=None):
    """register a new app"""
    if app_key is not None:
        url = f"{REGISTER_URL}?app_key={app_key}"
    else:
        url = REGISTER_URL
    headers = {"contentType": "application/json",
                "accept": "application/json",
    }
    if user_token is not None:
        headers["Authorization"]= "Bearer"+" "+user_token
    response = client.post(url, json=data, headers=headers)
    if response.status_code == 201:
        assert "message" in response.json()
        assert "registered_details" in response.json()
        assert "key" in response.json()
    return response

#app delete
def delete_app(app_id, app_key=None, user_token=None):
    """delete app"""
    if app_key is not None:
        url = f"{DELETE_URL}?app_key={app_key}&app_id={app_id}"
    else:
        url = f"{DELETE_URL}?app_id={app_id}"
    headers = {"contentType": "application/json",
                "accept": "application/json",
        }
    if user_token is not None:
        headers["Authorization"]= "Bearer"+" "+user_token
    response = client.delete(url, headers=headers)
    if response.status_code == 200:
        assert "message" in response.json()
        assert response.json()["message"] == f"deleted app with id : {app_id}"
    return response

#app login
def generate_app_key(data):
    """Generate key for app"""
    #with auth super admin
    data_SA = {
        "user_email": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    response = login(data_SA)
    token =  response.json()['token']
    headers_SA = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+token
            }
    params = f"?app_email={quote(data['app_email'])}&password={quote(data['password'])}"
    response = client.get(LOGIN_URL+params, headers=headers_SA)
    if response.status_code == 200:
        assert response.json()['message'] == "Key generated successfully"
        key =  response.json()['key']
        assert len(key) == 32
        assert "appId" in response.json()
    # elif response.status_code == 401:
    #     assert response.json()['error'] == "Authentication Error"
    #     assert response.json()['details'] ==\
    #         "The provided credentials are invalid, check for spelling mistakes "+\
    #         "in your password or username, email address, or phone number."
    return response


#app key delete
def delete_app_key(app_key, data):
    """delete app key"""
    # SA
    data_SA = {
        "user_email": SUPER_USER,
        "password": SUPER_PASSWORD
    }
    response = login(data_SA)
    token =  response.json()['token']

    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+ token
        }
    response = client.get(f"{LOGOUT_URL}?application_key={app_key}",
        headers=headers)
    if response.status_code == 200:
        assert response.json()['message'] == "Key deleted Successfully"
    return response

#--------------------------------------------test starts--------------------------------------
