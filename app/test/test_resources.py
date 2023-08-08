'''Test cases for versions related APIs'''
import re
from app.schema import schemas, schema_auth
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_versions import check_post as add_version
from .test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/resources'
RESTORE_URL = '/v2/admin/restore'
COMMENTARY_URL = '/v2/commentaries/'

headers_auth = {"contentType": "application/json",
                "accept": "application/json"
            }

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "resourceName" in item
    assert "resourceType" in item
    assert "resourcetypeId" in item['resourceType']
    assert "resourceType" in item['resourceType']
    assert "language" in item
    assert "code" in item["language"]
    assert "language" in item['language']
    assert "languageId" in item["language"]
    if "localScriptName" in item["language"]:
        assert item['language']['localScriptName'] is None or \
            isinstance(item['language']['localScriptName'], str)
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
    if item['version']['versionTag'] is None:
        tag = "1"
    elif isinstance(item['version']['versionTag'], list):
        tag = ".".join(item['version']['versionTag'])
        # tag = re.sub(r'(\.0)+$', "", tag)
    elif isinstance(item['version']['versionTag'], int):
        tag = str(item['version']['versionTag'])
    elif isinstance(item['version']['versionTag'], str):
        if item['version']['versionTag'].startswith("["):
            items = item['version']['versionTag'][1:-1].split(",")
            tag = ".".join([itm.strip() for itm in items])
            tag = re.sub(r"'", "", tag)
        else:
            tag = item['version']['versionTag']
    parts = [item['language']['code'], item['version']['versionAbbreviation'],
        tag, item['resourceType']['resourceType']]
    table_name = "_".join(parts)
    assert item["resourceName"] == table_name


def check_post(data: dict):
    '''common steps for positive post test cases'''
    #without auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #With auth Only vachan and super admin can only create resource
    headers_auth['Authorization'] = "Bearer"+" "+ initial_test_users['APIUser']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

    #try with vachanAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']

    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource created successfully"
    # data = response.json()["data"]
    # print("PERM==>",data['metaData']['accessPermissions'])
    assert_positive_get(response.json()['data'])
    return response

def test_post_default():
    '''Positive test to add a new resource'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
        "labels": ["latest"],
        "year": 2020,
        "license": "CC-BY-SA",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    create_resource = check_post(data)
    assert create_resource.json()['data']['labels'] == ["latest"]
    return create_resource

def test_post_wrong_version():
    '''Negative test with not available version or versionTag'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data1 = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTD",
        "versionTag": 1,
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
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT",
        "versionTag": 2,
        "year": 2020,
        "license": "CC-BY-SA",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data2)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert response.json()['details'] == "Version, TTT 2, not found in Database"

    data3 = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
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
        "resourceType": "commentary",
        "language": "aaj",
        "version": "TTT",
        "versionTag": 1,
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
    '''Negative test with not available resource type'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "bibl",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert response.json()['details'] == "ResourceType, bibl, not found in Database"

    # '''Negative test with not a valid license from license table'''
    data = {
        "resourceType": "vocabulary",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
        "year": 2020,
        "license": "XYZ-123",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert "License" in response.json()['details']

def test_post_wrong_label():
    '''Negative test with invalid label'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "bible",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
        "labels": ["testlabel"],
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_post_multiple_labels():
    '''Positive test  case to add multiple labels'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "bible",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
        "labels": ["latest","test"],
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    headers_auth = {"contentType": "application/json", "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()['data']['labels'] == ["latest","test"]

def test_post_wrong_label_format():
    '''Negative test case to labe in incorrect format.'''
    # Label(s) should pass as a list of strings
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "bible",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
        "labels": "latest",
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)


def test_post_wrong_year():
    '''Negative test with text in year field'''
    data = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
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
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
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
        "versionTag": 1,
        "year": 2020
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # no language
    data = {
        "resourceType": "commentary",
        "version": "TTT",
        "versionTag": 1,
        "year": 2020
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # no version
    data = {
        "resourceType": "commentary",
        "language": "hi",
        "versionTag": 1,
        "year": 2020
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # no year
    data = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT"
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_post_missing_some_info():
    '''Positive test with non mandatory contents missing.
    If versionTag not specified, 1 is assumed. Other fields are nullable or have default value'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT",
        "year": 2020
    }
    check_post(data)

def test_post_duplicate():
    '''Add the same resource twice'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT",
        "year": 2020
    }
    headers = {"contentType": "application/json", "accept": "application/json"} #pylint: disable=unused-variable
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
    version_data['versionTag'] = 2
    add_version(version_data)
    data = {
        "resourceType": "commentary",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    check_post(data)

    data_update = {
        "resourceName": 'ml_TTT_1_commentary',
        "versionTag": 2
    }
    #update resource without auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(UNIT_URL, headers=headers, json=data_update)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    # #with vachan admin who created the data
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']

    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()['data']['version']['versionTag'] == "2"
    assert response.json()['data']['resourceName'] == "ml_TTT_2_commentary"

    data_update = {
        'resourceName': 'ml_TTT_2_commentary',
        'metaData': {'owner': 'new owner'}
    }
    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()['data']['metaData'] == \
        {'accessPermissions': [schemas.ResourcePermissions.CONTENT], 'owner': 'new owner'}

    # updating label
    data_update = {
        'resourceName': 'ml_TTT_2_commentary',
        'labels': ["test"]
    }
    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()['data']['labels'] == ["test"]

def test_post_put_gitlab_resource():
    '''Positive test for gitlab resource type'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "gitlabrepo",
        "language": "hi",
        "version": "TTT",
        "year": 2020
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']

    # error for no repo link in metadata
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 422

    link ="https://gitlab/project/video"
    link2 = "https://gitlab/project/videoNew"
    data["metaData"] = {"repo":link}

    # with repo link default branch is main
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource created successfully"
    assert response.json()['data']["metaData"]["repo"] == link
    assert response.json()['data']["metaData"]["defaultBranch"] == "main"

    # create another resource with same repo link
    data["language"] = "ml"
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 409
    assert response.json()['details'] == "already present Resource with same repo link"

    # update another resource with exising repo link
    data["language"] = "af"
    data["metaData"] = {"repo":link2}
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource created successfully"
    assert response.json()['data']["metaData"]["repo"] == link2

    data_update = {
        "resourceName": 'af_TTT_1_gitlabrepo',
        "metaData": {
            "repo": link}
    }

    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 409
    assert response.json()['details'] == "already present another resource with same repo link"


def test_created_user_can_only_edit():
    """resource edit can do by created user and Super Admin"""
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
    version_data['versionTag'] = 2
    add_version(version_data)
    data = {
        "resourceType": "commentary",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    #create resource
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource created successfully"
    assert_positive_get(response.json()['data'])

    data_update = {
        "resourceName": 'ml_TTT_1_commentary',
        "versionTag": 2
    }

    #edit with SA who also the createdUser
    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()['data']['version']['versionTag'] == "2"
    assert response.json()['data']['resourceName'] == "ml_TTT_2_commentary"

    #edit with a non permited user VachanAdmin (not createdUser)
    data_update = {
        "resourceName": 'ml_TTT_2_commentary',
        "versionTag": 1
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
        "resourceType": "commentary",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    response = check_post(data)
    assert response.json()['data']['active']

    data_update = {
        'resourceName': 'ml_TTT_1_commentary',
        'active': False
    }
    response = client.put(UNIT_URL, headers=headers_auth, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource edited successfully"
    assert_positive_get(response.json()['data'])
    assert not response.json()['data']['active']

    response = client.get(UNIT_URL + '?active=False',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) > 0
    for item in response.json():
        assert_positive_get(item)
        assert not item['active']
    assert 'ml_TTT_1_commentary' in [item['resourceName'] for item in response.json()]

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

    response = client.get(UNIT_URL + '?language_code=hin6i')
    assert_input_validation_error(response)

def test_get_after_adding_data(): #pylint: disable=too-many-statements
    '''Add some resources to DB and test fecthing those data'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "vocabulary",
        "version": "TTT",
        "year": 2020
    }
    for lang in ['hi', 'mr', 'te']:
        data['language'] = lang
        check_post(data)

    version_data['versionTag'] = 2
    add_version(version_data)
    data['versionTag'] = 2
    for lang in ['hi', 'mr', 'te']:
        data['language'] = lang
        check_post(data)

    data['resourceType'] = 'commentary'
    data['versionTag'] = 1
    data['metaData'] = {'owner': 'myself'}
    data['license'] = "ISC"
    for lang in ['hi', 'mr', 'te']:
        data['language'] = lang
        check_post(data)

    check_default_get(UNIT_URL, headers_auth, assert_positive_get)
    #Get resources with and without auth
    headers = {"contentType": "application/json", "accept": "application/json"}
    # filter with contentType
    #without auth
    response = client.get(UNIT_URL + "?resource_type=commentary&version_abbreviation=TTT"+
        "&latest_revision=false",headers=headers)
    assert_not_available_content(response)
    #with auth
    response = client.get(UNIT_URL + "?resource_type=commentary&version_abbreviation=TTT"+
        "&latest_revision=false",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

    # filter with language
    #without auth
    response = client.get(UNIT_URL + \
         "?language_code=hi&&version_abbreviation=TTT&latest_revision=false")
    assert_not_available_content(response)
    #with auth
    response = client.get(UNIT_URL + "?language_code=hi&&version_abbreviation=TTT"+
        "&latest_revision=false",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

    # filter with versionTag  #WITH AUTH
    response = client.get(UNIT_URL + "?version_tag=2&version_abbreviation=TTT",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

    # filter with resource name
    response = client.get(UNIT_URL + \
         "?resource_name=hi_TTT_1_commentary",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    for item in response.json():
        assert_positive_get(item)

    # filter with version
    response = client.get(UNIT_URL + \
         "?version_abbreviation=TTT&latest_revision=false",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 9
    for item in response.json():
        assert_positive_get(item)

    # filter with license
    response = client.get(UNIT_URL + \
         "?license=CC-BY-SA&version_abbreviation=TTT",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 6
    for item in response.json():
        assert_positive_get(item)

    response = client.get(UNIT_URL + \
         "?license=ISC&version_abbreviation=TTT",headers=headers_auth)
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

    # filter with revsion and versionTag
    response = client.get(UNIT_URL + '?version_abbreviation=TTT&version_tag=1',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

def test_get_resource_filter_access_tag():
    """filter resource with access tags"""
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "vocabulary",
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
    assert len(response1.json()) >= 3
    for item in response1.json():
        assert_positive_get(item)

    response2 = client.get(UNIT_URL + \
         '?version_abbreviation=TTT&access_tag=open-access',headers=headers_auth)
    assert response2.status_code == 200
    assert len(response2.json()) == 1
    for item in response2.json():
        assert_positive_get(item)

    response3 = client.get(UNIT_URL + \
         '?version_abbreviation=TTT&access_tag=publishable',headers=headers_auth)
    assert response3.status_code == 200
    assert len(response3.json()) == 1
    for item in response3.json():
        assert_positive_get(item)

    response4 = client.get(UNIT_URL + \
         '?version_abbreviation=TTT&access_tag=content',headers=headers_auth)
    assert response4.status_code == 200
    assert len(response4.json()) == 3
    for item in response4.json():
        assert_positive_get(item)

    response5 = client.get(UNIT_URL + \
       '?version_abbreviation=TTT&access_tag=publishable&access_tag=open-access', \
        headers=headers_auth)
    assert response5.status_code == 200
    assert len(response5.json()) == 0

    #Add resource with access tags publishable , open-access
    data['language'] = 'ho'
    data['accessPermissions'] = ['publishable','open-access']
    check_post(data)

    response6 = client.get(UNIT_URL + \
        '?version_abbreviation=TTT&access_tag=publishable&access_tag=open-access', \
            headers=headers_auth)
    assert response6.status_code == 200
    assert len(response6.json()) == 1

def test_diffrernt_resources_with_app_and_roles(): #pylint: disable=too-many-statements
    """Test getting resources with users having different permissions and
    also from multiple apps"""
    headers_auth = {"contentType": "application/json","accept": "application/json"} #pylint: disable=redefined-outer-name
    #app names
    # API = schema_auth.App.API.value
    AG = schema_auth.App.AG.value #pylint: disable=invalid-name
    VACHAN = schema_auth.App.VACHAN.value #pylint: disable=invalid-name
    VACHANADMIN = schema_auth.AdminRoles.VACHANADMIN.value #pylint: disable=invalid-name
    VACHANCONTENTDASHBOARD = schema_auth.App.VACHANCONTENTDASHBOARD.value #pylint: disable=invalid-name

    #create resources for test with different access permissions
    #content is default
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT",
        "versionTag": 1,
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
        # check based on resource
        for item in response.json():
            if item["resourceName"] == "hi_TTT_1_commentary":
                assert "content" in item['metaData']['accessPermissions']
            elif item["resourceName"] == "ml_TTT_1_commentary":
                assert "open-access" in item['metaData']['accessPermissions']
            elif item["resourceName"] == "tn_TTT_1_commentary":
                assert "publishable" in item['metaData']['accessPermissions']
            elif item["resourceName"] == "af_TTT_1_commentary":
                assert "downloadable" in item['metaData']['accessPermissions']
            elif item["resourceName"] == "ak_TTT_1_commentary":
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
    #APP : Vachan Content Dashboard
    headers_auth['app'] = VACHANCONTENTDASHBOARD
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
    #APP : Vachan Content Dashboard
    headers_auth['app'] = VACHANCONTENTDASHBOARD
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
    #APP : Vachan Content Dashboard
    headers_auth['app'] = VACHANCONTENTDASHBOARD
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
     #APP : Vachan Content Dashboard
    headers_auth['app'] = VACHANCONTENTDASHBOARD
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)

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
    #APP : Vachan Content Dashboard
    headers_auth['app'] = VACHANCONTENTDASHBOARD
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
     #APP : Vachan Content Dashboard
    headers_auth['app'] = VACHANCONTENTDASHBOARD
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)

    #Get with VachanContentAdmin
    #default : API
    headers_auth = {"contentType": "application/json","accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanContentAdmin']['token']
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 5
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)
    #APP : Autographa
    headers_auth['app'] = AG
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)
    # assert 'open-access' in response.json()[0]['metaData']['accessPermissions']
    # assert 'publishable' in response.json()[1]['metaData']['accessPermissions']
    # check_list = ['open-access','publishable']
    # check_resp_permission(response, check_list)
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
     #APP : Vachan Content Dashboard
    headers_auth['app'] = VACHANCONTENTDASHBOARD
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 5
    check_list = ['open-access','publishable']
    check_resp_permission(response, check_list)

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
    #APP : Vachan Content Dashboard
    headers_auth['app'] = VACHANCONTENTDASHBOARD
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert_not_available_content(response)

    #Super Admin
    sa_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_user_data)
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
    #APP : Vachan Content Dashboard
    headers_auth['app'] = VACHANCONTENTDASHBOARD
    response = client.get(UNIT_URL+ '?version_abbreviation=TTT', headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 5
    check_list = ['open-access','publishable','downloadable','derivable','content']
    check_resp_permission(response, check_list)

def test_version_tag():
    '''version tag support a flexible pattern. Ensure its different forms are supported'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test"
    }

    # No versionTag
    add_version(data)

    # One digit versionTag
    data['versionTag'] = "2"
    add_version(data)

    # Dot separated numbers and varying number of parts
    data['versionTag'] = "2.0.1"
    add_version(data)

    # with string parts
    data['versionTag'] = "2.0.1.aplha.1"
    add_version(data)

    resource_data = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "XYZ",
        "versionTag": 1,
        "year": 2020,
        "license": "CC-BY-SA",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    check_post(resource_data)

    resource_data['versionTag'] = "2"
    check_post(resource_data)

    resource_data['versionTag'] = "2.0.1"
    check_post(resource_data)

    resource_data['versionTag'] = "2.0.1.aplha.1"
    check_post(resource_data)

    headers_auth = {"contentType": "application/json", "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.get(UNIT_URL+"?version_abbreviation=XYZ&latest_revision=false",headers=headers_auth)
    assert len(response.json()) == 4

    response = client.get(UNIT_URL+"?version_abbreviation=XYZ",headers=headers_auth)
    assert len(response.json()) == 1
    assert response.json()[0]['version']['versionTag'] == "2.0.1.aplha.1"

def test_version_tag_sorting_numeric():
    '''version tag support a flexible pattern. Ensure its sorted properly'''
    data = {
        "versionAbbreviation": "TTT",
        "versionName": "TTT version to test"
    }

    version_tags = ["10", "9", "9.1", "9.3.5.alpha.1", "9.3.5.alpha.2"]
    for tag in version_tags:
        data['versionTag'] = tag
        add_version(data)

    resource_data = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT",
        "year": 2020,
        "license": "CC-BY-SA",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    for tag in version_tags:
        resource_data['versionTag'] = tag
        check_post(resource_data)

    headers_auth = {"contentType": "application/json", "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.get(UNIT_URL+"?version_abbreviation=TTT&latest_revision=false",headers=headers_auth)
    assert len(response.json()) == 5
    assert response.json()[0]['version']['versionTag'] == "10"
    assert response.json()[1]['version']['versionTag'] == "9.3.5.alpha.2"
    assert response.json()[2]['version']['versionTag'] == "9.3.5.alpha.1"
    assert response.json()[3]['version']['versionTag'] == "9.1"
    assert response.json()[4]['version']['versionTag'] == "9"

def test_version_tag_sorting_dates():
    '''version tag support a flexible pattern. Ensure its sorted properly'''
    data = {
        "versionAbbreviation": "TTT",
        "versionName": "TTT version to test"
    }

    version_tags = ["1161", "2000.1", "2000.2.28", "1999.3.3", "2022.12.12"]
    for tag in version_tags:
        data['versionTag'] = tag
        add_version(data)

    resource_data = {
        "resourceType": "commentary",
        "language": "hi",
        "version": "TTT",
        "year": 2020,
        "license": "CC-BY-SA",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    for tag in version_tags:
        resource_data['versionTag'] = tag
        check_post(resource_data)

    headers_auth = {"contentType": "application/json", "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.get(UNIT_URL+"?version_abbreviation=TTT&latest_revision=false",headers=headers_auth)
    assert len(response.json()) == 5
    assert response.json()[0]['version']['versionTag'] == "2022.12.12"
    assert response.json()[1]['version']['versionTag'] == "2000.2.28"
    assert response.json()[2]['version']['versionTag'] == "2000.1"
    assert response.json()[3]['version']['versionTag'] == "1999.3.3"
    assert response.json()[4]['version']['versionTag'] == "1161"


def test_delete_default():
    ''' positive test case, checking for correct return of deleted resource ID'''
    from .test_commentaries import assert_positive_get as check_commentary  #pylint: disable=import-outside-toplevel

    #create new data
    response = test_post_default()
    headers_va = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['VachanAdmin']['token']
            }
    resource_name = response.json()['data']['resourceName']

     #Check Commentary table is created
    commentary_data = [
    	{'bookCode':'gen', 'chapter':1, 'verseStart':3, 'verseEnd': 30,
    		'commentary':'the creation'}
     ]
    # headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.post(COMMENTARY_URL+resource_name, headers=headers_va, json=commentary_data)
    response = client.get(COMMENTARY_URL+resource_name,headers=headers_va)
    assert response.status_code == 200
    assert len(response.json()) == 1
    for item in response.json():
        check_commentary(item)

    response = client.get(UNIT_URL + "?resource_name="+resource_name, headers=headers_va)
    resource_id = response.json()[0]["resourceId"]
    data = {"itemId":resource_id}
    # Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.delete(UNIT_URL + "?resource_id=" + str(resource_id), headers=headers)
    
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
     #Delete resource with other API user,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev']:
        headers_au = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL + "?resource_id=" + str(resource_id), headers=headers_au)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete resource with createdUser(VachanAdmin)
    response = client.delete(UNIT_URL + "?resource_id=" + str(resource_id),headers=headers_va)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Resource with identity {resource_id} deleted successfully"

    #Check resource is deleted from resources table
    check_resource_name = client.get(UNIT_URL + "?resource_name="+resource_name, \
        headers=headers_auth)
    assert_not_available_content(check_resource_name)
    #Check commentary exists
    response = client.get(COMMENTARY_URL+resource_name,headers=headers_va)
    assert response.status_code == 404

def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted resource ID'''
    #Created User or Super Admin can only delete resource
    #creating data
    response = test_post_default()
    resource_name = response.json()['data']['resourceName']

    #Login as Super Admin
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    response = client.get(UNIT_URL + "?resource_name="+resource_name, headers=headers_sa)
    resource_id = response.json()[0]["resourceId"]
    data = {"itemId":resource_id}

    #Delete resource
    response =response = client.delete(UNIT_URL + "?resource_id=" + str(resource_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] == \
    f"Resource with identity {resource_id} deleted successfully"
    logout_user(test_user_token)
    return response,resource_name

def test_delete_resource_id_string():
    '''positive test case, resource id as string'''
    response= test_post_default()
    resource_name = response.json()['data']['resourceName']
    #Login as Super Admin
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    response = client.get(UNIT_URL + "?resource_name="+resource_name, headers=headers_sa)
    resource_id = response.json()[0]["resourceId"]
    resource_id = str(resource_id)
    data = {"itemId":resource_id}
    response = client.delete(UNIT_URL + "?resource_id=" + str(resource_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] == \
         f"Resource with identity {resource_id} deleted successfully"
    logout_user(test_user_token)

def test_delete_incorrectdatatype():
    '''negative testcase. Passing input data not in json format'''
    response = test_post_default()
    resource_name = response.json()['data']['resourceName']

    #Login as Super Admin
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    resource_id = {}

    response = client.get(UNIT_URL + "?resource_name="+resource_name, headers=headers_sa)
    resource_id = response.json()[0]["resourceId"]
    resource_id = {}
    response = client.delete(UNIT_URL + "?resource_id=" + str(resource_id), headers=headers_sa)
    assert_input_validation_error(response)

def test_delete_missingvalue_resource_id():
    '''Negative Testcase. Passing input data without resource Id'''
    data = {}
    resource_id =" "
    headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['VachanAdmin']['token']
            }
    response = client.delete(UNIT_URL + "?resource_id=" + str(resource_id), headers=headers)
    assert_input_validation_error(response)

def test_delete_notavailable_resource():
    ''' request a non existing resource ID, Ensure there is no partial matching'''
    data = {"itemId":99999}
    resource_id=9999
    headers = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['VachanAdmin']['token']
            }
    response = client.delete(UNIT_URL + "?resource_id=" + str(resource_id),headers=headers)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"


def test_restore_default():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deelting data
    response, resource_name = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring data
    #Restore without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore resource with other API user,VachanAdmin,AgAdmin, \
    # AgUser,VachanUser,BcsDev,'VachanContentAdmin','VachanContentViewer'
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev','VachanContentAdmin','VachanContentViewer']:
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
    response = client.get(UNIT_URL + "?resource_name="+resource_name,headers=headers_sa)
    assert response.status_code == 200
    assert len(response.json()) == 1
    for item in response.json():
        assert_positive_get(item)
     #Check commentary exists
    response =client.get(COMMENTARY_URL+resource_name,headers=headers_sa)
    assert response.status_code == 200

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
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                     }
    response = client.put(RESTORE_URL, headers=headers_sa, json=data)
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
    headers_sa = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                     }

    #Passing input data not in json format
    data = deleteditem_id
    response = client.put(RESTORE_URL, headers=headers_sa, json=data)
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
