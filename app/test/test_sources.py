'''Test cases for versions related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_versions import check_post as add_version

UNIT_URL = '/v2/sources'


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
    assert "active" in item
    assert item["active"] in [True, False]
    parts = [item['language']['code'], item['version']['versionAbbreviation'],
        str(item['version']['revision']), item['contentType']['contentType']]
    table_name = "_".join(parts)
    assert item["sourceName"] == table_name



def check_post(data: dict):
    '''common steps for positive post test cases'''
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Source created successfully"
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
        "language": "hin",
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
        "language": "hin",
        "version": "TTD",
        "revision": 1,
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data1)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert response.json()['details'] == "Version, TTD 1, not found in Database"

    data2 = {
        "contentType": "commentary",
        "language": "hin",
        "version": "TTT",
        "revision": 2,
        "year": 2020,
        "license": "CC-BY-SA",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = client.post(UNIT_URL, headers=headers, json=data2)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert response.json()['details'] == "Version, TTT 2, not found in Database"

    data3 = {
        "contentType": "commentary",
        "language": "hin",
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
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
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
        "language": "hin",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert response.json()['details'] == "ContentType, bibl, not found in Database"

    # '''Negative test with not a valid license from license table'''
    data = {
        "contentType": "infographic",
        "language": "hin",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "XYZ-123",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    assert "License" in response.json()['details']

def test_post_wrong_year():
    '''Negative test with text in year field'''
    data = {
        "contentType": "commentary",
        "language": "hin",
        "version": "TTT",
        "revision": 1,
        "year": "twenty twenty",
        "license": "ISC",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)


def test_post_wrong_metadata():
    '''Negative test with incorrect format for metadata'''
    data = {
        "contentType": "commentary",
        "language": "hin",
        "version": "TTT",
        "revision": 1,
        "year": "twenty twenty",
        "license": "ISC",
        "metaData": '["owner"="someone", "access-key"="123xyz"]'
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_missing_mandatory_info():
    '''Negative tests with mandatory contents missing'''
    # no contentType
    data = {
        "language": "hin",
        "version": "TTT",
        "revision": 1,
        "year": 2020
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    # no language
    data = {
        "contentType": "commentary",
        "version": "TTT",
        "revision": 1,
        "year": 2020
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    # no version
    data = {
        "contentType": "commentary",
        "language": "hin",
        "revision": 1,
        "year": 2020
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    # no year
    data = {
        "contentType": "commentary",
        "language": "hin",
        "version": "TTT"
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
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
        "language": "hin",
        "version": "TTT",
        "year": 2020
    }
    check_post(data)

def test_post_duplicate():
    '''Add the same source twice'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "commentary",
        "language": "hin",
        "version": "TTT",
        "year": 2020
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    check_post(data)
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"


def test_get_empty():
    '''Test get before adding data to table. Usually done on freshly set up test DB.
    If the testing is done on a DB that already has some data, the response wont be empty.'''
    response = client.get(UNIT_URL)
    if len(response.json()) == 0:
        assert_not_available_content(response)

def test_get_wrong_values():
    '''Checks input validation for query params'''
    response = client.get(UNIT_URL + '?version_abbreviation=1')
    assert_input_validation_error(response)

    response = client.get(UNIT_URL + '?revision=X')
    assert_input_validation_error(response)

    response = client.get(UNIT_URL + '?language_code=hindi')
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
    for lang in ['hin', 'mar', 'tel']:
        data['language'] = lang
        check_post(data)

    version_data['revision'] = 2
    add_version(version_data)
    data['revision'] = 2
    for lang in ['hin', 'mar', 'tel']:
        data['language'] = lang
        check_post(data)

    data['contentType'] = 'commentary'
    data['revision'] = 1
    data['metaData'] = {'owner': 'myself'}
    data['license'] = "ISC"
    for lang in ['hin', 'mar', 'tel']:
        data['language'] = lang
        check_post(data)

    check_default_get(UNIT_URL, assert_positive_get)

    # filter with contentType
    response = client.get(UNIT_URL + "?content_type=commentary&latest_revision=false")
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

    # filter with language
    response = client.get(UNIT_URL + "?language_code=hin&latest_revision=false")
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

    # filter with revision
    response = client.get(UNIT_URL + "?revision=2")
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

    # filter with version
    response = client.get(UNIT_URL + "?version_abbreviation=TTT&latest_revision=false")
    assert response.status_code == 200
    assert len(response.json()) >= 9
    for item in response.json():
        assert_positive_get(item)

    # filter with license
    response = client.get(UNIT_URL + "?license=CC-BY-SA")
    assert response.status_code == 200
    assert len(response.json()) >= 6
    for item in response.json():
        assert_positive_get(item)

    response = client.get(UNIT_URL + "?license=ISC")
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)


    # filter with metadata
    response = client.get(UNIT_URL + '?metadata={"owner": "myself"}&latest_revision=false')
    assert response.status_code == 200
    assert len(response.json()) == 3
    for item in response.json():
        assert_positive_get(item)

    # filter with revsion and revision
    response = client.get(UNIT_URL + '?version_abbreviation=TTT&revision=1')
    assert response.status_code == 200
    assert len(response.json()) >= 3
    for item in response.json():
        assert_positive_get(item)

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
        'language': 'mal',
        "version": "TTT",
        "year": 2020
    }
    check_post(data)

    data_update = {
        "sourceName": 'mal_TTT_1_commentary',
        "revision": 2
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(UNIT_URL, headers=headers, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Source edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()['data']['version']['revision'] == 2
    assert response.json()['data']['sourceName'] == "mal_TTT_2_commentary"

    data_update = {
        'sourceName': 'mal_TTT_2_commentary',
        'metaData': {'owner': 'new owner'}
    }
    response = client.put(UNIT_URL, headers=headers, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Source edited successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()['data']['metaData'] == {'owner': 'new owner'}

def test_soft_delete():
    '''Soft delete is achived by updating the active flag to Fasle'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "commentary",
        'language': 'mal',
        "version": "TTT",
        "year": 2020
    }
    response = check_post(data)
    assert response.json()['data']['active']

    data_update = {
        'sourceName': 'mal_TTT_1_commentary',
        'active': False
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(UNIT_URL, headers=headers, json=data_update)
    assert response.status_code == 201
    assert response.json()['message'] == "Source edited successfully"
    assert_positive_get(response.json()['data'])
    assert not response.json()['data']['active']

    response = client.get(UNIT_URL + '?active=False')
    assert response.status_code == 200
    assert len(response.json()) > 0
    for item in response.json():
        assert_positive_get(item)
        assert not item['active']
    assert 'mal_TTT_1_commentary' in [item['sourceName'] for item in response.json()]
