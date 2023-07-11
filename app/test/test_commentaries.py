'''Test cases for commentaries related APIs'''
import time
from app.main import log
from . import client, contetapi_get_accessrule_checks_app_userroles
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_versions import check_post as add_version
from .test_resources import check_post as add_resource
from . test_auth_basic import SUPER_PASSWORD,SUPER_USER, login, logout_user
from .conftest import initial_test_users
from .test_stop_words_generation import get_job_status


UNIT_URL = '/v2/commentaries/'
RESOURCE_URL = '/v2/resources'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
RESTORE_URL = '/v2/restore'

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "book" in item
    assert "bookId" in item['book']
    assert "bookCode" in item['book']
    assert "chapter" in item
    # assert "verseStart" in item # optional params get_job remove null fields
    # assert "verseEnd" in item
    assert "commentary" in item
    assert "active" in item

def check_post(data: list):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for commentaries",
    }
    add_version(version_data)
    resource_data = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
        "year": 2000,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    resource = add_resource(resource_data)
    resource_name = resource.json()['data']['resourceName']
    #without auth
    headers = {"contentType": "application/json", "accept": "application/json"} #pylint: disable=redefined-outer-name
    response = client.post(UNIT_URL+resource_name, headers=headers, json=data)
    if response.status_code == 422:
        assert response.json()['error'] == 'Input Validation Error'
    else:
        assert response.status_code == 401
        assert response.json()['error'] == 'Authentication Error'
    #with auth
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    return response, resource_name

def check_commentary_job_finished(response):
    """check commentary upload finished or not"""
    assert "jobId" in response.json()['data']
    assert "status" in response.json()['data']
    for i in range(10):#pylint: disable=unused-variable
        job_response = get_job_status(response.json()['data']['jobId'])
        status = job_response.json()['data']['status']
        if status == 'job finished':
            break
        log.info("sleeping for a minute in get commentary status")
        time.sleep(60)
    return job_response

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
    response,resource_name = check_post(data)
    # resource_name = check_post(data)[0]
    assert response.status_code == 201
    assert response.json()['message'] == "Uploading Commentaries in background"
    job_response = check_commentary_job_finished(response)
    assert job_response.json()['data']['status'] == 'job finished'
    assert job_response.json()["message"] == "Commentaries added successfully"
    assert 'output' in job_response.json()['data']
    assert len(data) == len(job_response.json()['data']['output']['data'])
    # print("resp=======>",job_response.json()["message"])
    for item in job_response.json()['data']['output']['data']:
        assert_positive_get(item)
    return response,resource_name


def test_post_duplicate():
    '''Negative test to add two commentaries with same reference range'''
    data = [
    	{'bookCode':'gen', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    resp, resource_name = check_post(data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Uploading Commentaries in background"
    job_response = check_commentary_job_finished(resp)
    assert job_response.json()['data']['status'] == 'job finished'
    assert job_response.json()["message"] == "Commentaries added successfully"

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    data[0]['commentary'] = 'another commentary on first verse'

    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    job_response = get_job_status(response.json()['data']['jobId'])
    assert job_response.json()['data']['status'] == 'job error'
    assert job_response.json()["message"] == "Job is terminated with an error"
    assert job_response.json()["data"]["output"]["message"] ==\
        "Already exist commentary with same values for reference range"


def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    data = {'bookCode':'gen', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    resp, resource_name = check_post(data)
    assert_input_validation_error(resp)

    # data object with missing mandatory fields
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=unused-variable disable=redefined-outer-name
    data = [
        {'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':1, "verseEnd":1}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields

    data = [
        {'bookCode':'genesis', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':'introduction', 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':'introduction',
        'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':'introduction',
        'commentary':'first verse of Genesis', 'active': "deactive"}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':10,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    resource_name1 = resource_name.replace('commentary', 'bible')
    response = client.post(UNIT_URL+resource_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    resource_name2 = resource_name.replace('1', '2')
    response = client.post(UNIT_URL+resource_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_get_after_data_upload(): #pylint: disable=too-many-statements
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
    resp, resource_name = check_post(data)

    assert resp.status_code == 201
    assert resp.json()['message'] == "Uploading Commentaries in background"
    job_response = check_commentary_job_finished(resp)
    assert job_response.json()['data']['status'] == 'job finished'
    assert job_response.json()["message"] == "Commentaries added successfully"
    assert 'output' in job_response.json()['data']
    assert len(data) == len(job_response.json()['data']['output']['data'])
    for item in job_response.json()['data']['output']['data']:
        assert_positive_get(item)

    check_default_get(UNIT_URL+resource_name, headers_auth,assert_positive_get)

    #filter by book
    #without auth
    response = client.get(UNIT_URL+resource_name+'?book_code=gen')
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"

    #with auth
    response = client.get(UNIT_URL+resource_name+'?book_code=gen',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 6

    response = client.get(UNIT_URL+resource_name+'?book_code=exo',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 5

    # all book introductions
    response = client.get(UNIT_URL+resource_name+'?chapter=0',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # all chapter intros
    response = client.get(UNIT_URL+resource_name+'?verse=0',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # all commentaries associated with a verse
    response = client.get(UNIT_URL+resource_name+'?book_code=gen&chapter=1&verse=1',\
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(UNIT_URL+resource_name+'?book_code=gen&chapter=1&verse=8',\
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+resource_name+'?book_code=exo&chapter=1&verse=1',\
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.get(UNIT_URL+resource_name+'?book_code=exo&chapter=1&verse=2',\
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+resource_name+'?book_code=exo&chapter=1&verse=21',\
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # commentaries for a verse range
    # exact range
    response = client.get(UNIT_URL+resource_name+'?book_code=exo&chapter=1&verse=1&last_verse=25',\
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(UNIT_URL+resource_name+'?book_code=gen&chapter=1&verse=0&last_verse=0',\
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # inclusive
    response = client.get(UNIT_URL+resource_name+'?book_code=EXO&chapter=1&verse=1&last_verse=3',\
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # crossing boundary
    response = client.get(UNIT_URL+resource_name+'?book_code=exo&chapter=1&verse=3&last_verse=13',\
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # not available
    response = client.get(UNIT_URL+resource_name+'?book_code=rev&chapter=1&verse=3&last_verse=13',\
        headers=headers_auth)
    assert_not_available_content(response)

def test_get_incorrect_data():
    '''Check for input validations in get'''
    resource_name = 'hi_TTT'
    response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert_input_validation_error(response)

    resource_name = 'hi_TTT_1_commentary'
    response = client.get(UNIT_URL+resource_name+'?book_code=10',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+resource_name+'?book_code=matthew',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+resource_name+'?chapter=intro',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+resource_name+'?chapter=-10',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+resource_name+'?verse=-10',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+resource_name+'?active=not',headers=headers_auth)
    assert_input_validation_error(response)

    resp, resource_name = check_post([])
    assert resp.status_code == 201
    resource_name = resource_name.replace('commentary', 'bible')
    response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert response.status_code == 404

def test_put_after_upload():
    '''Positive tests for put'''
    data = [
        {'bookCode':'mat', 'chapter':1, 'verseStart':1,
        'verseEnd':10, 'commentary':"first verses of matthew"},
        {'bookCode':'mrk','chapter':0, 'commentary':"book intro to Mark"},
    ]
    response, resource_name = check_post(data)
    assert response.status_code == 201
    assert response.json()['message'] == "Uploading Commentaries in background"
    job_response = check_commentary_job_finished(response)
    assert job_response.json()['data']['status'] == 'job finished'
    assert job_response.json()["message"] == "Commentaries added successfully"
    assert 'output' in job_response.json()['data']
    assert len(data) == len(job_response.json()['data']['output']['data'])
    for item in job_response.json()['data']['output']['data']:
        assert_positive_get(item)

    # positive PUT
    new_data = [
        {'bookCode':'mat', 'chapter':1, 'verseStart':1,
        'verseEnd':10, 'commentary':"first verses of matthew"},
        {'bookCode':'mrk','chapter':0, 'commentary':"book intro to Mark"},
    ]
    #without auth
    response = client.put(UNIT_URL+resource_name,headers=headers, json=new_data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Updating Commentaries in background"
    job_response = check_commentary_job_finished(response)
    assert job_response.json()['data']['status'] == 'job finished'
    assert job_response.json()["message"] == "Commentaries updated successfully"
    for i,item in enumerate(job_response.json()['data']['output']['data']):
        assert_positive_get(item)
        assert item['commentary'] == new_data[i]['commentary']
        assert item['book']['bookCode'] == data[i]['bookCode']
        assert item['chapter'] == data[i]['chapter']
        if 'verseEnd' in data[i]:
            assert item['verseStart'] == data[i]['verseStart']
            assert item['verseEnd'] == data[i]['verseEnd']
        # else:
        #     assert item['verseStart'] is None
        #     assert item['verseEnd'] is None

    # not available PUT
    new_data[0]['chapter'] = 2
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    job_response = get_job_status(response.json()['data']['jobId'])
    assert job_response.json()['data']['status'] == 'job error'
    assert job_response.json()["message"] == "Job is terminated with an error"
    assert "message" in job_response.json()["data"]["output"]

    resource_name = resource_name.replace('1', '2')
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=[])
    assert response.status_code == 404

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''

    post_data = [{'bookCode':'gen', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}]
    resp, resource_name = check_post(post_data)
    assert resp.status_code == 201

    # single data object instead of list
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=unused-variable disable=redefined-outer-name
    data = {'bookCode':'gen', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'new commentary'}
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # data object with missing mandatory fields
    data = [
        {'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields

    data = [
        {'bookCode':'genesis', 'chapter':1, 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':'introduction', 'verseStart':1,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':'introduction',
        'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)


    data = [
        {'bookCode':'gen', 'chapter':1, 'verseStart':10,
        "verseEnd":1, 'commentary':'first verse of Genesis'}
    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    resource_name1 = resource_name.replace('commentary', 'bible')
    response = client.put(UNIT_URL+resource_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    resource_name2 = resource_name.replace('1', '2')
    response = client.put(UNIT_URL+resource_name2, headers=headers_auth, json=[])
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

    response, resource_name = check_post(data)
    assert response.json()['message'] == "Uploading Commentaries in background"
    job_response = check_commentary_job_finished(response)
    assert job_response.json()['data']['status'] == 'job finished'
    assert job_response.json()["message"] == "Commentaries added successfully"

    get_response1 = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert len(get_response1.json()) == len(data)
    delete_data[0]['active'] = False

    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=delete_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Updating Commentaries in background"
    job_response = check_commentary_job_finished(response)
    assert job_response.json()['data']['status'] == 'job finished'
    assert job_response.json()["message"] == "Commentaries updated successfully"
    for i,item in enumerate(job_response.json()['data']['output']['data']): #pylint: disable=unused-variable
        assert not item['active']

    get_response2 = client.get(UNIT_URL+resource_name, headers=headers_auth)
    assert len(get_response2.json()) == len(data) - len(delete_data)

    get_response3 = client.get(UNIT_URL+resource_name+'?active=false',headers=headers_auth)
    assert len(get_response3.json()) == len(delete_data)

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
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "commentary",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    #create resource
    response = client.post('/v2/resources', headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource created successfully"
    resource_name = 'ml_TTT_1_commentary'

    #create commentary
    data = [
        {'bookCode':'mat', 'chapter':1, 'verseStart':1,
        'verseEnd':10, 'commentary':"first verses of matthew"},
        {'bookCode':'mrk','chapter':0, 'commentary':"book intro to Mark"},
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Uploading Commentaries in background"
    job_response = check_commentary_job_finished(response)
    assert job_response.json()['data']['status'] == 'job finished'
    assert job_response.json()["message"] == "Commentaries added successfully"

    #update commentary with created SA user
    new_data = [
        {'bookCode':'mat', 'chapter':1, 'verseStart':1,
        'verseEnd':10, 'commentary':"first verses of matthew"},
        {'bookCode':'mrk','chapter':0, 'commentary':"book intro to Mark"},
    ]
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.status_code == 201
    assert response.json()['message'] == "Updating Commentaries in background"
    job_response = check_commentary_job_finished(response)
    assert job_response.json()['data']['status'] == 'job finished'
    assert job_response.json()["message"] == "Commentaries updated successfully"

    #update with VA not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'


def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    data = [
    	{'bookCode':'gen', 'chapter':0, 'commentary':'book intro to Genesis'}
    ]
    contetapi_get_accessrule_checks_app_userroles("commentary",UNIT_URL,data)

def test_delete_default():
    ''' positive test case, checking for correct return of deleted commentary ID'''
    #create new data
    response,resource_name = test_post_default()
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    post_response = client.get(UNIT_URL+resource_name+'?book_code=gen&chapter=0',\
        headers=headers_auth)
    assert post_response.status_code == 200
    assert len(post_response.json()) == 1
    for item in post_response.json():
        assert_positive_get(item)
    commentary_response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    commentary_id = commentary_response.json()[0]['commentaryId']

    #Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    response = client.delete(UNIT_URL+resource_name + "?delete_id=" + str(commentary_id), headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

     #Delete commentary with other API user,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev']:
        headers_au = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL+resource_name + "?delete_id=" + str(commentary_id), headers=headers_au)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete commentary with Vachan Admin
    headers_va = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['VachanAdmin']['token']
            }
    response = client.delete(UNIT_URL+resource_name + "?delete_id=" + str(commentary_id), headers=headers_va)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Commentary id {commentary_id} deleted successfully"
    #Check commentray is deleted from table
    commentary_response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert commentary_response.status_code == 200
    delete_response = client.get(UNIT_URL+resource_name+'?book_code=gen&chapter=0',\
        headers=headers_auth)
    assert_not_available_content(delete_response)

def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted commentary ID'''
    #Created User or Super Admin can only delete commentary
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

    commentary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    commentary_id = commentary_response.json()[0]['commentaryId']
    
     #Delete commentary with Super Admin
    response = client.delete(UNIT_URL+resource_name + "?delete_id=" + str(commentary_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Commentary id {commentary_id} deleted successfully"
    # Check commentray is deleted from table
    commentary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    logout_user(test_user_token)
    return response,resource_name

def test_delete_commentary_id_string():
    '''positive test case, commentary id as string'''
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

    commentary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    commentary_id = commentary_response.json()[0]['commentaryId']
    commentary_id = str(commentary_id)


    #Delete commentary with Super Admin
    response = client.delete(UNIT_URL+resource_name + "?delete_id=" + str(commentary_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Commentary id {commentary_id} deleted successfully"
    #Check commentray is deleted from table
    commentary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
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

    commentary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    commentary_id = commentary_response.json()[0]['commentaryId']
    commentary_id = str(commentary_id)

    commentary_id={}
    #Delete commentary with Super Admin
    response = client.delete(UNIT_URL+resource_name + "?delete_id=" + str(commentary_id), headers=headers_sa)
    assert_input_validation_error(response)
    logout_user(test_user_token)

def test_delete_missingvalue_commentary_id():
    '''Negative Testcase. Passing input data without commentaryId'''
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

    commentary_id=""
    response = client.delete(UNIT_URL+resource_name + "?delete_id=" + str(commentary_id), headers=headers_sa)
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
    commentary_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    commentary_id = commentary_response.json()[0]['commentaryId']
    # commentary_id = str(commentary_id)

    
    
    response = client.delete(UNIT_URL+ "?delete_id=" + str(commentary_id), headers=headers_sa)
    assert response.status_code == 404
    logout_user(test_user_token)

def test_delete_notavailable_content():
    ''' request a non existing content ID, Ensure there is no partial matching'''
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

    
    commentary_id=9999
     #Delete commentary with Super Admin
    response = client.delete(UNIT_URL+resource_name + "?delete_id=" + str(commentary_id), headers=headers_sa)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    logout_user(test_user_token)

def test_restore_default():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response, resource_name = test_delete_default_superadmin() #pylint: disable=unused-variable
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    # Restoring data
    # Restore without authentication
    headers = {"contentType": "application/json", "accept": "application/json"} #pylint: disable=redefined-outer-name
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore commentary with other API user,VachanAdmin,AgAdmin, \
    # AgUser,VachanUser,BcsDev and resoursecreatedUser
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev','APIUser2']:
        headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.put(RESTORE_URL, headers=headers, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    # Restore resource with Super Admin
    # Login as Super Admin
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
    restore_response = client.get(UNIT_URL+resource_name+'?book_code=gen&chapter=0',\
        headers=headers_sa)
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
    #Delete Associated Source
    get_resource_response = client.get(RESOURCE_URL + "?resource_name="+resource_name, headers=headers_auth)
    resource_id = get_resource_response.json()[0]["resourceId"]
    response = client.delete(RESOURCE_URL  + "?delete_id=" + str(resource_id), headers=headers_auth)
    assert response.status_code == 200
    #Restoring data
    #Restore content with Super Admin after deleting resource
    restore_response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    restore_response.status_code = 404
    logout_user(test_user_token)
