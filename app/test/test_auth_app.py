"""Basic test cases of features Register, Login, Logout, Role assignment"""
import json
import os
import pytest
from urllib.parse import quote

from app.schema import schema_auth
from . import assert_input_validation_error, client, check_skip, check_limit, TEST_APPS_LIST, TEST_ROLE_LIST
from .conftest import initial_test_users

LOGIN_URL = '/v2/app/key'
REGISTER_URL = '/v2/app/register'
LOGOUT_URL = '/v2/app/delete-key'
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

#login check
# def login(data):
#     '''test for login feature'''
#     #headers = {"contentType": "application/json", "accept": "application/json"}
#     params = f"?user_email={quote(data['user_email'])}&password={quote(data['password'])}"
#     response = client.get(LOGIN_URL+params)
#     if response.status_code == 200:
#         assert response.json()['message'] == "Login Succesfull"
#         token =  response.json()['token']
#         assert len(token) == 32
#         assert "userId" in response.json()
#     elif response.status_code == 401:
#         assert response.json()['error'] == "Authentication Error"
#         assert response.json()['details'] ==\
#             "The provided credentials are invalid, check for spelling mistakes "+\
#             "in your password or username, email address, or phone number."
#     return response


#app key delete
def delete_app_key(app_key):
    """delete app key"""
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+ initial_test_users["VachanAdmin"]["token"]
            }
    response = client.get(f"{LOGOUT_URL}?app_key={app_key}",headers=headers)
    return response

#--------------------------------------------test starts--------------------------------------
