'''Test cases for language related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_auth_basic import SUPER_USER,SUPER_PASSWORD, login, logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/languages'
RESTORE_URL = '/v2/restore'
VERSION_URL = '/v2/versions'
SOURCE_URL = '/v2/sources'

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "languageId" in item
    assert isinstance(item['languageId'], int)
    assert "language" in item
    assert "code" in item
    assert "scriptDirection" in item
    if "metaData" in item and item['metaData'] is not None:
        assert isinstance(item['metaData'], dict)

def test_get_default():
    '''positive test case, without optional params'''
    headers = {"contentType": "application/json", "accept": "application/json"}
    check_default_get(UNIT_URL, headers,assert_positive_get)

def test_get_language_code():
    '''positive test case, with one optional params, code wihtout registered user'''
    response = client.get(UNIT_URL+'?language_code=hi')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'hi'

    #with registred user header
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.get(UNIT_URL+'?language_code=hi',headers=headers_auth)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'hi'


def test_get_language_code_upper_case():
    '''positive test case, with one optional params, code in upper case'''
    response = client.get(UNIT_URL+'?language_code=HI')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'hi'

def test_get_language_name():
    '''positive test case, with one optional params, name'''
    response = client.get(UNIT_URL+'?language_name=hindi')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['language'].lower() == 'hindi'

def test_get_language_name_mixed_case():
    '''positive test case, with one optional params, name, with first letter capital'''
    response = client.get(UNIT_URL+'?language_name=Hindi')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['language'].lower() == 'hindi'

def test_get_multiple_params():
    '''positive test case, with two optional params'''
    response = client.get(UNIT_URL+'?language_name=hindi&language_code=hi')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['language'].lower() == 'hindi'
    assert response.json()[0]['code'] == 'hi'

def test_get_notavailable_language():
    ''' request a not available language, with code'''
    response = client.get(UNIT_URL+"?language_code=aaj")
    assert_not_available_content(response)

def test_get_notavailable_language2():
    ''' request a not available language, with language name'''
    response = client.get(UNIT_URL+"?language_name=not-a-language")
    assert_not_available_content(response)

def test_get_incorrectvalue_language_code():
    '''language code should be letters'''
    response = client.get(UNIT_URL+"?language_code=110")
    assert_input_validation_error(response)

def test_get_incorrectvalue_language_code2():
    '''language code should have exactly 3 letters'''
    response = client.get(UNIT_URL+"?language_code='abcd.10'")
    assert_input_validation_error(response)

def test_post_default():
    '''positive test case, checking for correct return object'''
    data = {
      "language": "new-lang",
      "code": "x-aaj",
      "scriptDirection": "left-to-right"
    }
    #Add Language without Auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Add with Auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "x-aaj"
    return response

def test_post_upper_case_code():
    '''positive test case, checking for case conversion of code'''
    data = {
      "language": "new-lang",
      "code": "X-AAJ",
      "scriptDirection": "left-to-right"
    }
    #Add Language without Auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Add with Auth
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "X-AAJ"

def test_post_optional_script_direction():
    '''positive test case, checking for correct return object'''
    data = {
      "language": "new-lang",
      "code": "x-aaj"
    }
    #Add without Auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Add with Auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "x-aaj"


def test_post_incorrectdatatype1():
    '''code should have letters only'''
    data = {
      "language": "new-lang",
      "code": "123",
      "scriptDirection": "left-to-right"
    }
    #Add with Auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_incorrectdatatype2():
    '''scriptDirection should be either left-to-right or right-to-left'''
    data = {
      "language": "new-lang",
      "code": "MMM",
      "scriptDirection": "regular"
    }
    #Add with Auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_missingvalue_language():
    '''language name should be present'''
    data = {
      "code": "MMM",
      "scriptDirection": "left-to-right"
    }
    #Add with Auth
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_put_languages():
    """put test for languages"""
    #create a new langauge
    data = {
      "language": "new-lang-test",
      "code": "x-abc"
    }
    #Add with Auth
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "x-abc"

    #get language id
    response = client.get(UNIT_URL+'?language_code=x-abc')
    assert response.status_code == 200
    language_id = response.json()[0]['languageId']

    #edit with created user
    data = {
      "languageId": language_id,
      "language": "new-lang-test-edited",
      "code": "x-abc"
    }
    response = client.put(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["language"] == "new-lang-test-edited"

    # #delete the user
    # delete_user_identity(test_user_id)

    #edit without login
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == "Authentication Error"

    #create a new user and edit the previous user created content
    headers_auth2 = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser']['token']
            }
    response = client.put(UNIT_URL, headers=headers_auth2, json=data)
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

    #super admin can edit the content
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']

    data = {
      "languageId": language_id,
      "language": "new-lang-test-edited-by-admin",
      "code": "x-abc"
    }
    headers_admin = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
            }
    response = client.put(UNIT_URL, headers=headers_admin, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["language"] == "new-lang-test-edited-by-admin"

    logout_user(token_admin)

def test_searching():
    '''Being able to query languages with code, name, country of even other info'''

    response = client.get(UNIT_URL+"?search_word=ml")
    assert len(response.json()) > 0
    found = False
    for lang in response.json():
        assert_positive_get(lang)
        if lang['code'] == "ml":
            found = True
    assert found

    response = client.get(UNIT_URL+"?search_word=india")
    assert len(response.json()) > 0
    found = False
    for lang in response.json():
        assert_positive_get(lang)
        if lang['code'] == "hi":
            found = True
    assert found
    response = client.get(UNIT_URL+"?search_word=sri%20lanka")
    assert len(response.json()) > 0
    found = False
    for lang in response.json():
        assert_positive_get(lang)
        if lang['language'] == "Sinhala":
            found = True
    assert found

    # search word with special symbols in them
    response = client.get(UNIT_URL+"?search_word=sri%20lanka(Asia)")
    assert len(response.json()) > 0
    found = False
    for lang in response.json():
        assert_positive_get(lang)
        if lang['language'] == "Sinhala":
            found = True
    assert found

    response = client.get(UNIT_URL+"?search_word=sri-lanka-asia!")
    assert len(response.json()) > 0
    found = False
    for lang in response.json():
        assert_positive_get(lang)
        if lang['language'] == "Sinhala":
            found = True
    assert found

    # ensure search words are not stemmed as per rules of english
    response = client.get(UNIT_URL+"?search_word=chinese")
    assert len(response.json()) > 5

def test_delete_default():
    ''' positive test case, checking for correct return of deleted language ID'''
    #create new data
    response = test_post_default()
    language_id = response.json()["data"]["languageId"]

    data = {"itemId":language_id}

    #Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

     #Delete language with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev']:
        headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL, headers=headers, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete language with item created API User
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Language with identity {language_id} deleted successfully"
    #Check language is deleted from languages table
    check_language_code = client.get(UNIT_URL+"?language_code=x-aaj")
    assert_not_available_content(check_language_code)

def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted language ID'''
    #Created User or Super Admin can only delete language
    #creating data
    response = test_post_default()
    language_id = response.json()['data']['languageId']
    data = {"itemId":language_id}

    #Delete language with Super Admin
     #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    #Delete language
    response = client.delete(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == \
    f"Language with identity {language_id} deleted successfully"
    logout_user(test_user_token)
    return response

def test_delete_language_id_string():
    '''positive test case, language id as string'''
    response = test_post_default()
    #Deleting created data
    language_id = response.json()['data']['languageId']
    language_id = str(language_id)
    data = {"itemId":language_id}
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    response = client.delete(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 200
    assert response.json()['message'] == \
         f"Language with identity {language_id} deleted successfully"
    logout_user(test_user_token)

def test_delete_incorrectdatatype():
    '''negative testcase. Passing input data not in json format'''
    response = test_post_default()
    #Deleting created data
    language_id = response.json()['data']['languageId']
    data = language_id
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_delete_missingvalue_language_id():
    '''Negative Testcase. Passing input data without languageId'''
    data = {}
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_delete_notavailable_language():
    ''' request a non existing content ID, Ensure there is no partial matching'''
    data = {"itemId":20000}
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL,headers=headers,json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"

def test_language_used_by_source():
    '''  Negativetest case, trying to delete that language which is used to create a source'''
    #create new data
    response = test_post_default()
    print("AFTER POST",response.json())
    language_id = response.json()["data"]["languageId"]
    print("Lang ID :",language_id)

    response = client.get(UNIT_URL+"?language_code=x-aaj")
    print("AFTER GET",response.json())
    language_code = response.json()[0]["code"]

    #create new source as SuperAdmin
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                     }
    #Create Version with associated with source
    version_data = {
        "versionAbbreviation": "KJV",
        "versionName": "King James Version",
        "revision": 1,
        "metaData": {
            "publishedIn": "1611"
            }
        }
    response = client.post(VERSION_URL, headers=headers_auth, json=version_data)
    print("AFTER CREATE VERSION",response.json())
    assert response.status_code == 201
    assert response.json()['message'] == "Version created successfully"

    source_data = {
        "contentType": "commentary",
        "language": language_code,
        "version": "KJV",
        "revision": 1,
        "year": 2020,
        "license": "ISC"
    }
    #Create Source with created language
    response = client.post(SOURCE_URL, headers=headers_auth, json=source_data)
    print("AFTER CREATE SOURCE",response.json())
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"
    logout_user(token_admin)

    #Delete language with item created API User
    data = {"itemId":language_id}
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['APIUser2']['token']
            }
    response = client.delete(UNIT_URL, headers=headers, json=data)
    print("AFTER DELETE LANGUAGE",response.json())
    assert response.status_code == 409
    assert response.json()['error'] == 'Already Exists'

def test_restore_default():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deelting data
    response = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring data
    #Restore without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore language with other API user,VachanAdmin,AgAdmin, \
    # AgUser,VachanUser,BcsDev and resoursecreatedUser
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev','APIUser2']:
        headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

    #Restore language with Super Admin
    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleteditem_id} restored successfully"
    logout_user(test_user_token)
    assert_positive_get(response.json()['data'])

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
    headers_auth = {"contentType": "application/json",
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
    headers_auth = {"contentType": "application/json",
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
