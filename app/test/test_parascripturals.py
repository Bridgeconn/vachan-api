'''Test cases for parascripturals related APIs'''
from . import client , contetapi_get_accessrule_checks_app_userroles
from . import check_default_get
from . import assert_input_validation_error, assert_not_available_content
from .test_versions import check_post as add_version
from .test_sources import check_post as add_source
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/sources/parascripturals/'
SOURCE_URL = '/v2/sources'
RESTORE_URL = '/v2/restore'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "parascriptId" in item
    assert isinstance(item['parascriptId'], int)
    assert "paratype" in item
    assert "title" in item

def check_post(data: list):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for parascriptural",
    }
    add_version(version_data)
    source_data = {
        "contentType": "parascriptural",
        "language": "ur",
        "version": "TTT",
        "year": 2020,
        "versionTag": 1
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    source = add_source(source_data)
    source_name = source.json()['data']['sourceName']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    #without auth
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    if response.status_code == 422:
        assert response.json()['error'] == 'Input Validation Error'
    else:
        assert response.status_code == 401
        assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    return response, source_name

def test_post_default():
    '''Positive test to upload parascriptural'''
    data = [
    	{'paratype':'Bible project video', 'title':"creation", "link":"http://somewhere.com/something"},
        {'paratype':'Bible project video', 'title':"abraham's family",
        "link":"http://somewhere.com/something"},
        {'paratype':'Bible Stories', 'title':"Isarel's travel routes",
        "link":"http://somewhere.com/something"},
        {'paratype':'Bible Stories', 'title':"the Gods reveals himself in new testament",
        "link":"http://somewhere.com/something"},
    ]
    response,source_name = check_post(data)
    assert response.status_code == 201
    assert response.json()['message'] == "Parascripturals added successfully"
    for item in response.json()['data']:
        assert_positive_get(item)
    assert len(data) == len(response.json()['data'])
    return response,source_name

def test_post_duplicate():
    '''Negative test to add two parascripturals Links with same type and title'''
    data = [
        {'paratype':'Bible Stories', 'title':"the Gods reveals himself in new testament",
        "link":"http://somewhere.com/new"}
    ]
    resp, source_name = check_post(data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Parascripturals added successfully"

    headers = {"contentType": "application/json", "accept": "application/json"}
    data[0]['link'] = 'http://anotherplace/item'
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    data = {'paratype':'Bible Stories', 'title':"the Geneology of Jesus Christ",
        "link":"http://somewhere.com/something"}
    resp, source_name = check_post(data)
    assert_input_validation_error(resp)

    # data object with missing mandatory fields
    headers = {"contentType": "application/json", "accept": "application/json"}
    data = [
        {'paratype':'Bible Stories',
        "link":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'title':"the Geneology of Jesus Christ",
        "link":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields
    data = [
        {'paratype':'mat', 'title':"the Geneology of Jesus Christ",
        "link":"not a url"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)


    data = [
        {'paratype':'Bible Stories', 'title':"the Geneology of Jesus Christ",
        "link":"noProtocol.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    source_name1 = source_name.replace('parascriptural', 'para')
    data = []
    response = client.post(UNIT_URL+source_name1, headers=headers_auth, json=data)
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '11')
    response = client.post(UNIT_URL+source_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_get_after_data_upload():
    '''Add some parascripturals data into the table and do all get tests'''
    data = [
        {'paratype':'Bible Stories', 'title':"creation",
        "link":"http://somewhere.com/something"},
        {'paratype':'Bible Stories', 'title':"Noah's Ark",
        "link":"http://somewhere.com/something"},
        {'paratype':'Bible Stories', 'title':"abraham's family",
        "link":"http://somewhere.com/something"},
        {'paratype':'Bible project video', 'title':"Isarel's travel routes",
        "link":"http://somewhere.com/something"},
        {'paratype':'Bible project video', 'title':"Paul's travel routes",
        "link":"http://somewhere.com/something"},
        {'paratype':'Bible project video', 'title':"the Gods reveals himself in new testament",
        "link":"http://somewhere.com/something"}
    ]
    res, source_name = check_post(data)
    assert res.status_code == 201
    # headers = {"contentType": "application/json", "accept": "application/json"}
    check_default_get(UNIT_URL+source_name, headers_auth,assert_positive_get)

    #filter by parascript type
    #without auth
    response = client.get(UNIT_URL+source_name+'?paratype=Bible%20Stories')
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"
    #with auth
    response = client.get(UNIT_URL+source_name+'?paratype=Bible%20Stories',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3

    # filter with title 
    response = client.get(UNIT_URL+source_name+'?title=creation',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # both title and book
    response = client.get(UNIT_URL+source_name+"?paratype=Bible%20Stories&title=Noah's%20Ark",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # not available
    response = client.get(UNIT_URL+source_name+'?paratype=Animations',headers=headers_auth)
    assert_not_available_content(response)

    response = client.get(UNIT_URL+source_name+'?paratype=Bible%20Stories&title=vision',headers=headers_auth)
    assert_not_available_content(response)

def test_get_incorrect_data():
    '''Check for input validations in get'''
    source_name = 'ur_TTT'
    response = client.get(UNIT_URL+source_name,headers=headers_auth)
    assert_input_validation_error(response)

    resp, source_name = check_post([])
    assert resp.status_code == 201
    source_name = source_name.replace('parascriptural', 'graphics')
    response = client.get(UNIT_URL+source_name, headers=headers_auth)
    assert response.status_code == 404

def test_put_after_upload():
    '''Positive tests for put'''
    data = [
        {'paratype':'Bible Stories', 'title':"12 apostles",
        "link":"http://somewhere.com/something"},
        {'paratype':'Bible Project Video', 'title':"miracles",
        "link":"http://somewhere.com/something"}
    ]
    response, source_name = check_post(data)
    assert response.status_code == 201

    # positive PUT
    new_data = [
        {'paratype':'Bible Stories', 'title':"12 apostles",
        "link":"http://anotherplace.com/something"},
        {'paratype':'Bible Project Video', 'title':"miracles",
        "link":"http://somewhereelse.com/something"}
    ]
    # headers = {"contentType": "application/json", "accept": "application/json"}
    #without auth
    response = client.put(UNIT_URL+source_name,headers=headers, json=new_data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Parascripturals updated successfully'
    for i,item in enumerate(response.json()['data']):
        assert_positive_get(item)
        assert response.json()['data'][i]['link'] == new_data[i]['link']
        assert response.json()['data'][i]['paratype'] == data[i]['paratype']
        assert response.json()['data'][i]['title'] == data[i]['title']

    # not available PUT
    new_data[0]['paratype'] = 'Bible Stories New'
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=new_data)
    assert response.status_code == 404

    source_name = source_name.replace('1', '10')
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''

    post_data = [
        {'paratype':'Bible Stories', 'title':"miracles",
        "link":"http://somewhere.com/something"},
        {'paratype':'Bible project video', 'title':"12 apostles",
        "link":"http://somewhere.com/something"}
    ]
    resp, source_name = check_post(post_data)
    assert resp.status_code == 201

    # single data object instead of list
    headers = {"contentType": "application/json", "accept": "application/json"}
    data =  {'paratype':'Bible Stories', 'title':"12 apostles",
        "link":"http://anotherplace.com/something"}
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # data object with missing mandatory fields
    data = [
        {'title':"12 apostles",
        "link":"http://anotherplace.com/something"}
            ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'paratype':'Bible Stories',
        "link":"http://somewhere.com/something"}    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields

    data = [
        {'paratype':'Bible Stories', 'title':"12 apostles",
        "link":"filename.txt"}    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    source_name1 = source_name.replace('parascriptural', 'graphics')
    response = client.put(UNIT_URL+source_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '10')
    response = client.put(UNIT_URL+source_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_created_user_can_only_edit():
    """only created user and SA can only edit"""
    SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    #creating one data with Super Admin and try to edit with VachanAdmin
    response = login(SA_user_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth['Authorization'] = "Bearer"+" "+test_user_token

    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "parascriptural",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    #create source
    response = client.post('/v2/sources', headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"
    source_name = response.json()['data']['sourceName']
    
    #create parascripturals
    data = [
        {'paratype':'Bible Stories', 'title':"12 apostles",
        "link":"http://somewhere.com/something"},
        {'paratype':'Bible project video', 'title':"miracles",
        "link":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert response.status_code == 201

    #update parascripturals with created SA user
    new_data = [
        {'paratype':'Bible Stories', 'title':"12 apostles",
        "link":"http://anotherplace.com/something"},
        {'paratype':'Bible project video', 'title':"miracles",
        "link":"http://somewhereelse.com/something"}]
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Parascripturals updated successfully'

    #update with VA not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'  

def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    data = [
    	{'paratype':'Bible Stories', 'title':"12 apostles",
        "link":"http://somewhere.com/something"}
    ]
    contetapi_get_accessrule_checks_app_userroles("parascriptural",UNIT_URL,data)

def test_delete_default():
    ''' positive test case, checking for correct return of deleted parascriptural ID'''
    #create new data
    response,source_name = test_post_default()
    print("source:",source_name)
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    post_response = client.get(UNIT_URL+source_name+"?book_code=Bible%20project%20video&title=creation",\
        headers=headers_auth)
    assert post_response.status_code == 200
    assert len(post_response.json()) == 1
    for item in post_response.json():
        assert_positive_get(item)
    parascript_response = client.get(UNIT_URL+source_name,headers=headers_auth)
    parascript_id = parascript_response.json()[0]['parascriptId']
    print("parasciptid:",parascript_id)

    #Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    response = client.delete(UNIT_URL+source_name + "?delete_id=" + str(parascript_id), headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

     #Delete parascriptural with other API user,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev']:
        headers_au = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL+source_name + "?delete_id=" + str(parascript_id), headers=headers_au)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete parascriptural with Vachan Admin
    headers_va = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['VachanAdmin']['token']
            }
    response = client.delete(UNIT_URL+source_name + "?delete_id=" + str(parascript_id), headers=headers_va)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Parascriptural id {parascript_id} deleted successfully"

   
def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted parascriptural ID'''
    #Created User or Super Admin can only delete parascriptural
    #creating data
    response,source_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    parascript_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    parascript_id = parascript_response.json()[0]['parascriptId']


     #Delete parascriptural with Super Admin
    response = client.delete(UNIT_URL+source_name + "?delete_id=" + str(parascript_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Parascriptural id {parascript_id} deleted successfully"
    #Check parascriptural is deleted from table
    parascript_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    post_response = client.get(UNIT_URL+source_name+"?book_code=Bible%20project%20video&title=creation",\
        headers=headers_sa)
    assert_not_available_content(post_response)
    logout_user(test_user_token)
    return response,source_name

def test_delete_parascript_id_string():
    '''positive test case, parascriptural id as string'''
    response,source_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    parascript_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    parascript_id = parascript_response.json()[0]['parascriptId']
    parascript_id = str(parascript_id)

    #Delete parascriptural with Super Admin
    response = client.delete(UNIT_URL+source_name + "?delete_id=" + str(parascript_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Parascriptural id {parascript_id} deleted successfully"
    #Check parascriptural parascriptural is deleted from table
    parascript_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    logout_user(test_user_token)


def test_delete_missingvalue_parascript_id():
    '''Negative Testcase. Passing input data without parascriptId'''
    response,source_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    response = client.delete(UNIT_URL+source_name + "?delete_id=", headers=headers_sa)
    assert_input_validation_error(response)
    logout_user(test_user_token)

def test_delete_missingvalue_source_name():
    '''Negative Testcase. Passing input data without sourceName'''
    response,source_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    parascript_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    parascript_id = parascript_response.json()[0]['parascriptId']
    
    response = client.delete(UNIT_URL+ "?delete_id=" + str(parascript_id), headers=headers_sa)
    assert response.status_code == 404
    logout_user(test_user_token)

def test_delete_notavailable_content():
    ''' request a non existing parascriptural ID, Ensure there is no partial matching'''
    response,source_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    parascript_id=20000
     #Delete parascriptural with Super Admin
    response = client.delete(UNIT_URL+source_name + "?delete_id=" + str(parascript_id), headers=headers_sa)
    print("del resp:",response.json())
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    logout_user(test_user_token)

def test_restore_default():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response,source_name = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}
    #Restoring data
    #Restore without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'


    #Restore content with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev']:
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
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleteditem_id} restored successfully"
    #Check Infpgraphic exists after restore
    restore_response =  client.get(UNIT_URL+source_name+"?paratype=Bible project video&title=creation",\
        headers=headers_auth)
    assert restore_response.status_code == 200
    assert len(restore_response.json()) == 1
    for item in restore_response.json():
        assert_positive_get(item)
    logout_user(test_user_token)

def test_restore_item_id_string():
    '''positive test case, passing deleted item id as string'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response = test_delete_default_superadmin()[0]
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
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
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
    response = test_delete_default_superadmin()[0]
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
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
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
    data = {"itemId":9999}
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

def test_restoreitem_with_notavailable_source():
    ''' Negative test case.request to restore an item whoose source is not available'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response,source_name = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}
    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    #Delete Associated Source
    get_source_response = client.get(SOURCE_URL + "?source_name="+source_name, headers=headers_auth)
    source_id = get_source_response.json()[0]["sourceId"]
    response = client.delete(SOURCE_URL + "?delete_id=" + str(source_id), headers=headers_auth)
    assert response.status_code == 200
    #Restoring data
    #Restore content with Super Admin after deleting source
    restore_response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    restore_response.status_code = 404
    logout_user(test_user_token)
