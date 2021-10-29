'''Test cases for bible videos related APIs'''
from . import client, contetapi_get_accessrule_checks_app_userroles
from . import check_default_get, check_soft_delete
from .test_sources import check_post as add_source
from .test_versions import check_post as add_version
from . import assert_input_validation_error, assert_not_available_content
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER
from .conftest import initial_test_users

UNIT_URL = '/v2/biblevideos/'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "books" in item
    assert  isinstance(item['books'], list)
    for book in item['books']:
        assert isinstance(book, str)
        assert len(book) == 3
    assert "title" in item
    assert "theme" in item
    assert "description" in item
    assert "videoLink" in item

def check_post(data: list):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for biblevideo",
    }
    add_version(version_data)
    source_data = {
        "contentType": "biblevideo",
        "language": "mr",
        "version": "TTT",
        "year": 1999,
        "revision": 1
    }
    source = add_source(source_data)
    table_name = source.json()['data']['sourceName']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    #without auth
    resp = client.post(UNIT_URL+table_name, headers=headers, json=data)
    if resp.status_code == 422:
        assert resp.json()['error'] == 'Input Validation Error'
    else:
        assert resp.status_code == 401
        assert resp.json()['error'] == 'Authentication Error'
    #with auth
    resp = client.post(UNIT_URL+table_name, headers=headers_auth, json=data)
    return resp, table_name

def test_post_default():
    '''Positive test to upload bible videos'''
    data = [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
    resp = check_post(data)[0]
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible videos added successfully"
    for item in resp.json()['data']:
        assert_positive_get(item)
    assert len(data) == len(resp.json()['data'])

def test_post_duplicate():
    '''Negative test to add two bible videos Links with same title'''
    data = [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
    response1, source_name = check_post(data)
    assert response1.status_code == 201
    assert response1.json()['message'] == "Bible videos added successfully"

    data[0]['videoLink'] = 'https://www.youtube.com/biblevideos/anothervid'
    response2 = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert response2.status_code == 409
    assert response2.json()['error'] == "Already Exists"

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    one_row = {'title':'Overview: Genesis', 'theme': 'Old testament',
        'description':"brief description",
        'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}

    resp, source_name = check_post(one_row)
    assert_input_validation_error(resp)

    # data object with missing mandatory fields
    headers = {"contentType": "application/json", "accept": "application/json"}
    data = [
        {'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen']}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields
    data = [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': 'gen', 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'vid'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    data = [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['Genesis'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    source_name1 = source_name.replace('biblevideo', 'video')
    data = []
    response = client.post(UNIT_URL+source_name1, headers=headers_auth, json=data)
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '22')
    response = client.post(UNIT_URL+source_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_get_after_data_upload():
    '''Add some infographics data into the table and do all get tests'''
    input_data = [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Gospels', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat', 'mrk', 'luk', 'jhn'],
            'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament',
            'description':"brief description",
            'books': ['act'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Matthew', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
    res, source_name = check_post(input_data)
    assert res.status_code == 201
    check_default_get(UNIT_URL+source_name, headers_auth, assert_positive_get)

    #filter by book
    #without auth
    response = client.get(UNIT_URL+source_name+'?book_code=gen')
    assert response.status_code == 403
    assert response.json()['error'] == 'Permision Denied'
    #with auth
    response = client.get(UNIT_URL+source_name+'?book_code=gen',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(UNIT_URL+source_name+'?book_code=mat',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # filter with title
    response = client.get(UNIT_URL+source_name+'?title=Overview:%20Matthew')
    assert response.status_code == 403
    assert response.json()['error'] == 'Permision Denied'
    #with auth
    response = client.get(UNIT_URL+source_name+'?title=Overview:%20Matthew',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with theme
    response = client.get(UNIT_URL+source_name+"?theme=Old%20testament",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+source_name+"?theme=New%20testament",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3

    # not available
    response = client.get(UNIT_URL+source_name+'?book_code=rev',headers=headers_auth)
    assert_not_available_content(response)

    response = client.get(UNIT_URL+source_name+'?book_code=mat&theme=Old%20testament',headers=headers_auth)
    assert_not_available_content(response)

def test_get_incorrect_data():
    '''Check for input validations in get'''
    source_name = 'mr_TTT'
    response = client.get(UNIT_URL+source_name)
    assert_input_validation_error(response)

    source_name = 'mr_TTT_1_biblevideo'
    response = client.get(UNIT_URL+source_name+'?book_code=61',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?book_code=luke',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?book_code=[gen]',headers=headers_auth)
    assert_input_validation_error(response)

    resp, source_name = check_post([])
    assert resp.status_code == 201

    source_name_edited = source_name.replace('bible', '')
    response = client.get(UNIT_URL+source_name_edited,headers=headers_auth)
    assert response.status_code == 404

def test_put_after_upload():
    '''Positive tests for put'''
    data = [
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament',
            'description':"brief description",
            'books': ['act'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Matthew', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
    response, source_name = check_post(data)
    assert response.status_code == 201

    # positive PUT
    new_data = [
        {'title':'Overview: Matthew', 'active': False},
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament history'},
        {'title':'Overview: Exodus', 'videoLink': 'https://www.youtube.com/biblevideos/newvid'}
    ]
    # headers = {"contentType": "application/json", "accept": "application/json"}
    #Without Auth
    new_response = client.put(UNIT_URL+source_name,headers=headers, json=new_data)
    assert new_response.status_code == 401
    assert new_response.json()['error'] == 'Authentication Error'
    #with auth
    new_response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert new_response.status_code == 201
    assert new_response.json()['message'] == 'Bible videos updated successfully'
    print(new_response.json()['data'])
    for item in new_response.json()['data']:
        assert_positive_get(item)
        if item['title'] == 'Overview: Exodus':
            assert item['videoLink'].endswith('newvid')
        if item['title'] == 'Overview: Matthew':
            assert not item['active']
        if item['title'] == 'Overview: Acts of Apostles':
            assert item['theme'] == 'New testament history'

    # not available PUT
    new_data = [
        {'title':'Overview: Acts', 'theme': 'New testament history'}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=new_data)
    assert response.status_code == 404

    source_name = source_name.replace('1', '20')
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''

    post_data = [
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament',
            'description':"brief description",
            'books': ['act'], 'videoLink': 'https://www.youtube.com/biblevideos/vid',
            'status':True},
        {'title':'Overview: Matthew', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat'], 'videoLink': 'https://www.youtube.com/biblevideos/vid',
            'status':True},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid', 'status':True}
    ]
    resp, source_name = check_post(post_data)
    assert resp.status_code == 201

    # single data object instead of list
    headers = {"contentType": "application/json", "accept": "application/json"}
    data =  {'title':'Overview: Acts of Apostles', 'theme': 'Old testament'}
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # data object with missing mandatory fields
    data = [
        {'theme': 'New testament',
        "videoLink":"http://anotherplace.com/something"}
            ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields

    data = [
        {'title':'Overview: Acts of Apostles', 'books': 'acts'}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'title':'Overview: Acts of Apostles', 'active': 'deactivate'}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'title':'Overview: Acts of Apostles', 'books': [1,2,3]}
    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)


    data = [ {'title':'Overview: Acts of Apostles', "videoLink":"Not a link"} ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    source_name1 = source_name.replace('bible', '')
    response = client.put(UNIT_URL+source_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '13')
    response = client.put(UNIT_URL+source_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_soft_delete():
    '''check soft delete in infographics'''
    data = [
        {'title':'Words of Jesus', 'theme': 'New testament',
            'description':"brief description",
            'books': ['mat', 'mrk', 'luk', 'jhn'],
            'videoLink': 'https://www.youtube.com/biblevideos/vid',
            'status':True},
        {'title':'Miracles of Jesus', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat', 'mrk', 'luk', 'jhn'],
            'videoLink': 'https://www.youtube.com/biblevideos/vid',
            'status':True},
        {'title':'Miracles the Israelites saw', 'theme': 'Old testament',
            'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid', 'status':True}
    ]

    delete_data = [
        {'title':'Words of Jesus'},
        {'title':'Miracles of Jesus'}
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
        "versionName": "test version for biblevideo",
    }
    add_version(version_data)
    source_data = {
        "contentType": "biblevideo",
        "language": "mr",
        "version": "TTT",
        "year": 1999,
        "revision": 1
    }
    #create source
    response = client.post('/v2/sources', headers=headers_auth, json=source_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"
    source_name = response.json()['data']['sourceName']
    
    #create bible videos
    data = [
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament',
            'description':"brief description",
            'books': ['act'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Matthew', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
    resp = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert resp.status_code == 201
    assert resp.json()['message'] == 'Bible videos added successfully'

    #update dictionary with created SA user
    new_data = [
        {'title':'Overview: Matthew', 'active': False},
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament history'},
        {'title':'Overview: Exodus', 'videoLink': 'https://www.youtube.com/biblevideos/newvid'}
    ]
    new_response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert new_response.status_code == 201
    assert new_response.json()['message'] == 'Bible videos updated successfully'

    #update with VA not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    new_response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert new_response.status_code == 403
    assert new_response.json()['error'] == 'Permision Denied'

def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    data = [
    	{'title':'Overview: Acts of Apostles', 'theme': 'New testament',
            'description':"brief description",
            'books': ['act'], 'videoLink': 'https://www.youtube.com/biblevideos/vid',
            'status':True}
    ]
    contetapi_get_accessrule_checks_app_userroles("biblevideo",UNIT_URL,data)