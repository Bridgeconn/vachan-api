'''Test cases for versions related APIs'''
from app.schema import schemas, schema_auth
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_versions import check_post as add_version
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER
from .conftest import initial_test_users

UNIT_URL = '/v2/sources'

headers_auth = {"contentType": "application/json",
                "accept": "application/json"
            }

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "sourceName" in item
    assert "contentType" in item
    assert "contentId" in item['contentType']
    assert "contentType" in item['contentType']
    assert "language" in item
    assert "code" in item["language"]
    assert "language" in item['language']
    assert "languageId" in item["language"]
    assert "version" in item
    assert "versionAbbreviation" in item['version']
    assert "versionId" in item['version']
    assert "year" in item
    assert "license" in item
    assert isinstance(item["license"], dict)
    assert "metaData" in item
    assert item['metaData'] is None or isinstance(item['metaData'], dict)
    assert 'accessPermissions' in item['metaData'].keys()
    assert "active" in item
    assert item["active"] in [True, False]
    parts = [item['language']['code'], item['version']['versionAbbreviation'],
        str(item['version']['revision']), item['contentType']['contentType']]
    table_name = "_".join(parts)
    assert item["sourceName"] == table_name


def check_post(data: dict):
    '''common steps for positive post test cases'''
    #without auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    
    #With auth Only vachan and super admin can only create source
    headers_auth['Authorization'] = "Bearer"+" "+ initial_test_users['APIUser']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

    #try with vachanAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']

    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"
    # data = response.json()["data"]
    # print("PERM==>",data['metaData']['accessPermissions'])
    assert_positive_get(response.json()['data'])
    return response

def test_post_default():
    '''Positive test to add a new source'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "CC-BY-SA",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    check_post(data)

def test_post_wrong_version():
    '''Negative test with not available version or revision'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data1 = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTD",
        "revision": 1,
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    #header with auth
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data1)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert response.json()['details'] == "Version, TTD 1, not found in Database"

    data2 = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "revision": 2,
        "year": 2020,
        "license": "CC-BY-SA",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data2)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert response.json()['details'] == "Version, TTT 2, not found in Database"

    data3 = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    check_post(data3)

def test_post_wrong_lang():
    '''Negative test with not available language'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "commentary",
        "language": "aaj",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    #test with auth
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert response.json()['details'] == "Language code, aaj, not found in Database"

def test_post_wrong_content():
    '''Negative test with not available content type'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "bibl",
        "language": "hi",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert response.json()['details'] == "ContentType, bibl, not found in Database"

    # '''Negative test with not a valid license from license table'''
    data = {
        "contentType": "infographic",
        "language": "hi",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "XYZ-123",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert "License" in response.json()['details']

def test_post_wrong_year():
    '''Negative test with text in year field'''
    data = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "revision": 1,
        "year": "twenty twenty",
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)


def test_post_wrong_metadata():
    '''Negative test with incorrect format for metadata'''
    data = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "revision": 1,
        "year": "twenty twenty",
        "license": "ISC",
        "metaData": '["owner"="someone", "access-key"="123xyz"]'
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_post_missing_mandatory_info():
    '''Negative tests with mandatory contents missing'''
    # no contentType
    data = {
        "language": "hi",
        "version": "TTT",
        "revision": 1,
        "year": 2020
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # no language
    data = {
        "contentType": "commentary",
        "version": "TTT",
        "revision": 1,
        "year": 2020
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # no version
    data = {
        "contentType": "commentary",
        "language": "hi",
        "revision": 1,
        "year": 2020
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # no year
    data = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT"
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_post_missing_some_info():
    '''Positive test with non mandatory contents missing.
    If revision not specified, 1 is assumed. Other fields are nullable or have default value'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "year": 2020
    }
    check_post(data)
    # response = client.post(UNIT_URL, headers=headers_auth, json=data)

def test_post_duplicate():
    '''Add the same source twice'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "year": 2020
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    check_post(data)
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

def test_put_default():
    '''Add some data and test updating them'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    version_data['revision'] = 2
    add_version(version_data)
    data = {
        "contentType": "commentary",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    check_post(data)

    data_update = {
        "sourceName": 'ml_TTT_1_commentary',
        "revision": 2
    }
    #update source without auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(UNIT_URL, headers=headers, json=data_update)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    # #with vachan admin who created the data
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']

    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Source edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()['data']['version']['revision'] == 2
    assert response.json()['data']['sourceName'] == "ml_TTT_2_commentary"

    data_update = {
        'sourceName': 'ml_TTT_2_commentary',
        'metaData': {'owner': 'new owner'}
    }
    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Source edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()['data']['metaData'] == \
        {'accessPermissions': [schemas.SourcePermissions.CONTENT], 'owner': 'new owner'}

def test_created_user_can_only_edit():
    """source edit can do by created user and Super Admin"""
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
    version_data['revision'] = 2
    add_version(version_data)
    data = {
        "contentType": "commentary",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    #create source
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"
    assert_positive_get(response.json()['data'])

    data_update = {
        "sourceName": 'ml_TTT_1_commentary',
        "revision": 2
    }

    #edit with SA who also the createdUser
    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Source edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()['data']['version']['revision'] == 2
    assert response.json()['data']['sourceName'] == "ml_TTT_2_commentary"

    #edit with a non permited user VachanAdmin (not createdUser)
    data_update = {
        "sourceName": 'ml_TTT_2_commentary',
        "revision": 1
    }
    
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']

    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

def test_soft_delete():
    '''Soft delete is achived by updating the active flag to Fasle'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
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
    response = check_post(data)
    assert response.json()['data']['active']

    data_update = {
        'sourceName': 'ml_TTT_1_commentary',
        'active': False
    }
    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Source edited successfully"
    assert_positive_get(response.json()['data'])
    assert not response.json()['data']['active']

    response = client.get(UNIT_URL + '?active=False',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) > 0
    for item in response.json():
        assert_positive_get(item)
        assert not item['active']
    assert 'ml_TTT_1_commentary' in [item['sourceName'] for item in response.json()]

def test_get_empty():
    '''Test get before adding data to table. Usually done on freshly set up test DB.
    If the testing is done on a DB that already has some data, the response wont be empty.'''
    response = client.get(UNIT_URL + '?version_abbreviation=TTT')
    if len(response.json()) == 0:
        assert_not_available_content(response)

def test_get_wrong_values():
    '''Checks input validation for query params'''
    response = client.get(UNIT_URL + '?version_abbreviation=1')
    assert_input_validation_error(response)

    response = client.get(UNIT_URL + '?revision=X')
    assert_input_validation_error(response)

    response = client.get(UNIT_URL + '?language_code=hin6i')
    assert_input_validation_error(response)

def test_get_after_adding_data():
    '''Add some sources to DB and test fecthing those data'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "infographic",
        "version": "TTT",
        "year": 2020
    }
    for lang in ['hi', 'mr', 'te']:
        data['language'] = lang
        check_post(data)

    version_data['revision'] = 2
    add_version(version_data)
    data['revision'] = 2
    for lang in ['hi', 'mr', 'te']:
        data['language'] = lang
        check_post(data)

    data['contentType'] = 'commentary'
    data['revision'] = 1
    data['metaData'] = {'owner': 'myself'}
    data['license'] = "ISC"
    for lang in ['hi', 'mr', 'te']:
        data['language'] = lang
        check_post(data)

    check_default_get(UNIT_URL, headers_auth, assert_positive_get)
    #Get sources with and without auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    # filter with contentType
    #without auth
    response = client.get(UNIT_URL + "?content_type=commentary&version_abbreviation=TTT"+
        "&latest_revision=false",headers=headers)
    assert_not_available_content(response)
    #with auth
    response = client.get(UNIT_URL + "?content_type=commentary&version_abbreviation=TTT"+
        "&latest_revision=false",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

    # filter with language
    #without auth
    response = client.get(UNIT_URL + "?language_code=hi&&version_abbreviation=TTT&latest_revision=false")
    assert_not_available_content(response)
    #with auth
    response = client.get(UNIT_URL + "?language_code=hi&&version_abbreviation=TTT"+
        "&latest_revision=false",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

    # filter with revision  #WITH AUTH
    response = client.get(UNIT_URL + "?revision=2&version_abbreviation=TTT",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

    # filter with version
    response = client.get(UNIT_URL + "?version_abbreviation=TTT&latest_revision=false",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 9
    for item in response.json():
        assert_positive_get(item)

    # filter with license
    response = client.get(UNIT_URL + "?license=CC-BY-SA&version_abbreviation=TTT",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 6
    for item in response.json():
        assert_positive_get(item)

    response = client.get(UNIT_URL + "?license=ISC&version_abbreviation=TTT",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

    # filter with metadata
    response = client.get(UNIT_URL + '?metadata={"owner": "myself"}&&version_abbreviation=TTT'+
        '&latest_revision=false',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3
    for item in response.json():
        assert_positive_get(item)

    # filter with revsion and revision
    response = client.get(UNIT_URL + '?version_abbreviation=TTT&revision=1',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

def test_get_source_filter_access_tag():
    """filter source with access tags"""
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "infographic",
        "version": "TTT",
        "year": 2020,
        "accessPermissions": [
            "content"
        ],
    }
    data['language'] = 'hi'
    check_post(data)
    data['language'] = 'mr'
    data['accessPermissions'] = ['open-access']
    check_post(data)
    data['language'] = 'te'
    data['accessPermissions'] = ['publishable']
    check_post(data)
    
    response1 = client.get(UNIT_URL,headers=headers_auth)
    assert response1.status_code == 200
    assert len(response1.json()) == 3
    for item in response1.json():
        assert_positive_get(item)

    response2 = client.get(UNIT_URL + '?version_abbreviation=TTT&access_tag=open-access',headers=headers_auth)
    assert response2.status_code == 200
    assert len(response2.json()) == 1
    for item in response2.json():
        assert_positive_get(item)

    response3 = client.get(UNIT_URL + '?version_abbreviation=TTT&access_tag=publishable',headers=headers_auth)
    assert response3.status_code == 200
    assert len(response3.json()) == 1
    for item in response3.json():
        assert_positive_get(item)

    response4 = client.get(UNIT_URL + '?version_abbreviation=TTT&access_tag=content',headers=headers_auth)
    assert response4.status_code == 200
    assert len(response4.json()) == 3
    for item in response4.json():
        assert_positive_get(item)

    response5 = client.get(UNIT_URL + '?version_abbreviation=TTT&access_tag=publishable&access_tag=open-access',headers=headers_auth)
    assert response5.status_code == 200
    assert len(response5.json()) == 0

    #Add source with access tags publishable , open-access
    data['language'] = 'ho'
    data['accessPermissions'] = ['publishable','open-access']
    check_post(data)

    response6 = client.get(UNIT_URL + '?version_abbreviation=TTT&access_tag=publishable&access_tag=open-access',headers=headers_auth)
    assert response6.status_code == 200
    assert len(response6.json()) == 1
    

def test_diffrernt_sources_with_app_and_roles():
    """Test getting sources with users having different permissions and 
    also from multiple apps"""
    headers_auth = {"contentType": "application/json",
                "accept": "application/json"
            }
    #app names
    API = schema_auth.App.API.value
    AG = schema_auth.App.AG.value
    VACHAN = schema_auth.App.VACHAN.value
    VACHANADMIN = schema_auth.AdminRoles.VACHANADMIN.value

    #create sources for test with different access permissions
    #content is default
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "CC-BY-SA",
        "accessPermissions": [
        "content"
        ],
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = check_post(data)
    resp_data = response.json()['data']['metaData']
    assert ['content'] == resp_data['accessPermissions']

    #open-access
    data["language"] = 'ml'
    data["accessPermissions"] = ['open-access']
    response = check_post(data)
    resp_data = response.json()['data']['metaData']
    assert ['open-access', 'content'] == resp_data['accessPermissions']

    #publishable
    data["language"] = 'tn'
    data["accessPermissions"] = ['publishable']
    response = check_post(data)
    resp_data = response.json()['data']['metaData']
    assert ['publishable', 'content'] == resp_data['accessPermissions']

    #downloadable
    data["language"] = 'af'
    data["accessPermissions"] = ['downloadable']
    response = check_post(data)
    resp_data = response.json()['data']['metaData']
    assert ['downloadable', 'content'] == resp_data['accessPermissions']

    #derivable
    data["language"] = 'ak'
    data["accessPermissions"] = ['derivable']
    response = check_post(data)
    resp_data = response.json()['data']['metaData']
    assert ['derivable', 'content'] == resp_data['accessPermissions']

    def check_resp_permission(response,check_list):
        """function to check permission in response"""
        db_perm_list = []
        for i in range(len(response.json())):
            temp_list = response.json()[i]['metaData']['accessPermissions']
            db_perm_list = db_perm_list + list(set(temp_list)-set(db_perm_list))
        for item in check_list:
            assert item in db_perm_list
        # check based on source
        for item in response.json():
            if item["sourceName"] == "hi_TTT_1_commentary":
                assert "content" in item['metaData']['accessPermissions']
            elif item["sourceName"] == "ml_TTT_1_commentary":
                assert "open-access" in item['metaData']['accessPermissions']
            elif item["sourceName"] == "tn_TTT_1_commentary":
                assert "publishable" in item['metaData']['accessPermissions']
            elif item["sourceName"] == "af_TTT_1_commentary":
                assert "downloadable" in item['metaData']['accessPermissions']
            elif item["sourceName"] == "ak_TTT_1_commentary":
                assert "derivable" in item['metaData']['accessPermissions']            

    #Get without Login
    #default : API
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    resp_data = response.json()[0]['metaData']
    # assert 'open-access' in resp_data['accessPermissions']
    check_list = ["open-access"]
    check_resp_permission(response, check_list)
    #APP : Autographa
    headers_auth['app'] = AG
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)
    #APP : Vachan Online
    headers_auth['app'] = VACHAN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Admin
    headers_auth['app'] = VACHANADMIN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)

    #Get with AgUser
    #default : API
    headers_auth = {"contentType": "application/json","accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Autographa
    headers_auth['app'] = AG
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Online
    headers_auth['app'] = VACHAN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Admin
    headers_auth['app'] = VACHANADMIN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)

    #Get with VachanUser
    #default : API
    headers_auth = {"contentType": "application/json","accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Autographa
    headers_auth['app'] = AG
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)
    #APP : Vachan Online
    headers_auth['app'] = VACHAN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Admin
    headers_auth['app'] = VACHANADMIN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)

    #Get with VachanAdmin
    #default : API
    headers_auth = {"contentType": "application/json","accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 5
    # assert 'content' in response.json()[0]['metaData']['accessPermissions']
    # assert 'open-access' in response.json()[1]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[2]['metaData']['accessPermissions']
    # assert 'downloadable' in response.json()[3]['metaData']['accessPermissions']
    # assert 'derivable' in response.json()[4]['metaData']['accessPermissions']
    check_list = ['open-access','publishable','downloadable','derivable','content']
    check_resp_permission(response, check_list)
    #APP : Autographa
    headers_auth['app'] = AG
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)
    #APP : Vachan Online
    headers_auth['app'] = VACHAN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Admin
    headers_auth['app'] = VACHANADMIN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert len(response.json()) == 5
    # assert 'content' in response.json()[0]['metaData']['accessPermissions']
    # assert 'open-access' in response.json()[1]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[2]['metaData']['accessPermissions']
    # assert 'downloadable' in response.json()[3]['metaData']['accessPermissions']
    # assert 'derivable' in response.json()[4]['metaData']['accessPermissions']
    check_list = ['open-access','publishable','downloadable','derivable','content']
    check_resp_permission(response, check_list)

    #Get with API-User
    #default : API
    headers_auth = {"contentType": "application/json","accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Autographa
    headers_auth['app'] = AG
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)
    #APP : Vachan Online
    headers_auth['app'] = VACHAN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Admin
    headers_auth['app'] = VACHANADMIN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)

    #Get with AgAdmin
    #default : API
    headers_auth = {"contentType": "application/json","accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Autographa
    headers_auth['app'] = AG
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Online
    headers_auth['app'] = VACHAN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Admin
    headers_auth['app'] = VACHANADMIN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)

    #Get with BcsDeveloper
    #default : API
    headers_auth = {"contentType": "application/json","accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 5
    # assert 'content' in response.json()[0]['metaData']['accessPermissions']
    # assert 'open-access' in response.json()[1]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[2]['metaData']['accessPermissions']
    # assert 'downloadable' in response.json()[3]['metaData']['accessPermissions']
    # assert 'derivable' in response.json()[4]['metaData']['accessPermissions']
    check_list = ['open-access','publishable','downloadable','derivable','content']
    check_resp_permission(response, check_list)
    #APP : Autographa
    headers_auth['app'] = AG
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)
    #APP : Vachan Online
    headers_auth['app'] = VACHAN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Admin
    headers_auth['app'] = VACHANADMIN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)

    #Super Admin
    SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(SA_user_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]

    #Get with SA Admin
    #default : API
    headers_auth = {"contentType": "application/json","accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+ test_user_token
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 5
    # assert 'content' in response.json()[0]['metaData']['accessPermissions']
    # assert 'open-access' in response.json()[1]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[2]['metaData']['accessPermissions']
    # assert 'downloadable' in response.json()[3]['metaData']['accessPermissions']
    # assert 'derivable' in response.json()[4]['metaData']['accessPermissions']
    check_list = ['open-access','publishable','downloadable','derivable','content']
    check_resp_permission(response, check_list)
    #APP : Autographa
    headers_auth['app'] = AG
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Online
    headers_auth['app'] = VACHAN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Vachan Admin
    headers_auth['app'] = VACHANADMIN
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 5
    # assert 'content' in response.json()[0]['metaData']['accessPermissions']
    # assert 'open-access' in response.json()[1]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[2]['metaData']['accessPermissions']
    # assert 'downloadable' in response.json()[3]['metaData']['accessPermissions']
    # assert 'derivable' in response.json()[4]['metaData']['accessPermissions']
    check_list = ['open-access','publishable','downloadable','derivable','content']
    check_resp_permission(response, check_list)