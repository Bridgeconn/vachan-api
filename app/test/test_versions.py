'''Test cases for versions related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get

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

def test_post_multiple_with_same_abbr():
    '''Positive test to add two version, with same abbr and diff revision'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "revision": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    check_post(data)
    data["revision"] = 2
    check_post(data)

def test_post_multiple_with_same_abbr_negative():
    '''Negative test to add two version, with same abbr and revision'''
    data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "revision": "1",
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    check_post(data)
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

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

def test_get_after_adding_data():
    '''Add some data to versions table and test get method'''
    data = {
        'versionAbbreviation': "AAA",
        'versionName': 'test name A',
        'revision': 1
    }
    check_post(data)
    data['revision'] = 2
    check_post(data)
    data = {
        'versionAbbreviation': "BBB",
        'versionName': 'test name B',
        'revision': 1
    }
    check_post(data)
    data['revision'] = 2
    check_post(data)
    check_default_get(UNIT_URL, assert_positive_get)

    # filter with abbr
    response = client.get(UNIT_URL + '?version_abbreviation=AAA')
    assert response.status_code == 200
    assert len(response.json()) == 2
    for item in response.json():
        assert_positive_get(item)
        assert item['versionAbbreviation'] == 'AAA'


    # filter with abbr, for not available content
    response = client.get(UNIT_URL + '?version_abbreviation=CCC')
    assert_not_available_content(response)

    # filter with name
    response = client.get(UNIT_URL + '?version_name=test%20name%20B')
    assert response.status_code == 200
    assert len(response.json()) == 2
    for item in response.json():
        assert_positive_get(item)
        assert item['versionName'] == 'test name B'

   # filter with abbr and revision
    response = client.get(UNIT_URL + '?version_abbreviation=AAA&revision=2')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['versionAbbreviation'] == 'AAA'
    assert response.json()[0]['revision'] == 2

    data = {
        'versionAbbreviation': "CCC",
        'versionName': 'test name C',
        'metaData': {'owner': 'myself'}
    }
    check_post(data)

    # filter with metaData and default value for metadata
    response = client.get(UNIT_URL + '?metadata={"owner":"myself"}')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['versionAbbreviation'] == 'CCC'
    assert response.json()[0]['revision'] == 1
    assert response.json()[0]['metaData']['owner'] == 'myself'