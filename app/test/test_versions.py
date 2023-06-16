'''Test cases for versions related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
#from .test_sources import check_post as add_source
from .test_auth_basic import login,SUPER_USER,SUPER_PASSWORD,logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/versions'
RESTORE_URL = '/v2/restore'
SOURCE_URL = '/v2/sources'

headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "versionId" in item
    assert isinstance(item['versionId'], int)
    assert "versionAbbreviation" in item
    assert "versionName" in item
    assert "versionTag" in item
    assert "metaData" in item

def check_post(data):
    '''common steps for positive post test cases'''
    #without Auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #with Auth
    headers_auth = {"contentType": "application/json", #pylint: disable=redefined-outer-name
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Version created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["versionAbbreviation"] == data['versionAbbreviation']
    return response

def test_post_default():
    '''Positive test to add a new version'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "versionTag": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    create_version = check_post(data)
    return create_version

def test_post_multiple_with_same_abbr():
    '''Positive test to add two version, with same abbr and diff versionTag'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "versionTag": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    check_post(data)
    data["versionTag"] = 2
    check_post(data)

def test_post_multiple_with_same_abbr_negative():
    '''Negative test to add two version, with same abbr and versionTag'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "versionTag": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    check_post(data)
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

def test_version_tag():
    '''version tag support a flexible pattern. Ensure its different forms are supported'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test"
    }

    # No versionTag
    response = check_post(data)
    assert response.json()['data']['versionTag'] == "1"

    # One digit versionTag
    data['versionTag'] = "2"
    response = check_post(data)
    assert response.json()['data']['versionTag'] == "2"

    # Dot separated numbers and varying number of parts
    data['versionTag'] = "2.0.1"
    response = check_post(data)
    assert response.json()['data']['versionTag'] == "2.0.1"

    # with string parts
    data['versionTag'] = "2.0.1.aplha.1"
    response = check_post(data)
    assert response.json()['data']['versionTag'] == "2.0.1.aplha.1"

    # get
    response = client.get(UNIT_URL+"?version_abbreviation=XYZ")
    assert response.status_code == 200
    response = response.json()
    assert len(response) == 4
    assert response[0]['versionTag'] == '1'
    assert response[1]['versionTag'] == '2'
    assert response[2]['versionTag'] == '2.0.1'
    assert response[3]['versionTag'] == "2.0.1.aplha.1"


def test_post_without_versionTag():
    '''versionTag field should have a default value, even not provided'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = check_post(data)
    assert response.json()['data']['versionTag'] == "1"

def test_post_without_metadata():
    '''metadata field is not mandatory'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "versionTag": "3"
    }
    response = check_post(data)
    assert response.json()['data']['metaData'] is None

def test_post_without_abbr():
    '''versionAbbreviation is mandatory'''
    data = {
        "versionName": "Xyz version to test",
        "versionTag": "1",
        "metaData": {"owner": "some", "access-key": "123xyz"}
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_post_wrong_abbr():
    '''versionAbbreviation cannot have space, dot etc'''
    data = {
        "versionAbbreviation": "XY Z",
        "versionName": "Xyz version to test",
        "versionTag": "1",
        "metaData": {"owner": "one", "access-key": "123xyz"}
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data['versionAbbreviation'] = 'X.Y'
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_post_wrong_versionTag():
    '''versionTag cannot have space, comma letters etc'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "versionTag": "1,0",
        "metaData": {"owner": "another one", "access-key": "123xyz"}
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data['versionTag'] = "1 2"
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data['versionTag'] = '1@a'
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_post_without_name():
    '''versionName is mandatory'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionTag": "1",
        "metaData": {"owner": "no one", "access-key": "123xyz"}
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_get():
    '''Test get before adding data to table. Usually run on new test DB on local or github.
    If the testing is done on a DB that already has data(staging), the response wont be empty.'''
    response = client.get(UNIT_URL)
    if len(response.json()) == 0:
        assert_not_available_content(response)


def test_get_wrong_abbr():
    '''abbreviation with space, number'''
    response = client.get(UNIT_URL+'?version_abbreviation=A%20A')
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+'?version_abbreviation=123')
    assert_input_validation_error(response)

def test_get_wrong_versionTag():
    '''versionTag as text'''
    response = client.get(UNIT_URL+'?version_abbreviation=A%20A')
    assert_input_validation_error(response)

def test_get_after_adding_data():
    '''Add some data to versions table and test get method'''
    data = {
        'versionAbbreviation': "AAA",
        'versionName': 'test name A',
        'versionTag': 1
    }
    check_post(data)
    data['versionTag'] = 2
    check_post(data)
    data = {
        'versionAbbreviation': "BBB",
        'versionName': 'test name B',
        'versionTag': 1
    }
    check_post(data)
    data['versionTag'] = 2
    check_post(data)
    headers = {"contentType": "application/json", "accept": "application/json"}
    check_default_get(UNIT_URL, headers,assert_positive_get)

    # filter with abbr
    response = client.get(UNIT_URL + '?version_abbreviation=AAA')
    assert response.status_code == 200
    assert len(response.json()) == 2
    for item in response.json():
        assert_positive_get(item)
        assert item['versionAbbreviation'] == 'AAA'

    # filter with abbr with registered user
    response = client.get(UNIT_URL + '?version_abbreviation=AAA',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    for item in response.json():
        assert_positive_get(item)
        assert item['versionAbbreviation'] == 'AAA'

    # filter with abbr, for not available content
    response = client.get(UNIT_URL + '?version_abbreviation=CCC')
    assert_not_available_content(response)

    # filter with name
    response = client.get(UNIT_URL + '?version_name=test%20name%20B')
    assert response.status_code == 200
    assert len(response.json()) == 2
    for item in response.json():
        assert_positive_get(item)
        assert item['versionName'] == 'test name B'

   # filter with abbr and versionTag
    response = client.get(UNIT_URL + '?version_abbreviation=AAA&version_tag=2')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['versionAbbreviation'] == 'AAA'
    assert response.json()[0]['versionTag'] == "2"

    data = {
        'versionAbbreviation': "CCC",
        'versionName': 'test name C',
        'metaData': {'owner': 'myself'}
    }
    check_post(data)

    # filter with metaData and default value for metadata
    response = client.get(UNIT_URL + '?metadata={"owner":"myself"}')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['versionAbbreviation'] == 'CCC'
    assert response.json()[0]['versionTag'] == "1"
    assert response.json()[0]['metaData']['owner'] == 'myself'

def test_put_version():
    """test default put for versions with auth check"""
    #create version with auth
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "versionTag": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    headers_auth = {"contentType": "application/json", #pylint: disable=redefined-outer-name
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    version_id = response.json()['data']['versionId']

    #edit with same user created
    data = {
        "versionId": version_id,
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test edited",
        "versionTag": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = client.put(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Version edited successfully"
    assert response.json()["data"]["versionName"] == "Xyz version to test edited"

    headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser']['token']
            }
    response = client.put(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

    #edit with super user
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']

    data = {
        "versionId": version_id,
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version edited by admin",
        "versionTag": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    headers_admin = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
            }
    response = client.put(UNIT_URL, headers=headers_admin, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Version edited successfully"
    assert response.json()["data"]["versionName"] == "Xyz version edited by admin"
    logout_user(token_admin)

def test_delete_default():
    ''' positive test case, checking for correct return of deleted version ID'''
    #create new data
    response = test_post_default()
    version_id = response.json()["data"]["versionId"]

    data = {"itemId":version_id}

    #Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}
    response =client.request("delete" ,UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Delete version with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev']:
        user_headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response =client.request("delete" ,UNIT_URL, headers=user_headers, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete version with item created API User
    headers_au = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.request("delete" ,UNIT_URL, headers=headers_au, json=data)
    assert response.status_code == 200
    assert response.json()['message'] ==  \
        f"Version with identity {version_id} deleted successfully"
    #Check version is deleted from versions table
    check_version =client.get(UNIT_URL+'?version_abbreviation=XYZ')
    assert_not_available_content(check_version)

def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted version ID'''
    #Created User or Super Admin can only delete version
    #creating data
    response = test_post_default()
    version_id = response.json()['data']['versionId']
    data = {"itemId":version_id}

    #Delete version with Super Admin
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

    #Delete verison
    response =client.request("delete" ,UNIT_URL, headers=headers_sa, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == \
    f"Version with identity {version_id} deleted successfully"
    logout_user(test_user_token)
    return response

def test_delete_version_id_string():
    '''positive test case, version id as string'''
    response = test_post_default()
    #Deleting created data
    version_id = response.json()['data']['versionId']
    version_id = str(version_id)
    data = {"itemId":version_id}
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
    response = client.request("delete" ,UNIT_URL, headers=headers_sa, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == \
        f"Version with identity {version_id} deleted successfully"
    logout_user(test_user_token)

def test_delete_incorrectdatatype():
    '''negative testcase. Passing input data not in json format'''
    response = test_post_default()

    #Deleting created data
    version_id = response.json()['data']['versionId']
    data = version_id
    response = client.request("delete" ,UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_delete_missingvalue_version_id():
    '''Negative Testcase. Passing input data without version Id'''
    data = {}
    response = client.request("delete" ,UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_delete_notavailable_version():
    ''' request a non existing version ID, Ensure there is no partial matching'''
    data = {"itemId":20000}
    response = client.request("delete" ,UNIT_URL,headers=headers_auth,json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"

def test_version_used_by_source():
    '''  Negativetest case, trying to delete that version which is used to create a source'''

    #Create Version with associated with source
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for versions",
    }
    check_post(version_data)

    #Create Source with license
    source_data = {
        "contentType": "commentary",
        "language": "en",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    # add_source()
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
    response = client.post(SOURCE_URL, headers=headers_admin, json=source_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"

    #Delete version
    version_response = client.get(UNIT_URL+'?version_abbreviation=TTT')
    version_id = version_response.json()[0]['versionId']
    data = {"itemId":version_id}
    response = client.request("delete" ,UNIT_URL, headers=headers_admin, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == 'Conflict'
    logout_user(token_admin)

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

    #Restore version with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev and APIUSer2
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev','APIUser2']:
        user_headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.put(RESTORE_URL, headers=user_headers, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Restore version with Super Admin
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
    #Check version is available in versions table after restore
    check_version_abbr = client.get(UNIT_URL+'?version_abbreviation=XYZ')
    assert check_version_abbr.status_code == 200

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
