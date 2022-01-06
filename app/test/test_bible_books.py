'''Test cases for bible-books related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .conftest import initial_test_users
UNIT_URL = '/v2/lookup/bible/books'

headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "bookId" in item
    assert isinstance(item['bookId'], int)
    assert "bookCode" in item
    assert "bookName" in item

def test_get_default():
    '''positive test case, without optional params'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    check_default_get(UNIT_URL, headers_auth, assert_positive_get)

def test_get_book_code():
    '''positive test case, with one optional params, code'''
    #Without Auth
    response = client.get(UNIT_URL+'?book_code=psa')
    assert response.status_code == 200
    # assert response.json()["error"] == "Authentication Error"
    #With Auth
    response = client.get(UNIT_URL+'?book_code=psa',headers=headers_auth)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['bookCode'] == 'psa'

def test_get_book_code_upper_case():
    '''positive test case, with one optional params, code in upper case'''
    #Without Auth
    response = client.get(UNIT_URL+'?book_code=PSA')
    assert response.status_code == 200
    # assert response.json()["error"] == "Authentication Error"
    #With Auth
    response = client.get(UNIT_URL+'?book_code=PSA',headers=headers_auth)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['bookCode'] == 'psa'

def test_get_book_name():
    '''positive test case, with one optional params, name'''
    #Without Auth
    response = client.get(UNIT_URL+'?book_name=genesis')
    assert response.status_code == 200
    # assert response.json()["error"] == "Authentication Error"
    #With Auth
    response = client.get(UNIT_URL+'?book_name=genesis',headers=headers_auth)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['bookName'] == 'genesis'

def test_get_book_name_mixed_case():
    '''positive test case, with one optional params, name, with first letter capital'''
    response = client.get(UNIT_URL+'?book_name=Matthew',headers=headers_auth)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['bookName'] == 'matthew'

def test_get_multiple_params():
    '''positive test case, with two optional params'''
    response = client.get(UNIT_URL+'?book_name=1%20Samuel&book_code=1sa',headers=headers_auth)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['bookName'] == '1 samuel'
    assert response.json()[0]['bookCode'] == '1sa'

def test_get_notavailable_code():
    ''' request a not available book, with code'''
    response = client.get(UNIT_URL+"?book_code=abc",headers=headers_auth)
    assert_not_available_content(response)

def test_get_notavailable_name():
    ''' request a not available book, with book name'''
    response = client.get(UNIT_URL+"?book_name=OT",headers=headers_auth)
    assert_not_available_content(response)

def test_get_incorrectvalue_book_code():
    '''book code should be as per defined pattern'''
    response = client.get(UNIT_URL+"?book_code=110",headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+"?book_code='abcd'",headers=headers_auth)
    assert_input_validation_error(response)
