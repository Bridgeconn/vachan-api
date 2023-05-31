'''Test cases for infographics related APIs'''
from . import client , contetapi_get_accessrule_checks_app_userroles
from . import check_default_get, check_soft_delete
from . import assert_input_validation_error, assert_not_available_content
from .test_versions import check_post as add_version
from .test_sources import check_post as add_source
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/infographics/'
SOURCE_URL = '/v2/sources'
RESTORE_URL = '/v2/restore'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "book" in item
    assert "bookId" in item['book']
    assert "bookCode" in item['book']
    assert "title" in item
    assert "infographicLink" in item

def check_post(data: list):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for infographic",
    }
    add_version(version_data)
    source_data = {
        "contentType": "infographic",
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
    '''Positive test to upload infographics'''
    data = [
    	{'bookCode':'gen', 'title':"creation", "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'gen', 'title':"abraham's family",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'exo', 'title':"Isarel's travel routes",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"the Gods reveals himself in new testament",
        "infographicLink":"http://somewhere.com/something"},
    ]
    response,source_name = check_post(data)
    assert response.status_code == 201
    assert response.json()['message'] == "Infographics added successfully"
    for item in response.json()['data']:
        assert_positive_get(item)
    assert len(data) == len(response.json()['data'])
    return response,source_name

def test_post_duplicate():
    '''Negative test to add two infographics Links with same book and title'''
    data = [
        {'bookCode':'rev', 'title':"the Gods reveals himself in new testament",
        "infographicLink":"http://somewhere.com/something"}
    ]
    resp, source_name = check_post(data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Infographics added successfully"

    headers = {"contentType": "application/json", "accept": "application/json"}
    data[0]['infographicLink'] = 'http://anotherplace/item'
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    data = {'bookCode':'mat', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"http://somewhere.com/something"}
    resp, source_name = check_post(data)
    assert_input_validation_error(resp)

    # data object with missing mandatory fields
    headers = {"contentType": "application/json", "accept": "application/json"}
    data = [
        {'bookCode':'mat',
        "infographicLink":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'title':"the Geneology of Jesus Christ",
        "infographicLink":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields

    data = [
        {'bookCode':'mat ', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mathew', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"not a url"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)


    data = [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"noProtocol.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    source_name1 = source_name.replace('infographic', 'info')
    data = []
    response = client.post(UNIT_URL+source_name1, headers=headers_auth, json=data)
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '11')
    response = client.post(UNIT_URL+source_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_get_after_data_upload():
    '''Add some infographics data into the table and do all get tests'''
    data = [
        {'bookCode':'gen', 'title':"creation",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'gen', 'title':"Noah's Ark",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'gen', 'title':"abraham's family",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'exo', 'title':"Isarel's travel routes",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'act', 'title':"Paul's travel routes",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"the Gods reveals himself in new testament",
        "infographicLink":"http://somewhere.com/something"}
    ]
    res, source_name = check_post(data)
    assert res.status_code == 201
    # headers = {"contentType": "application/json", "accept": "application/json"}
    check_default_get(UNIT_URL+source_name, headers_auth,assert_positive_get)

    #filter by book
    #without auth
    response = client.get(UNIT_URL+source_name+'?book_code=gen')
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"
    #with auth
    response = client.get(UNIT_URL+source_name+'?book_code=gen',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.get(UNIT_URL+source_name+'?book_code=exo',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with title introductions
    response = client.get(UNIT_URL+source_name+'?title=creation',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # both title and book
    response = client.get(UNIT_URL+source_name+"?book_code=gen&title=Noah's%20Ark",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # not available
    response = client.get(UNIT_URL+source_name+'?book_code=mat',headers=headers_auth)
    assert_not_available_content(response)

    response = client.get(UNIT_URL+source_name+'?book_code=rev&title=vision',headers=headers_auth)
    assert_not_available_content(response)

def test_get_incorrect_data():
    '''Check for input validations in get'''
    source_name = 'ur_TTT'
    response = client.get(UNIT_URL+source_name,headers=headers_auth)
    assert_input_validation_error(response)

    source_name = 'ur_TTT_1_infographic'
    response = client.get(UNIT_URL+source_name+'?book_code=60',headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?book_code=mark',headers=headers_auth)
    assert_input_validation_error(response)

    resp, source_name = check_post([])
    assert resp.status_code == 201
    source_name = source_name.replace('infographic', 'graphics')
    response = client.get(UNIT_URL+source_name, headers=headers_auth)
    assert response.status_code == 404

def test_put_after_upload():
    '''Positive tests for put'''
    data = [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhere.com/something"}
    ]
    response, source_name = check_post(data)
    assert response.status_code == 201

    # positive PUT
    new_data = [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://anotherplace.com/something"},
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhereelse.com/something"}
    ]
    # headers = {"contentType": "application/json", "accept": "application/json"}
    #without auth
    response = client.put(UNIT_URL+source_name,headers=headers, json=new_data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Infographics updated successfully'
    for i,item in enumerate(response.json()['data']):
        assert_positive_get(item)
        assert response.json()['data'][i]['infographicLink'] == new_data[i]['infographicLink']
        assert response.json()['data'][i]['book']['bookCode'] == data[i]['bookCode']
        assert response.json()['data'][i]['title'] == data[i]['title']

    # not available PUT
    new_data[0]['bookCode'] = 'mrk'
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=new_data)
    assert response.status_code == 404

    source_name = source_name.replace('1', '10')
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''

    post_data = [
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"}
    ]
    resp, source_name = check_post(post_data)
    assert resp.status_code == 201

    # single data object instead of list
    headers = {"contentType": "application/json", "accept": "application/json"}
    data =  {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://anotherplace.com/something"}
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # data object with missing mandatory fields
    data = [
        {'title':"12 apostles",
        "infographicLink":"http://anotherplace.com/something"}
            ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mat',
        "infographicLink":"http://somewhere.com/something"}    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields

    data = [
         {'bookCode':'41', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"}   ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"filename.txt"}    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mat ', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"}    ]
    response = client.put(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    source_name1 = source_name.replace('infographic', 'graphics')
    response = client.put(UNIT_URL+source_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '10')
    response = client.put(UNIT_URL+source_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_soft_delete():
    '''check soft delete in infographics'''
    data = [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"Words of Jesus",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"7 churches of Asia Minor",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"Creatures in Heaven",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"All the Sevens",
        "infographicLink":"http://somewhere.com/something"}
    ]

    delete_data = [
        {'bookCode':'rev', 'title':"Creatures in Heaven"},
        {'bookCode':'rev', 'title':"All the Sevens"}
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
        "contentType": "infographic",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    #create source
    response = client.post('/v2/sources', headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"
    source_name = response.json()['data']['sourceName']
    
    #create infographics
    data = [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers_auth, json=data)
    assert response.status_code == 201

    #update infographics with created SA user
    new_data = [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://anotherplace.com/something"},
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhereelse.com/something"}]
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Infographics updated successfully'

    #update with VA not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.put(UNIT_URL+source_name,headers=headers_auth, json=new_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'  

def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    data = [
    	{'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"}
    ]
    contetapi_get_accessrule_checks_app_userroles("infographic",UNIT_URL,data)

def test_delete_default():
    ''' positive test case, checking for correct return of deleted infographic ID'''
    #create new data
    response,source_name = test_post_default()
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    post_response = client.get(UNIT_URL+source_name+"?book_code=gen&title=creation",\
        headers=headers_auth)
    assert post_response.status_code == 200
    assert len(post_response.json()) == 1
    for item in post_response.json():
        assert_positive_get(item)
    infographic_response = client.get(UNIT_URL+source_name,headers=headers_auth)
    infographic_id = infographic_response.json()[0]['infographicId']
    data = {
      "itemId":infographic_id
    }

    #Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    response = client.delete(UNIT_URL+source_name, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

     #Delete infpgraphic with other API user,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev']:
        headers_au = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL+source_name, headers=headers_au, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete infographic with Vachan Admin
    headers_va = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['VachanAdmin']['token']
            }
    response = client.delete(UNIT_URL+source_name, headers=headers_va, json=data)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Infographic id {infographic_id} deleted successfully"
    infographic_response = client.get(UNIT_URL+source_name,headers=headers_auth)
    assert infographic_response.status_code == 200
    #Check infographic is deleted from table
    delete_response = client.get(UNIT_URL+source_name+"?book_code=gen&title=creation",\
        headers=headers_auth)
    assert_not_available_content(delete_response)

def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted infographic ID'''
    #Created User or Super Admin can only delete infographic
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

    infographic_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    infographic_id = infographic_response.json()[0]['infographicId']

    data = {
      "itemId":infographic_id
    }

     #Delete infographic with Super Admin
    response = client.delete(UNIT_URL+source_name, headers=headers_sa, json=data)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Infographic id {infographic_id} deleted successfully"
    #Check infographic is deleted from table
    infographic_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    logout_user(test_user_token)
    return response,source_name

def test_delete_infographic_id_string():
    '''positive test case, infographic id as string'''
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

    infographic_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    infographic_id = infographic_response.json()[0]['infographicId']
    infographic_id = str(infographic_id)

    data = {
      "itemId":infographic_id
    }

    #Delete infographic with Super Admin
    response = client.delete(UNIT_URL+source_name, headers=headers_sa, json=data)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Infographic id {infographic_id} deleted successfully"
    #Check infographic infographic is deleted from table
    infographic_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    logout_user(test_user_token)

def test_delete_incorrectdatatype():
    '''negative testcase. Passing input data not in json format'''
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

    infographic_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    infographic_id = infographic_response.json()[0]['infographicId']
    data = infographic_id

    #Delete infographic with Super Admin
    response = client.delete(UNIT_URL+source_name, headers=headers_sa, json=data)
    assert_input_validation_error(response)
    logout_user(test_user_token)

def test_delete_missingvalue_infographic_id():
    '''Negative Testcase. Passing input data without infographicId'''
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

    data = {"sourceName":source_name}
    response = client.delete(UNIT_URL, headers=headers_sa, json=data)
    assert response.status_code == 404
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
    infographic_response = client.get(UNIT_URL+source_name,headers=headers_sa)
    infographic_id = infographic_response.json()[0]['infographicId']
    data = {"itemId":infographic_id}
    response = client.delete(UNIT_URL, headers=headers_sa, json=data)
    assert response.status_code == 404
    logout_user(test_user_token)

def test_delete_notavailable_content():
    ''' request a non existing infographic ID, Ensure there is no partial matching'''
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

    data = {
      "itemId":99999
    }

     #Delete infographic with Super Admin
    response = client.delete(UNIT_URL+source_name, headers=headers_sa, json=data)
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
    restore_response =  client.get(UNIT_URL+source_name+"?book_code=gen&title=creation",\
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
    source_data = {"itemId":source_id}
    response = client.delete(SOURCE_URL, headers=headers_auth, json=source_data)
    assert response.status_code == 200
    #Restoring data
    #Restore content with Super Admin after deleting source
    restore_response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    restore_response.status_code = 404
    logout_user(test_user_token)

