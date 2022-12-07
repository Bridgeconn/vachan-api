'''Test cases for contentType related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_auth_basic import SUPER_USER,SUPER_PASSWORD, login, logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/contents'
RESTORE_URL = '/v2/restore'
VERSION_URL = '/v2/versions'
SOURCE_URL = '/v2/sources'

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "contentId" in item
    assert isinstance(item['contentId'], int)
    assert "contentType" in item

def test_get_default():
    '''positive test case, without optional params'''
    headers = {"contentType": "application/json", "accept": "application/json"}
    check_default_get(UNIT_URL, headers ,assert_positive_get)

def test_get_notavailable_content_type():
    ''' request a not available content, Ensure there is not partial matching'''
    response = client.get(UNIT_URL+"?content_type=bib")
    assert_not_available_content(response)

    #test get not avaialble content with auth header
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.get(UNIT_URL+"?content_type=bib",headers=headers_auth)
    assert_not_available_content(response)

def test_post_default():
    '''positive test case, checking for correct return object'''
    data = {"contentType":"altbible"}
    #Registered user can only add content type
    #Add test without login
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Add content with auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Content type created successfully"
    assert_positive_get(response.json()['data'])
    return response

def test_post_incorrectdatatype1():
    '''the input data object should a json with "contentType" key within it'''
    data = "bible"
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)


def test_post_incorrectdatatype2():
    '''contentType should not be integer, as per the Database datatype constarints'''
    data = {"contentType":75}
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_missingvalue_contenttype():
    '''contentType is mandatory in input data object'''
    data = {}
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_incorrectvalue_contenttype():
    ''' The contentType name should not contain spaces,
    as this name would be used for creating tables'''
    data = {"contentType":"Bible Contents"}
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_delete_default():
    ''' positive test case, checking for correct return of deleted content ID'''
    #create new data
    response = test_post_default()
    content_id = response.json()["data"]["contentId"]

    data = {"itemId":content_id}

    #Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Delete content with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev']:
        headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL, headers=headers, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete content with item created API User

    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }

    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 200
    assert response.json()['message'] ==  \
        f"Content with identity {content_id} deleted successfully"
    #Check content is deleted from content_types table
    check_content_type = client.get(UNIT_URL+"?content_type=altbible")
    assert_not_available_content(check_content_type)

def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted content ID'''
    #Created User or Super Admin can only delete content
    #creating data
    response = test_post_default()
    content_id = response.json()['data']['contentId']
    data = {"itemId":content_id}

    #Delete content with Super Admin
     #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    #Delete content
    response = client.delete(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == \
    f"Content with identity {content_id} deleted successfully"
    logout_user(test_user_token)
    return response

def test_delete_content_id_string():
    '''positive test case, content id as string'''
    response = test_post_default()
    #Deleting created data
    content_id = response.json()['data']['contentId']
    content_id = str(content_id)
    data = {"itemId":content_id}
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    response = client.delete(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == \
        f"Content with identity {content_id} deleted successfully"
    logout_user(test_user_token)

def test_delete_incorrectdatatype():
    '''negative testcase. Passing input data not in json format'''
    response = test_post_default()
    #Deleting created data
    content_id = response.json()['data']['contentId']
    data = content_id
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_delete_missingvalue_content_id():
    '''Negative Testcase. Passing input data without contentId'''
    data = {}
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_delete_notavailable_content():
    ''' request a non existing content ID, Ensure there is no partial matching'''
    data = {"itemId":20000}
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL,headers=headers,json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"

def test_content_used_by_source():
    '''  Negativetest case, trying to delete that content which is used to create a source'''

    #get id of an already existing content
    response = client.get(UNIT_URL+"?content_type=commentary")
    content_id = response.json()[0]["contentId"]

    #create new source as SuperAdmin
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                     }
    #Create Version with associated with source
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "Test Version",
        "revision": 1,
        "metaData": {
            "publishedIn": "1611"
            }
        }
    response = client.post(VERSION_URL, headers=headers_auth, json=version_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Version created successfully"

    source_data = {
        "contentType": "commentary",
        "language": "en",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "ISC"
    }
    #Create Source with content
    response = client.post(SOURCE_URL, headers=headers_auth, json=source_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"
    logout_user(token_admin)

    #Delete content
    data = {"itemId":content_id}
    response = client.delete(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == 'Conflict'


def test_restore_default():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring data
    #Restore without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore content with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev and APIUSer2
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev','APIUser2']:
        headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

    #Restore content with Super Admin
    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleteditem_id} restored successfully"
    assert_positive_get(response.json()['data'])
    logout_user(test_user_token)
    #Check content is available in content_types table after restore
    check_content_type = client.get(UNIT_URL+"?content_type=altbibile")
    assert check_content_type.status_code == 200

def test_restore_item_id_string():
    '''positive test case, passing deleted item id as string'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring string data
    deleteditem_id = str(deleteditem_id)
    data = {"itemId": deleteditem_id}

#Login as Super Admin
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                     }

    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleteditem_id} restored successfully"
    logout_user(token_admin)

def test_restore_incorrectdatatype():
    '''Negative Test Case. Passing input data not in json format'''
    #Creating and Deleting data
    response = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Login as Super Admin
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                     }

    #Passing input data not in json format
    data = deleteditem_id

    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)
    logout_user(token_admin)

def test_restore_missingvalue_itemid():
    '''itemId is mandatory in input data object'''
    data = {}
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']
    headers_admin = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                    }
    response = client.put(RESTORE_URL, headers=headers_admin, json=data)
    assert_input_validation_error(response)
    logout_user(token_admin)

def test_restore_notavailable_item():
    ''' request a non existing restore ID, Ensure there is no partial matching'''
    data = {"itemId":20000}
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']
    headers_admin = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                    }
    response = client.put(RESTORE_URL, headers=headers_admin, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
