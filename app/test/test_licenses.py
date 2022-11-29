'''Test cases for licenses related APIs'''
from . import client, check_default_get
from . import assert_input_validation_error, assert_not_available_content
from .test_auth_basic import logout_user,login,SUPER_PASSWORD,SUPER_USER
from .conftest import initial_test_users
from schema.schemas import SourcePermissions

UNIT_URL = '/v2/licenses'
RESTORE_URL = '/v2/restore'
headers = {"contentType": "application/json", "accept": "application/json"}

headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "license" in item
    assert "name" in item
    assert "code" in item
    assert "permissions" in item
    assert isinstance(item['permissions'], list)
    assert "active" in item

def test_get():
    '''positive test case, without optional params'''
    check_default_get(UNIT_URL, headers,assert_positive_get)

    # '''positive test case, with one optional params, code and without registered user'''
    response = client.get(UNIT_URL+'?license_code=ISC')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'ISC'

    # '''positive test case, with one optional params, code with registered user header'''
    response = client.get(UNIT_URL+'?license_code=ISC',headers=headers_auth)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'ISC'

    # '''positive test case, with one optional params, code in lower case'''
    response = client.get(UNIT_URL+'?license_code=isc')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'ISC'

    # '''positive test case, with one optional params, name'''
    response = client.get(UNIT_URL+'?license_name=Creative%20Commons%20License')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'CC-BY-SA'

    # '''positive test case, with two optional params'''
    response = client.get(UNIT_URL+'?license_code=ISC&active=true')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['active']
    assert response.json()[0]['code'] == 'ISC'

    # ''' request a not available license, with code'''
    response = client.get(UNIT_URL+"?license_code=aaj")
    assert_not_available_content(response)

    # '''filter with permissions'''
    response = client.get(UNIT_URL+'?permission='+SourcePermissions.OPENACCESS.value)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # ''' request a not available license, with license name'''
    response = client.get(UNIT_URL+"?license_name=not-a-license")
    assert_not_available_content(response)

    # '''license code should not have spaces'''
    response = client.get(UNIT_URL+"?license_code=ISC%20II")
    assert_input_validation_error(response)

    # '''permissions should take only predefined values'''
    response = client.get(UNIT_URL+"?permission=abcd")
    assert_input_validation_error(response)

def test_post():
    '''positive test case, checking for correct return object'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser2']['token']
    data = {
      "license": "A very very long license text",
      "name": "Test License version 1",
      "code": "LIC-1",
      "permissions": [SourcePermissions.OPENACCESS.value]
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    #without Auth
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #With Auth
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "License uploaded successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "LIC-1"
    create_license = response

    # '''positive test case, checking for case conversion of code'''
    data["code"]= "lic-2"
    data['name']= "Test License version 2"

    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "License uploaded successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "LIC-2"

    # '''positive test case, checking without permissions'''
    data = {
        "code": "lic-3",
        "name": "Test License version 3",
        "license": "a long long long text"
    }
    #without auth
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "License uploaded successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["permissions"] == [SourcePermissions.OPENACCESS.value]

    # '''without mandatory fields'''
    #with auth
    data = {
        "code": "lic-4",
        "name": "Test License version 4",
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = {
        "code": "lic-4",
        "license": "Test License version 4",
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = {
        "license": "long long text",
        "name": "Test License version 4",
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # '''code should have letters numbers  . _ or - only'''
    data = {
      "license": "new-lang",
      "code": "AB@",
      "name": "new name"
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = {
      "license": "new-lang",
      "code": "AB 1",
      "name": "new name"
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # '''permissions should be from the pre-defined list'''
    data = {
      "license": "new- license text",
      "code": "MMM",
      "name": "new name",
      "permissions": ["regular"]
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)
    return(create_license)

def test_put():
    '''Add a new license and then alter it'''
    data = {
      "license": "A very very long license text",
      "code": "LIC-1",
      "name": "Test License version 1",
      "permissions": [SourcePermissions.OPENACCESS.value]
    }
    #without Auth
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #with auth
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "License uploaded successfully"

    update_data = {"code":"LIC-1", "permissions":
      [SourcePermissions.OPENACCESS.value, SourcePermissions.PUBLISHABLE.value]}
    #without auth update
    response = client.put(UNIT_URL, json=update_data, headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #with auth
    response = client.put(UNIT_URL, json=update_data, headers=headers_auth)
    assert response.status_code == 201
    assert response.json()['message'] == "License edited successfully"
    assert response.json()['data']['permissions'] ==\
      [SourcePermissions.OPENACCESS.value, SourcePermissions.PUBLISHABLE.value]

    update_data = {"code":"LIC-1", "name":"New name for test license"}
    response = client.put(UNIT_URL, json=update_data, headers=headers_auth)
    assert response.status_code == 201
    assert response.json()['message'] == "License edited successfully"
    assert response.json()['data']['name'] == "New name for test license"

    update_data = {"code":"LIC-1", "license":"A different text"}
    response = client.put(UNIT_URL, json=update_data, headers=headers_auth)
    assert response.status_code == 201
    assert response.json()['message'] == "License edited successfully"
    assert response.json()['data']['license'] == "A different text"

    headers_auth2 = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser']['token']
            }
    response = client.put(UNIT_URL, json=update_data, headers=headers_auth2)
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

    #try to edit with super admin
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }      
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']

    data = {
      "license": "license edited by admin",
      "code": "LIC-1",
      "name": "Test License version 1",
      "permissions": [SourcePermissions.OPENACCESS.value]
    }
    headers_admin = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
            }
    response = client.put(UNIT_URL, headers=headers_admin, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "License edited successfully"
    assert response.json()['data']['license'] == "license edited by admin"

    logout_user(token_admin)

    # unavailable code
    update_data['code'] = "LIC-2"
    response = client.put(UNIT_URL, json=update_data, headers=headers_auth)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"

    #without code
    update_data = {"name": "some name", "active":False}
    response = client.put(UNIT_URL, json=update_data, headers=headers_auth)
    assert_input_validation_error(response)

    #deactivate or soft-delete
    resp1 = client.get(UNIT_URL)
    assert resp1.status_code == 200
    assert len(resp1.json()) >= 3

    update_data = {"code": "LIC-1", "active":False}
    response = client.put(UNIT_URL, json=update_data, headers=headers_auth)
    assert response.status_code == 201

    resp2 = client.get(UNIT_URL)
    assert resp1.status_code == 200
    assert len(resp1.json()) - len(resp2.json()) == 1

def test_delete_default():
    ''' positive test case, checking for correct return of deleted license ID'''
    #create new data
    response = test_post()
    license_id = response.json()["data"]["licenseId"]
    res = client.get(UNIT_URL+'?license_code=LIC-1')

    data = {"itemId":license_id}

    #Delete without authentication
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Delete license with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev']:
        user_headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL, headers=user_headers, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete license with item created API User

    response = client.delete(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 200
    assert response.json()['message'] ==  \
        f"License with identity {license_id} deleted successfully"
    #Check license is deleted from licenses table
    check_license =client.get(UNIT_URL+'?license_code=LIC-1')
    assert_not_available_content(check_license)

def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted license ID'''
    #Created User or Super Admin can only delete license
    #creating data
    response = test_post()
    license_id = response.json()['data']['licenseId']
    data = {"itemId":license_id}

    #Delete license with Super Admin
     #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    #Delete license
    response = client.delete(UNIT_URL, headers=headers_sa, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == \
    f"License with identity {license_id} deleted successfully"
    logout_user(test_user_token)
    return response

def test_delete_license_id_string():
    '''positive test case, license id as string'''
    response = test_post()
    #Deleting created data
    license_id = response.json()['data']['licenseId']
    license_id = str(license_id)
    data = {"itemId":license_id}
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    response = client.delete(UNIT_URL, headers=headers_sa, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == \
        f"License with identity {license_id} deleted successfully"
    logout_user(test_user_token)

def test_delete_incorrectdatatype():
    '''negative testcase. Passing input data not in json format'''
    response = test_post()
    #Deleting created data
    license_id = response.json()['data']['licenseId']
    data = license_id
    response = client.delete(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_delete_missingvalue_license_id():
    '''Negative Testcase. Passing input data without licenseId'''
    data = {}
    response = client.delete(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_delete_notavailable_license():
    ''' request a non existing license ID, Ensure there is no partial matching'''
    data = {"itemId":20000}
    response = client.delete(UNIT_URL,headers=headers_auth,json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"

def test_restore_default():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring data
    #Restore without authentication
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore license with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev and APIUSer2
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev','APIUser2']:
        user_headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
    response = client.put(RESTORE_URL, headers=user_headers, json=data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

    #Restore license with Super Admin
    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    response = client.put(RESTORE_URL, headers=headers_sa, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleteditem_id} restored successfully"
    assert_positive_get(response.json()['data'])
    logout_user(test_user_token)
    #Check license is available in licenses table after restore
    check_license_code = client.get(UNIT_URL+"?icense_code=LIC-1")
    assert check_license_code.status_code == 200

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
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                     }

    response = client.put(RESTORE_URL, headers=headers_sa, json=data)
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
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                     }

    #Passing input data not in json format
    data = deleteditem_id

    response = client.put(RESTORE_URL, headers=headers_sa, json=data)
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
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                    }
    response = client.put(RESTORE_URL, headers=headers_sa, json=data)
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
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                    }
    response = client.put(RESTORE_URL, headers=headers_sa, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
