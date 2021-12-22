'''Test cases for dictionary related APIs'''
from . import client , contetapi_get_accessrule_checks_app_userroles
from . import assert_input_validation_error, assert_not_available_content

from . import check_default_get, check_soft_delete
from .test_versions import check_post as add_version
from .test_sources import check_post as add_source
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER
from .conftest import initial_test_users

UNIT_URL = '/v2/dictionaries/'
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
        "versionName": "test version for dictionaries",
    }
    add_version(version_data)
    source_data = {
        "contentType": "dictionary",
        "language": "en",
        "version": "TTT",
        "revision": 1,
        "year": 2000
    }
    source = add_source(source_data)
    headers = {"contentType": "application/json", "accept": "application/json"}
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
    '''Positive test to upload dictionary words'''
    data = [
    	{"word": "one", "details":{"digit": 1, "type":"odd"}},
    	{"word": "two", "details":{"digit": 2, "type":"even"}},
    	{"word": "three", "details":{"digit": 3, "type":"odd"}},
    	{"word": "four", "details":{"digit": 4, "type":"even"}},
    	{"word": "five", "details":{"digit": 5, "type":"odd"}}
    ]
    response = check_post(data)[0]
    assert response.status_code == 201
    assert response.json()['message'] == "Dictionary words added successfully"
    assert len(data) == len(response.json()['data'])
    for item in response.json()['data']:
        assert_positive_get(item)


def test_post_duplicate():
    '''Negative test to add two entires with same word'''
    data = [
    	{"word": "one", "details":{"digit": 1, "type":"odd"}}
    ]
    resp, source_name = check_post(data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Dictionary words added successfully"

    # headers = {"contentType": "application/json", "accept": "application/json"}
    data[0]['details'] = {"digit": 1, "type":"natural number"}
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    data = {"word": "one", "details":{"digit": 1, "type":"odd"}}
    # (this step creates version and source that can be used in other tests in this function)
    resp, source_name = check_post(data)
    assert_input_validation_error(resp)

    # data object with missing mandatory fields
    # headers = {"contentType": "application/json", "accept": "application/json"}
    data = [
    	{"details":{"digit": 1, "type":"odd"}}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data value for details
    data = [
    	{"details":'"digit"= 1, "type"="odd"'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

 	# wrong source name
    source_name1 = source_name.replace('dictionary', 'bible')
    response = client.post(UNIT_URL+source_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '3')
    response = client.post(UNIT_URL+source_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_get_after_data_upload():
    '''Add some data into the table and do all get tests'''
    data = [
    	{"word": "one", "details":{"digit": 1, "type":"odd", "link":UNIT_URL+'dictionary?word=one'}},
    	{"word": "two", "details":{"digit": 2, "type":"even", "link":UNIT_URL+'dictionary?word=two'}},
    	{"word": "three", "details":{"digit": 3, "type":"odd",
    	"link":UNIT_URL+'dictionary?word=three'}},
    	{"word": "four", "details":{"digit": 4, "type":"even",
    	"link":UNIT_URL+'dictionary?word=four'}},
    	{"word": "five", "details":{"digit": 5, "type":"odd", "link":UNIT_URL+'dictionary?word=five'}}
    ]
    resp, source_name = check_post(data)
    assert resp.status_code == 201
    # headers = {"contentType": "application/json", "accept": "application/json"}
    check_default_get(UNIT_URL+source_name, headers_auth ,assert_positive_get)

    # search with first letter
    #without auth
    response = client.get(UNIT_URL+source_name+'?search_word=f')
    assert response.status_code == 403
    assert response.json()["error"] == "Permission Denied"
    #with auth
    response = client.get(UNIT_URL+source_name+'?search_word=f',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # search with starting two letters
    response = client.get(UNIT_URL+source_name+'?search_word=fi',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # search for not available
    response = client.get(UNIT_URL+source_name+'?search_word=ten',headers=headers_auth)
    assert_not_available_content(response)

    # full word match
    response = client.get(UNIT_URL+source_name+'?search_word=two&exact_match=True',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['word'] == 'two'

    # with only words flag
    response = client.get(UNIT_URL+source_name+'?word_list_only=True',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 5
    for item in response.json():
        assert "details" not in item

    # with details
    response = client.get(UNIT_URL+source_name+'?details={"type":"odd"}',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3
    for item in response.json():
        assert item['details']['type'] == "odd"

    response = client.get(UNIT_URL+source_name+'?details={"type":"even"}',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    for item in response.json():
        assert item['details']['type'] == "even"

def test_get_incorrect_data():
    '''Check for input validations in get'''

    source_name = 'en_TTT'
    response = client.get(UNIT_URL+source_name,headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?details="test"',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?details=None',headers=headers_auth)
    assert_input_validation_error(response)

    resp, source_name = check_post([])
    assert resp.status_code == 201
    source_name = source_name.replace('dictionary', 'bible')
    response = client.get(UNIT_URL+source_name,headers=headers_auth)
    assert response.status_code == 404

def test_put_after_upload():
    '''Tests for put'''
    data = [
    	{"word": "Adam", "details": {"description": "Frist man"}},
    	{"word": "Eve", "details": {"description": "Wife of Adam"}}
    ]
    response, source_name = check_post(data)
    assert response.status_code == 201

    # positive PUT
    new_data = [
    	{"word": "Adam", "details": {"description": "Frist man God created"}},
    	{"word": "Eve", "details": {"description": "Wife of Adam, and Mother of mankind"}}
    ]
    # headers = {"contentType": "application/json", "accept": "application/json"}
    #without auth
    response = client.put(UNIT_URL+source_name,headers=headers, json=new_data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #with auth
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Dictionary words updated successfully'
    for i,item in enumerate(response.json()['data']):
        assert_positive_get(item)
        assert response.json()['data'][i]['details'] == new_data[i]['details']

    # not available PUT
    new_data = [
    	{"word": "Moses", "details": {"description": "Leader of Isreal"}}
    ]
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 404

    source_name = source_name.replace('1', '5')
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=[])
    assert response.status_code == 404

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''

    # to create necessary versions and source
    resp, source_name = check_post([])
    assert resp.status_code == 201


    # single data object instead of list
    headers = {"contentType": "application/json", "accept": "application/json"}
    data = {"word": "one", "details":{"digit": 1, "type":"odd"}}
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # data object with missing mandatory fields
    data = [
    	{"details":{"digit": 1, "type":"odd"}}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data value for details
    data = [
    	{"details":'"digit"= 1, "type"="odd"'}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

 	# wrong source name
    source_name1 = source_name.replace('dictionary', 'bible')
    response = client.put(UNIT_URL+source_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '3')
    response = client.put(UNIT_URL+source_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_soft_delete():
    '''check soft delete in dictionaries'''
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
        "versionName": "test version for dictionaries",
    }
    add_version(version_data)
    source_data = {
        "contentType": "dictionary",
        "language": "en",
        "version": "TTT",
        "revision": 1,
        "year": 2000
    }
    #create source
    response = client.post('/v2/sources', headers=headers_auth, json=source_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"
    source_name = response.json()['data']['sourceName']
    
    #create dictionary
    data = [
    	{"word": "Adam", "details": {"description": "Frist man"}},
    	{"word": "Eve", "details": {"description": "Wife of Adam"}}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Dictionary words added successfully'

    #update dictionary with created SA user
    new_data = [
    	{"word": "Adam", "details": {"description": "Frist man God created"}},
    	{"word": "Eve", "details": {"description": "Wife of Adam, and Mother of mankind"}}
    ]
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Dictionary words updated successfully'

    #update with VA not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    data = [
    	{"word": "one", "details":{"digit": 1, "type":"odd", "link":UNIT_URL+'dictionary?word=one'}}
    ]
    contetapi_get_accessrule_checks_app_userroles("dictionary",UNIT_URL,data)