'''Test cases for versions related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
# from . import check_default_get

UNIT_URL = '/v2/versions'


def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "versionId" in item
    assert isinstance(item['versionId'], int)
    assert "versionAbbreviation" in item
    assert "versionName" in item
    assert "revision" in item
    assert "metaData" in item

def check_post(data):
    '''common steps for positive post test cases'''
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Version created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["versionAbbreviation"] == data['versionAbbreviation']
    return response

def test_post_default():
    '''Positive test to add a new version'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "revision": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    check_post(data)


def test_post_without_revision():
    '''revision field should have a default value, even not provided'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    response = check_post(data)
    assert response.json()['data']['revision'] == 1

def test_post_without_metadata():
    '''metadata field is not mandatory'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "revision": "3"
    }
    response = check_post(data)
    assert response.json()['data']['metaData'] is None

def test_post_without_abbr():
    '''versionAbbreviation is mandatory'''
    data = {
        "versionName": "Xyz version to test",
        "revision": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_wrong_abbr():
    '''versionAbbreviation cannot have space, dot etc'''
    data = {
        "versionAbbreviation": "XY Z",
        "versionName": "Xyz version to test",
        "revision": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    data['versionAbbreviation'] = 'X.Y'
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_wrong_revision():
    '''revision cannot have space, dot letters etc'''
    data = {
        "versionAbbreviation": "XY Z",
        "versionName": "Xyz version to test",
        "revision": "1.0",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    data['revision'] = "1 2"
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    data['revision'] = '1a'
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_without_name():
    '''versionName is mandatory'''
    data = {
        "versionAbbreviation": "XYZ",
        "revision": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_get():
    '''test get on empty table'''
    response = client.get(UNIT_URL)
    assert_not_available_content(response)

def test_get_wrong_abbr():
    '''abbreviation with space, number'''
    response = client.get(UNIT_URL+'?version_abbreviation=A%20A')
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+'?version_abbreviation=123')
    assert_input_validation_error(response)

def test_get_wrong_revision():
    '''revision as text'''
    response = client.get(UNIT_URL+'?version_abbreviation=A%20A')
    assert_input_validation_error(response)

