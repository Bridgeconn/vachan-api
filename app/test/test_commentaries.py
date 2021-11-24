'''Test cases for commentaries related APIs'''
from . import client, contetapi_get_accessrule_checks_app_userroles
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get, check_soft_delete
from .test_versions import check_post as add_version
from .test_sources import check_post as add_source
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER
from .conftest import initial_test_users

UNIT_URL = '/v2/commentaries/'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "book" in item
    assert "bookId" in item['book']
    assert "bookCode" in item['book']
    assert "chapter" in item
    assert "verseStart" in item
    assert "verseEnd" in item
    assert "commentary" in item
    assert "active" in item

def check_post(data: list):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for commentaries",
    }
    add_version(version_data)
    source_data = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "revision": 1,
        "year": 2000,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    source = add_source(source_data)
    source_name = source.json()['data']['sourceName']
    #without auth
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    if response.status_code == 422:
        assert response.json()['error'] == 'Input Validation Error'
    else:
        assert response.status_code == 401
        assert response.json()['error'] == 'Authentication Error'
    #with auth
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    return response, source_name

def test_post_default():
    '''Positive test to upload commentries, with various kins of ref ranges supported'''
    data = [
    	{'bookCode':'gen', 'chapter':0, 'commentary':'book intro to Genesis'},
    	{'bookCode':'gen', 'chapter':1, 'verseStart':0, 'verseEnd': 0,
    		'commentary':'chapter intro to Genesis 1'},
    	{'bookCode':'gen', 'chapter':1, 'verseStart':1, 'verseEnd': 10,
    		'commentary':'the begining'},
    	{'bookCode':'gen', 'chapter':1, 'verseStart':3, 'verseEnd': 30,
    		'commentary':'the creation'},
    	{'bookCode':'gen', 'chapter':1, 'verseStart':-1, 'verseEnd': -1,
    		'commentary':'Chapter Epilogue. God completes creation in 6 days.'},
    	{'bookCode':'gen', 'chapter':-1, 'commentary':'book Epilogue.'}
    ]
    response = check_post(data)[0]
    assert response.status_code == 201
    assert response.json()['message'] == "Commentaries added successfully"
    assert len(data) == len(response.json()['data'])
    for item in response.json()['data']:
        assert_positive_get(item)


def test_post_duplicate():
    '''Negative test to add two commentaries with same reference range'''
    data = [
    	{'bookCode':'gen', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    resp, source_name = check_post(data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Commentaries added successfully"

    headers = {"contentType": "application/json", "accept": "application/json"}
    data[0]['commentary'] = 'another commentary on first verse'
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    data = {'bookCode':'gen', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    resp, source_name = check_post(data)
    assert_input_validation_error(resp)

    # data object with missing mandatory fields
    headers = {"contentType": "application/json", "accept": "application/json"}
    data = [
        {'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':1, "verseEnd":1}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields

    data = [
        {'bookCode':'genesis', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':'introduction', 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':'introduction',
        'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':'introduction',
        'commentary':'first verse of Genesis', 'active': "deactive"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':10,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    source_name1 = source_name.replace('commentary', 'bible')
    response = client.post(UNIT_URL+source_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '2')
    response = client.post(UNIT_URL+source_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_get_after_data_upload():
    '''Add some data into the table and do all get tests'''
    data = [
        {'bookCode':'gen', 'chapter':0, 'commentary':'book intro to Genesis'},
        {'bookCode':'gen', 'chapter':1, 'verseStart':0, 'verseEnd': 0,
            'commentary':'chapter intro to Genesis 1'},
        {'bookCode':'gen', 'chapter':1, 'verseStart':1, 'verseEnd': 10,
            'commentary':'the begining'},
        {'bookCode':'gen', 'chapter':1, 'verseStart':3, 'verseEnd': 30,
            'commentary':'the creation'},
        {'bookCode':'gen', 'chapter':1, 'verseStart':-1, 'verseEnd': -1,
            'commentary':'Chapter Epilogue. God completes creation in 6 days.'},
        {'bookCode':'gen', 'chapter':-1, 'commentary':'book Epilogue.'},

        {'bookCode':'exo', 'chapter':1, 'verseStart':1,
            "verseEnd":1, 'commentary':'first verse of Exodus'},
        {'bookCode':'exo', 'chapter':1, 'verseStart':1,
        "verseEnd":10, 'commentary':'first para of Exodus'},
        {'bookCode':'exo', 'chapter':1, 'verseStart':1,
        "verseEnd":25, 'commentary':'first few paras of Exodus'},
        {'bookCode':'exo', 'chapter':1, 'verseStart':20,
        "verseEnd":25, 'commentary':'a middle para of Exodus'},
        {'bookCode':'exo', 'chapter':0, 'commentary':'Book intro to Exodus'}
    ]
    resp, source_name = check_post(data)

    assert resp.status_code == 201
    check_default_get(UNIT_URL+source_name, headers_auth,assert_positive_get)

    #filter by book
    #without auth
    response = client.get(UNIT_URL+source_name+'?book_code=gen')
    assert response.status_code == 403
    assert response.json()["error"] == "Permission Denied"

    #with auth
    response = client.get(UNIT_URL+source_name+'?book_code=gen',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 6

    response = client.get(UNIT_URL+source_name+'?book_code=exo',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 5

    # all book introductions
    response = client.get(UNIT_URL+source_name+'?chapter=0',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # all chapter intros
    response = client.get(UNIT_URL+source_name+'?verse=0',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # all commentaries associated with a verse
    response = client.get(UNIT_URL+source_name+'?book_code=gen&chapter=1&verse=1',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(UNIT_URL+source_name+'?book_code=gen&chapter=1&verse=8',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+source_name+'?book_code=exo&chapter=1&verse=1',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.get(UNIT_URL+source_name+'?book_code=exo&chapter=1&verse=2',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+source_name+'?book_code=exo&chapter=1&verse=21',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # commentaries for a verse range
    # exact range
    response = client.get(UNIT_URL+source_name+'?book_code=exo&chapter=1&verse=1&last_verse=25',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(UNIT_URL+source_name+'?book_code=gen&chapter=1&verse=0&last_verse=0',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # inclusive
    response = client.get(UNIT_URL+source_name+'?book_code=EXO&chapter=1&verse=1&last_verse=3',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # crossing boundary
    response = client.get(UNIT_URL+source_name+'?book_code=exo&chapter=1&verse=3&last_verse=13',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # not available
    response = client.get(UNIT_URL+source_name+'?book_code=rev&chapter=1&verse=3&last_verse=13',headers=headers_auth)
    assert_not_available_content(response)

def test_get_incorrect_data():
    '''Check for input validations in get'''
    source_name = 'hi_TTT'
    response = client.get(UNIT_URL+source_name,headers=headers_auth)
    assert_input_validation_error(response)

    source_name = 'hi_TTT_1_commentary'
    response = client.get(UNIT_URL+source_name+'?book_code=10',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?book_code=matthew',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?chapter=intro',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?chapter=-10',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?verse=-10',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?active=not',headers=headers_auth)
    assert_input_validation_error(response)

    resp, source_name = check_post([])
    assert resp.status_code == 201
    source_name = source_name.replace('commentary', 'bible')
    response = client.get(UNIT_URL+source_name,headers=headers_auth)
    assert response.status_code == 404

def test_put_after_upload():
    '''Positive tests for put'''
    data = [
        {'bookCode':'mat', 'chapter':1, 'verseStart':1,
        'verseEnd':10, 'commentary':"first verses of matthew"},
        {'bookCode':'mrk','chapter':0, 'commentary':"book intro to Mark"},
    ]
    response, source_name = check_post(data)
    assert response.status_code == 201

    # positive PUT
    new_data = [
        {'bookCode':'mat', 'chapter':1, 'verseStart':1,
        'verseEnd':10, 'commentary':"first verses of matthew"},
        {'bookCode':'mrk','chapter':0, 'commentary':"book intro to Mark"},
    ]
    #without auth
    response = client.put(UNIT_URL+source_name,headers=headers, json=new_data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Commentaries updated successfully'
    for i,item in enumerate(response.json()['data']):
        assert_positive_get(item)
        assert response.json()['data'][i]['commentary'] == new_data[i]['commentary']
        assert response.json()['data'][i]['book']['bookCode'] == data[i]['bookCode']
        assert response.json()['data'][i]['chapter'] == data[i]['chapter']
        if 'verseEnd' in data[i]:
            assert response.json()['data'][i]['verseStart'] == data[i]['verseStart']
            assert response.json()['data'][i]['verseEnd'] == data[i]['verseEnd']
        else:
            assert response.json()['data'][i]['verseStart'] is None
            assert response.json()['data'][i]['verseEnd'] is None

    # not available PUT
    new_data[0]['chapter'] = 2
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 404

    source_name = source_name.replace('1', '2')
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=[])
    assert response.status_code == 404

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''

    post_data = [{'bookCode':'gen', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}]
    resp, source_name = check_post(post_data)
    assert resp.status_code == 201

    # single data object instead of list
    headers = {"contentType": "application/json", "accept": "application/json"}
    data = {'bookCode':'gen', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'new commentary'}
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # data object with missing mandatory fields
    data = [
        {'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields

    data = [
        {'bookCode':'genesis', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':'introduction', 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':'introduction',
        'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)


    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':10,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    source_name1 = source_name.replace('commentary', 'bible')
    response = client.put(UNIT_URL+source_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '2')
    response = client.put(UNIT_URL+source_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_soft_delete():
    '''check soft delete in commentaries'''
    data = [
        {'bookCode':'mrk', 'chapter':1, 'verseStart':1,
        'verseEnd':10, 'commentary':"first verses of Mark"},
        {'bookCode':'mrk','chapter':0, 'commentary':"book intro to Mark"},
    ]

    delete_data = [
        {'bookCode':'mrk', 'chapter':1, 'verseStart':1, 'verseEnd':10}
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
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "commentary",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    #create source
    response = client.post('/v2/sources', headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"
    source_name = 'ml_TTT_1_commentary'
    
    #create commentary
    data = [
        {'bookCode':'mat', 'chapter':1, 'verseStart':1,
        'verseEnd':10, 'commentary':"first verses of matthew"},
        {'bookCode':'mrk','chapter':0, 'commentary':"book intro to Mark"},
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert response.status_code == 201

    #update commentary with created SA user
    new_data = [
        {'bookCode':'mat', 'chapter':1, 'verseStart':1,
        'verseEnd':10, 'commentary':"first verses of matthew"},
        {'bookCode':'mrk','chapter':0, 'commentary':"book intro to Mark"},
    ]
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Commentaries updated successfully'

    #update with VA not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'


def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    data = [
    	{'bookCode':'gen', 'chapter':0, 'commentary':'book intro to Genesis'}
    ]
    contetapi_get_accessrule_checks_app_userroles("commentary",UNIT_URL,data)