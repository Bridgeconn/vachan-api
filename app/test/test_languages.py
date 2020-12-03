'''Test cases for language related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get

UNIT_URL = '/v2/languages'


def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "languageId" in item
    assert isinstance(item['languageId'], int)
    assert "language" in item
    assert "code" in item
    assert "scriptDirection" in item

def test_get_default():
    '''positive test case, without optional params'''
    check_default_get(UNIT_URL, assert_positive_get)

def test_get_language_code():
    '''positive test case, with one optional params, code'''
    response = client.get(UNIT_URL+'?language_code=hin')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'hin'

def test_get_language_code_upper_case():
    '''positive test case, with one optional params, code in upper case'''
    response = client.get(UNIT_URL+'?language_code=HIN')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'hin'

def test_get_language_name():
    '''positive test case, with one optional params, name'''
    response = client.get(UNIT_URL+'?language_name=hindi')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['language'] == 'hindi'

def test_get_language_name_mixed_case():
    '''positive test case, with one optional params, name, with first letter capital'''
    response = client.get(UNIT_URL+'?language_name=Hindi')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['language'] == 'hindi'

def test_get_multiple_params():
    '''positive test case, with two optional params'''
    response = client.get(UNIT_URL+'?language_name=hindi;language_code=hin')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['language'] == 'hindi'
    assert response.json()[0]['code'] == 'hin'

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
    response = client.get(UNIT_URL+"?language_code='abcd'")
    assert_input_validation_error(response)

def test_post_default():
    '''positive test case, checking for correct return object'''
    data = {
      "language": "new-lang",
      "code": "aaj",
      "scriptDirection": "left-to-right"
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "aaj"

def test_post_upper_case_code():
    '''positive test case, checking for case conversion of code'''
    data = {
      "language": "new-lang",
      "code": "AAJ",
      "scriptDirection": "left-to-right"
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    print(response.json())
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "aaj"

def test_post_optional_script_direction():
    '''positive test case, checking for correct return object'''
    data = {
      "language": "new-lang",
      "code": "aaj"
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    print(response.json())
    assert response.status_code == 201
    assert response.json()['message'] == "Language created successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "aaj"

def test_post_incorrectdatatype1():
    '''code should have letters only'''
    data = {
      "language": "new-lang",
      "code": "123",
      "scriptDirection": "left-to-right"
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_incorrectdatatype2():
    '''scriptDirection should be either left-to-right or right-to-left'''
    data = {
      "language": "new-lang",
      "code": "MMM",
      "scriptDirection": "regular"
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_post_missingvalue_language():
    '''language name should be present'''
    data = {
      "code": "MMM",
      "scriptDirection": "left-to-right"
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)
