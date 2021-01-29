'''Test cases for contentType related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
UNIT_URL = '/v2/contents'


def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "contentId" in item
    assert isinstance(item['contentId'], int)
    assert "contentType" in item

def test_get_default():
    '''positive test case, without optional params'''
    check_default_get(UNIT_URL, assert_positive_get)

def test_get_notavailable_content_type():
    ''' request a not available content, Ensure there is not partial matching'''
    response = client.get(UNIT_URL+"?content_type=bib")
    assert_not_available_content(response)

def test_post_default():
    '''positive test case, checking for correct return object'''
    data = {"contentType":"altbible"}
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    print(response.json())
    assert response.status_code == 201
    assert response.json()['message'] == "Content type created successfully"
    assert_positive_get(response.json()['data'])

def test_post_incorrectdatatype1():
    '''the input data object should a json with "contentType" key within it'''
    data = "bible"
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_incorrectdatatype2():
    '''contentType should not be integer, as per the Database datatype constarints'''
    data = {"contentType":75}
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_missingvalue_contenttype():
    '''contentType is mandatory in input data object'''
    data = {}
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_incorrectvalue_contenttype():
    ''' The contentType name should not contain spaces,
    as this name would be used for creating tables'''
    data = {"contentType":"Bible Contents"}
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)
