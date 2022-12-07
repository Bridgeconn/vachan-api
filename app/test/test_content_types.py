'''Test cases for contentType related APIs'''
import json
from sqlalchemy.orm import Session
from database import SessionLocal
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_auth_basic import SUPER_USER,SUPER_PASSWORD, login, logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/contents'
RESTORE_URL = '/v2/restore'

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

def populate_db(db_ : Session): # pylint: disable=C0116
    db_.execute('''INSERT INTO content_types(content_type) \
    VALUES ('testdata')''')
    db_.commit()
    content_id = db_.execute('''SELECT content_type_id FROM content_types \
    WHERE (content_type = 'testdata')''')
    db_.commit()
    [test_content_id] = content_id.fetchone()
    test_id = test_content_id
    return test_id

def delete_db(db_ : Session): # pylint: disable=C0116
    db_.execute('''DELETE FROM content_types WHERE content_type = 'testdata' ''')
    db_.commit()
    test_id = populate_db(db_=db_)
    data = {'contentType': "testdata", 'contentId': test_id}
    del_data = json.dumps(data)
    db_.execute(f'''INSERT INTO deleted_items(deleted_data,deleted_user,deleted_from) \
    VALUES('{del_data}','registred_user','content_types')''')
    db_.commit()
    deleted_item_id = db_.execute('''SELECT item_id FROM deleted_items \
    WHERE (deleted_data::text LIKE '%test%')''')
    db_.commit()
    [deleted_id] = deleted_item_id.fetchone()
    db_.execute(f'''DELETE FROM content_types WHERE content_type_id = {test_id}''')
    db_.commit()
    return deleted_id

def test_delete_default():
    ''' positive test case, checking for correct return of deleted content ID'''
    db_= SessionLocal()
    t_id = populate_db(db_=db_)
    data = {"contentId":t_id}
    #Registerd User can only delete content type
    #Delete content without auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Delete content with auth
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == f"Content with identity {t_id} deleted successfully"

def test_delete_content_id_string():
    '''positive test case, content id as string'''
    db_= SessionLocal()
    db_.execute('''DELETE FROM content_types WHERE content_type= 'testdata' ''')
    db_.commit()
    t_id = populate_db(db_=db_)
    testid = str(t_id)
    data = {"contentId":testid}
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == f"Content with identity {t_id} deleted successfully"

def test_delete_incorrectdatatype():
    '''the input data object should a json with "contentId" key within it'''
    db_= SessionLocal()
    db_.execute('''DELETE FROM content_types WHERE content_type= 'testdata' ''')
    db_.commit()
    test_id = populate_db(db_=db_)
    data = test_id
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_delete_missingvalue_content_id():
    '''contentId is mandatory in input data object'''
    data = {}
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_delete_notavailable_content_id():
    ''' request a non existing content ID, Ensure there is no partial matching'''
    data = {"contentId":1000}
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL,headers=headers,json=data)
    assert response.status_code == 502
    assert response.json()['error'] == "Database Error"

def test_restore_default():
    '''positive test case, checking for correct return object'''
    db_= SessionLocal()
    deleted_item_id = delete_db(db_=db_)
    data = {"itemId": deleted_item_id}
    #Add content with auth
    #Super Admin can only restore data
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
    response = client.post(RESTORE_URL, headers=headers_admin, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleted_item_id} restored successfully"
    logout_user(token_admin)

def test_restore_incorrect_login():
    '''negative test case, login withouth authentication'''
    db_= SessionLocal()
    deleted_item_id = delete_db(db_=db_)
    data = {"itemId": deleted_item_id}
    #Add test without login
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

def test_restore_item_id_string():
    '''positive test case, item id as string'''
    db_= SessionLocal()
    deleted_item_id = delete_db(db_=db_)
    item_id = str(deleted_item_id)
    data = {"itemId": item_id}
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
    response = client.post(RESTORE_URL, headers=headers_admin, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {item_id} restored successfully"
    logout_user(token_admin)

def test_restore_incorrectdatatype():
    '''the input data object should a json with "itemId" key within it'''
    db_= SessionLocal()
    deleted_item_id = delete_db(db_=db_)
    data = deleted_item_id
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
    response = client.post(RESTORE_URL, headers=headers_admin, json=data)
    assert_input_validation_error(response)
    logout_user(token_admin)

def test_restore_missingvalue_contenttype():
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
    response = client.post(RESTORE_URL, headers=headers_admin, json=data)
    assert_input_validation_error(response)
    logout_user(token_admin)
