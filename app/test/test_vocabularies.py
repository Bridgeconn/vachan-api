'''Test cases for vocabulary related APIs'''
from . import client , resourcetypeapi_get_accessrule_checks_app_userroles
from . import assert_input_validation_error, assert_not_available_content

from . import check_default_get, check_soft_delete
from .test_versions import check_post as add_version
from .test_resources import check_post as add_resource
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/resources/vocabularies/'
RESOURCE_URL = '/v2/resources'
RESTORE_URL = '/v2/admin/restore'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "word" in item
    assert "details" in item
    if item['details'] is not None:
        assert isinstance(item["details"], dict)

def check_post(data: list):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for vocabularies",
    }
    add_version(version_data)
    resource_data = {
        "resourceType": "vocabulary",
        "language": "en",
        "version": "TTT",
        "revision": 1,
        "year": 2000
    }
    resource = add_resource(resource_data)
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    resource_name = resource.json()['data']['resourceName']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    #without auth
    response = client.post(UNIT_URL+resource_name, headers=headers, json=data)
    if response.status_code == 422:
        assert response.json()['error'] == 'Input Validation Error'
    else:
        assert response.status_code == 401
        assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    return response, resource_name

def test_post_default():
    '''Positive test to upload vocabulary words'''
    data = [
    	{"word": "one", "details":{"digit": 1, "type":"odd"}},
    	{"word": "two", "details":{"digit": 2, "type":"even"}},
    	{"word": "three", "details":{"digit": 3, "type":"odd"}},
    	{"word": "four", "details":{"digit": 4, "type":"even"}},
    	{"word": "five", "details":{"digit": 5, "type":"odd"}}
    ]
    response,resource_name = check_post(data)
    assert response.status_code == 201
    assert response.json()['message'] == "Vocabulary words added successfully"
    assert len(data) == len(response.json()['data'])
    for item in response.json()['data']:
        assert_positive_get(item)
    return response,resource_name


def test_post_duplicate():
    '''Negative test to add two entires with same word'''
    data = [
    	{"word": "one", "details":{"digit": 1, "type":"odd"}}
    ]
    resp, resource_name = check_post(data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Vocabulary words added successfully"

    # headers = {"contentType": "application/json", "accept": "application/json"}
    data[0]['details'] = {"digit": 1, "type":"natural number"}
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    data = {"word": "one", "details":{"digit": 1, "type":"odd"}}
    # (this step creates version and resource that can be used in other tests in this function)
    resp, resource_name = check_post(data)
    assert_input_validation_error(resp)

    # data object with missing mandatory fields
    # headers = {"contentType": "application/json", "accept": "application/json"}
    data = [
    	{"details":{"digit": 1, "type":"odd"}}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data value for details
    data = [
    	{"details":'"digit"= 1, "type"="odd"'}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

 	# wrong resource name
    resource_name1 = resource_name.replace('vocabulary', 'bible')
    response = client.post(UNIT_URL+resource_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    resource_name2 = resource_name.replace('1', '3')
    response = client.post(UNIT_URL+resource_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_get_after_data_upload():
    '''Add some data into the table and do all get tests'''
    data = [
    	{"word": "one", "details":{"digit": 1, "type":"odd", "link":UNIT_URL+'vocabulary?word=one'}},
    	{"word": "two", "details":{"digit": 2, "type":"even", "link":UNIT_URL+'vocabulary?word=two'}},
    	{"word": "three", "details":{"digit": 3, "type":"odd",
    	"link":UNIT_URL+'vocabulary?word=three'}},
    	{"word": "four", "details":{"digit": 4, "type":"even",
    	"link":UNIT_URL+'vocabulary?word=four'}},
    	{"word": "five", "details":{"digit": 5, "type":"odd", "link":UNIT_URL+'vocabulary?word=five'}},
        {"word": "another", "details":{"empty-field": ""}}
    ]
    resp, resource_name = check_post(data)
    assert resp.status_code == 201
    # headers = {"contentType": "application/json", "accept": "application/json"}
    check_default_get(UNIT_URL+resource_name, headers_auth ,assert_positive_get)

    # search with first letter
    #without auth
    response = client.get(UNIT_URL+resource_name+'?search_word=f')
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"
    #with auth
    response = client.get(UNIT_URL+resource_name+'?search_word=f',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # search with starting two letters
    response = client.get(UNIT_URL+resource_name+'?search_word=fi',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # search for not available
    response = client.get(UNIT_URL+resource_name+'?search_word=ten',headers=headers_auth)
    assert_not_available_content(response)

    # full word match
    response = client.get(UNIT_URL+resource_name+'?search_word=two&exact_match=True',\
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['word'] == 'two'

    # with only words flag
    response = client.get(UNIT_URL+resource_name+'?word_list_only=True',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 6
    for item in response.json():
        assert "details" not in item

    # with details
    response = client.get(UNIT_URL+resource_name+'?details={"type":"odd"}',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3
    for item in response.json():
        assert item['details']['type'] == "odd"

    response = client.get(UNIT_URL+resource_name+'?details={"type":"even"}',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    for item in response.json():
        assert item['details']['type'] == "even"

   # search details having empty value
    response = client.get(UNIT_URL+resource_name+'?details={"empty-field":""}',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    for item in response.json():
        assert item['details']['empty-field'] == ""

    # search word from details
    response = client.get(UNIT_URL+resource_name+'?search_word=odd',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3
    for item in response.json():
        assert item['details']['type'] == "odd"


def test_get_incorrect_data():
    '''Check for input validations in get'''

    resource_name = 'en_TTT'
    response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+resource_name+'?details="test"',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+resource_name+'?details=None',headers=headers_auth)
    assert_input_validation_error(response)

    resp, resource_name = check_post([])
    assert resp.status_code == 201
    resource_name = resource_name.replace('vocabulary', 'bible')
    response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert response.status_code in [415, 404]# included 415
    #due to https://github.com/Bridgeconn/vachan-api/issues/302

def test_put_after_upload():
    '''Tests for put'''
    data = [
    	{"word": "Adam", "details": {"description": "Frist man"}},
    	{"word": "Eve", "details": {"description": "Wife of Adam"}}
    ]
    response, resource_name = check_post(data)
    assert response.status_code == 201

    # positive PUT
    new_data = [
    	{"word": "Adam", "details": {"description": "Frist man God created"}},
    	{"word": "Eve", "details": {"description": "Wife of Adam, and Mother of mankind"}}
    ]
    # headers = {"contentType": "application/json", "accept": "application/json"}
    #without auth
    response = client.put(UNIT_URL+resource_name,headers=headers, json=new_data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #with auth
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Vocabulary words updated successfully'
    for i,item in enumerate(response.json()['data']):
        assert_positive_get(item)
        assert response.json()['data'][i]['details'] == new_data[i]['details']

    # not available PUT
    new_data = [
    	{"word": "Moses", "details": {"description": "Leader of Isreal"}}
    ]
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 404

    resource_name = resource_name.replace('1', '5')
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=[])
    assert response.status_code == 404

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''

    # to create necessary versions and resource
    resp, resource_name = check_post([])
    assert resp.status_code == 201


    # single data object instead of list
    headers = {"contentType": "application/json", "accept": "application/json"} #pylint: disable=redefined-outer-name disable=unused-variable
    data = {"word": "one", "details":{"digit": 1, "type":"odd"}}
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # data object with missing mandatory fields
    data = [
    	{"details":{"digit": 1, "type":"odd"}}
    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data value for details
    data = [
    	{"details":'"digit"= 1, "type"="odd"'}
    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

 	# wrong resource name
    resource_name1 = resource_name.replace('vocabulary', 'bible')
    response = client.put(UNIT_URL+resource_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    resource_name2 = resource_name.replace('1', '3')
    response = client.put(UNIT_URL+resource_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_soft_delete():
    '''check soft delete in vocabularies'''
    data = [
        {'word':'Good', 'details':{'meaning':'good', 'form':'Positive'}},
        {'word':'Better', 'details':{'meaning':'good', 'form':'Comparative'}},
        {'word':'Best', 'details':{'meaning':'good', 'form':'Superlative'}},
        {'word':'Nice', 'details':{'meaning':'nice', 'form':'Positive'}},
        {'word':'Nicer', 'details':{'meaning':'good', 'form':'Comparative'}},
        {'word':'Nicest', 'details':{'meaning':'good', 'form':'Superlative'}},
        {'word':'Warm', 'details':{'meaning':'warm', 'form':'Positive'}}
    ]

    delete_data = [
        {'word': "Good"}, {'word': "Nice"}, {"word":"Warm"}
    ]
    check_soft_delete(UNIT_URL, check_post, data, delete_data, headers_auth)

def test_created_user_can_only_edit():
    """only created user and SA can only edit"""
    sa_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    #creating one data with Super Admin and try to edit with VachanAdmin
    response = login(sa_user_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth['Authorization'] = "Bearer"+" "+test_user_token

    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for vocabularies",
    }
    add_version(version_data)
    resource_data = {
        "resourceType": "vocabulary",
        "language": "en",
        "version": "TTT",
        "versionTag": 1,
        "year": 2000
    }
    #create resource
    response = client.post('/v2/resources', headers=headers_auth, json=resource_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource created successfully"
    resource_name = response.json()['data']['resourceName']

    #create vocabulary
    data = [
    	{"word": "Adam", "details": {"description": "Frist man"}},
    	{"word": "Eve", "details": {"description": "Wife of Adam"}}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Vocabulary words added successfully'

    #update vocabulary with created SA user
    new_data = [
    	{"word": "Adam", "details": {"description": "Frist man God created"}},
    	{"word": "Eve", "details": {"description": "Wife of Adam, and Mother of mankind"}}
    ]
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Vocabulary words updated successfully'

    #update with VA not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    data = [
    	{"word": "one", "details":{"digit": 1, "type":"odd", "link":UNIT_URL+'vocabulary?word=one'}}
    ]
    resourcetypeapi_get_accessrule_checks_app_userroles("vocabulary",UNIT_URL,data)

def test_get_count_after_data_upload():
    '''Add some data into the table and do all tests on get count API'''
    data = [
        {"word": "one", "details":{"digit": 1, "type":"odd", "link":UNIT_URL+'vocabulary?word=one'}},
        {"word": "two", "details":{"digit": 2, "type":"even", "link":UNIT_URL+'vocabulary?word=two'}},
        {"word": "three", "details":{"digit": 3, "type":"odd",
        "link":UNIT_URL+'vocabulary?word=three'}},
        {"word": "four", "details":{"digit": 4, "type":"even",
        "link":UNIT_URL+'vocabulary?word=four'}},
        {"word": "five", "details":{"digit": 5, "type":"odd", "link":UNIT_URL+'vocabulary?word=five'}},
        {"word": "another", "details":{"empty-field": ""}},
        {"word": "inactive", "active": "false"}
    ]
    resp, resource_name = check_post(data)
    assert resp.status_code == 201
    # headers = {"contentType": "application/json", "accept": "application/json"}
    check_default_get(UNIT_URL+resource_name, headers_auth ,assert_positive_get)

    # search with first letter
    #without auth
    response = client.get(UNIT_URL+resource_name+'/count?search_word=f')
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"
    #with auth
    response = client.get(UNIT_URL+resource_name+'/count?search_word=f',headers=headers_auth)
    assert response.status_code == 200
    assert response.json() == 2

    # search with starting two letters
    response = client.get(UNIT_URL+resource_name+'/count?search_word=fi',headers=headers_auth)
    assert response.status_code == 200
    assert response.json() == 1

    # search for not available
    response = client.get(UNIT_URL+resource_name+'/count?search_word=ten',headers=headers_auth)
    assert response.json() == 0

    # full word match
    response = client.get(UNIT_URL+resource_name+'/count?search_word=two&exact_match=True',headers=headers_auth)
    assert response.status_code == 200
    assert response.json() == 1

    # with details
    response = client.get(UNIT_URL+resource_name+'/count?details={"type":"odd"}',headers=headers_auth)
    assert response.status_code == 200
    assert response.json() == 3

    response = client.get(UNIT_URL+resource_name+'/count?details={"type":"even"}',headers=headers_auth)
    assert response.status_code == 200
    assert response.json() == 2

   # search details having empty value
    response = client.get(UNIT_URL+resource_name+'/count?details={"empty-field":""}',headers=headers_auth)
    assert response.status_code == 200
    assert response.json() == 1

    # search word from details
    response = client.get(UNIT_URL+resource_name+'/count?search_word=odd',headers=headers_auth)
    assert response.status_code == 200
    assert response.json() == 3

    # all words, active and inactive
    response = client.get(UNIT_URL+resource_name+'/count',headers=headers_auth)
    assert response.json() == 7
    response = client.get(UNIT_URL+resource_name+'/count?active=True',headers=headers_auth)
    assert response.json() == 6
    response = client.get(UNIT_URL+resource_name+'/count?active=false',headers=headers_auth)
    assert response.json() == 1

def test_get_active_and_inactive():
    '''Test after the API change as per the request: 
    https://github.com/Bridgeconn/vachan-api/issues/508'''

    data = [
        {"word": "one", "details":{"digit": 1, "type":"odd", "link":UNIT_URL+'vocabulary?word=one'}},
        {"word": "two", "details":{"digit": 2, "type":"even", "link":UNIT_URL+'vocabulary?word=two'}},
        {"word": "three", "details":{"digit": 3, "type":"odd",
        "link":UNIT_URL+'vocabulary?word=three'}},
        {"word": "four", "details":{"digit": 4, "type":"even",
        "link":UNIT_URL+'vocabulary?word=four'}},
        {"word": "five", "details":{"digit": 5, "type":"odd", "link":UNIT_URL+'vocabulary?word=five'}},
        {"word": "another", "details":{"empty-field": ""}},
        {"word": "inactive", "active": "false"}
    ]
    resp, resource_name = check_post(data)
    assert resp.status_code == 201

    # all words, active and inactive
    response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert len(response.json()) == 7
    response = client.get(UNIT_URL+resource_name+'?active=True',headers=headers_auth)
    assert len(response.json()) == 6
    response = client.get(UNIT_URL+resource_name+'?active=false',headers=headers_auth)
    assert len(response.json()) == 1


def test_delete_default():
    ''' positive test case, checking for correct return of deleted word ID'''
    #create new data
    response,resource_name = test_post_default()
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    post_response = client.get(UNIT_URL+resource_name+'?search_word=one',\
        headers=headers_auth)
    assert post_response.status_code == 200
    assert len(post_response.json()) == 1
    for item in post_response.json():
        assert_positive_get(item)   
    vocabulary_response = client.get(UNIT_URL+resource_name ,headers=headers_auth)
    word_id = vocabulary_response.json()[0]['wordId'] 

    #Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    response = client.delete(UNIT_URL+resource_name  + "?word_id=" + str(word_id), headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

     #Delete word with other API user,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev']:
        headers_au = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL+resource_name  + "?word_id=" + str(word_id), headers=headers_au)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete word with Vachan Admin
    headers_va = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['VachanAdmin']['token']
            }
    response = client.delete(UNIT_URL+resource_name  + "?word_id=" + str(word_id), headers=headers_va)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Vocabulary id {word_id} deleted successfully"
    #Check vocabulary is deleted from table
    vocabulary_response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert vocabulary_response.status_code == 200
    delete_response = client.get(UNIT_URL+resource_name+'?search_word=one',\
        headers=headers_auth)
    assert_not_available_content(delete_response)

def test_delete_with_editable_permission():
    '''Delete operation of item with access permission editable upon resource creation
    * As per the request https://github.com/Bridgeconn/vachan-api/issues/572'''
    # Create Version
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for vocabularies",
    }
    add_version(version_data)
    # Create Resource with access permission "editable by VachanAdmin"
    resource_data = {
        "resourceType": "vocabulary",
        "language": "en",
        "version": "TTT",
        "revision": 1,
        "year": 2000,
        "accessPermissions": ["editable"]
    }
    response = add_resource(resource_data)
    resource_name = response.json()['data']['resourceName']
    # Add items to table by VachanAdmin
    headers_va = {"contentType": "application/json",
                "accept": "application/json"}
    headers_va['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    data = [
    	{"word": "one", "details":{"digit": 1, "type":"odd"}},
    	{"word": "two", "details":{"digit": 2, "type":"even"}},
    	{"word": "three", "details":{"digit": 3, "type":"odd"}},
    	{"word": "four", "details":{"digit": 4, "type":"even"}}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_va, json=data)
    #get item ids
    vocabulary_response = client.get(UNIT_URL+resource_name,headers=headers_va)
    item_ids = [item['wordId'] for item in vocabulary_response.json()]


    #Delete item with API user,VachanUser,BcsDev - Negative Test
    for user in ['APIUser','VachanUser','BcsDev']:
        headers_noauth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL+resource_name  + "?word_id=" + str(item_ids[0]), headers=headers_noauth)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete item with AgAdmin, SanketMASTAdmin, AgUser, SanketMASTUser- Positive Test
    users = ["AgAdmin", "SanketMASTAdmin", "AgUser", "SanketMASTUser"]
    for item_id, user in zip(item_ids, users):
        data = {
            "itemId": item_id
        }
        headers_users = {
            "contentType": "application/json",
            "accept": "application/json",
            'Authorization': "Bearer " + initial_test_users[user]['token']
        }

        response = client.delete(UNIT_URL+resource_name  + "?word_id=" + str(item_id), headers=headers_users)
        assert response.status_code == 200
        assert response.json()['message'] == f"Vocabulary id {item_id} deleted successfully"

    #Confirm deleted items does not exist in table
    vocabulary_response = client.get(UNIT_URL+resource_name,headers=headers_va)
    assert_not_available_content(vocabulary_response)

def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted word ID'''
    #Created User or Super Admin can only delete word
    #creating data
    response,resource_name = test_post_default()

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

    vocabulary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    word_id = vocabulary_response.json()[0]['wordId']
     #Delete word with Super Admin
    response = client.delete(UNIT_URL+resource_name  + "?word_id=" + str(word_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Vocabulary id {word_id} deleted successfully"
    #Check word is deleted from table
    vocabulary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    logout_user(test_user_token)
    return response,resource_name

def test_delete_word_id_string():
    '''positive test case, vocabulary id as string'''
    response,resource_name = test_post_default()

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

    vocabulary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    word_id = vocabulary_response.json()[0]['wordId']
    word_id = str(word_id)
    #Delete vocabulary with Super Admin
    response = client.delete(UNIT_URL+resource_name  + "?word_id=" + str(word_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Vocabulary id {word_id} deleted successfully"
    #Check vocabulary word is deleted from table
    vocabulary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    logout_user(test_user_token)

def test_delete_incorrectdatatype():
    '''negative testcase. Passing input data not in json format'''
    response,resource_name = test_post_default()

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

    vocabulary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    word_id = {}
    

    #Delete vocabulary with Super Admin
    response = client.delete(UNIT_URL+resource_name  + "?word_id=" + str(word_id), headers=headers_sa)
    assert_input_validation_error(response)
    logout_user(test_user_token)

def test_delete_missingvalue_word_id():
    '''Negative Testcase. Passing input data without wordId'''
    response,resource_name = test_post_default()

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

    word_id =" "
    response = client.delete(UNIT_URL+resource_name  + "?word_id=" + str(word_id), headers=headers_sa)
    assert_input_validation_error(response)
    logout_user(test_user_token)

def test_delete_missingvalue_resource_name():
    '''Negative Testcase. Passing input data without resourceName'''
    response,resource_name = test_post_default()

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
    vocabulary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    word_id = vocabulary_response.json()[0]['wordId']
    response = client.delete(UNIT_URL + "?word_id=" + str(word_id), headers=headers_sa)
    assert response.status_code == 404
    logout_user(test_user_token)

def test_delete_notavailable_content():
    ''' request a non existing word ID, Ensure there is no partial matching'''
    response,resource_name = test_post_default()

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

    word_id = 9999

     #Delete vocabulary with Super Admin
    response = client.delete(UNIT_URL+resource_name  + "?word_id=" + str(word_id), headers=headers_sa)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    logout_user(test_user_token)

def test_restore_default():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response,resource_name = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}
    #Restoring data
    #Restore without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'


    #Restore content with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev,'VachanContentAdmin','VachanContentViewer'
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev','VachanContentAdmin','VachanContentViewer']:
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
    restore_response = client.get(UNIT_URL+resource_name+'?search_word=one',\
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

def test_restoreitem_with_notavailable_resource():
    ''' Negative test case.request to restore an item whoose resource is not available'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response,resource_name = test_delete_default_superadmin()
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
    #Delete Associated Resource
    get_resource_response = client.get(RESOURCE_URL + "?resource_name="+resource_name, headers=headers_auth)
    resource_id = get_resource_response.json()[0]["resourceId"]
    response = client.delete(RESOURCE_URL +"?resource_id=" + str(resource_id), headers=headers_auth)
    assert response.status_code == 200
    #Restoring data
    #Restore content with Super Admin after deleting resource
    restore_response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    restore_response.status_code = 404
    logout_user(test_user_token)
