'''Test cases for bible-books related APIs'''
from . import gql_request,assert_not_available_content_gql,check_skip_limit_gql
from .conftest import initial_test_users
from .test_bible_books import assert_positive_get

headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']

get_all_books = """
    {
  bibleBooks{
    bookId
    bookName
    bookCode
  }
}
"""

def test_get_default():
    '''positive test case, without optional params'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    executed = gql_request(query=get_all_books,headers=headers_auth)
    items = executed["data"]["bibleBooks"]
    for item in items:
        item["bookId"] = int(item["bookId"])
        assert_positive_get(item)

    #check skip limit 
    check_query = """
        query getbooks($skip:Int,$limit:Int){
  bibleBooks(skip:$skip,limit:$limit){
    bookId
    bookName
    bookCode
  }
}
    """
    check_skip_limit_gql(check_query,"bibleBooks",headers=headers_auth)    

query_book_code = """
    query getbooks($code:String){
  bibleBooks(bookCode:$code){
    bookId
    bookName
    bookCode
  }
}
    """

def test_get_book_code():
    '''positive test case, with one optional params, code'''
    #Without Auth
    var = {
  "code": "psa"
}
    executed = gql_request(query=query_book_code,variables=var)
    assert "errors" in executed
    #With Auth
    executed = gql_request(query=query_book_code,headers=headers_auth,variables=var)
    data = executed["data"]["bibleBooks"]
    assert data[0]["bookCode"] == 'psa'

def test_get_book_code_upper_case():
    '''positive test case, with one optional params, code in upper case'''
    #Without Auth
    var = {
  "code": "PSA"
}
    executed = gql_request(query=query_book_code,variables=var)
    assert "errors" in executed
    #With Auth
    executed = gql_request(query=query_book_code,headers=headers_auth,variables=var)
    data = executed["data"]["bibleBooks"]
    assert data[0]["bookCode"] == 'psa'

query_book_name = """
    query getbooks($name:String){
  bibleBooks(bookName:$name){
    bookId
    bookName
    bookCode
  }
}
"""

def test_get_book_name():
    '''positive test case, with one optional params, name'''
    #Without Auth
    var = {
  "name": "genesis"
}
    executed = gql_request(query=query_book_name,variables=var)
    assert "errors" in executed
    #With Auth
    executed = gql_request(query=query_book_name,headers=headers_auth,variables=var)
    data = executed["data"]["bibleBooks"]
    assert data[0]["bookName"] == 'genesis'

def test_get_book_name_mixed_case():
    '''positive test case, with one optional params, name, with first letter capital'''
    #Without Auth
    var = {
  "name": "Matthew"
}
    executed = gql_request(query=query_book_name,variables=var)
    assert "errors" in executed
    #With Auth
    executed = gql_request(query=query_book_name,headers=headers_auth,variables=var)
    data = executed["data"]["bibleBooks"]
    assert data[0]["bookName"] == 'matthew'

query_book_mul_params = """
    query getbooks($name:String,$code:String){
  bibleBooks(bookName:$name,bookCode:$code){
    bookId
    bookName
    bookCode
  }
}
"""

def test_get_multiple_params():
    '''positive test case, with two optional params'''
    #Without Auth
    var = {
  "name": "1 samuel",
  "code": "1sa"
}
    executed = gql_request(query=query_book_mul_params,variables=var)
    assert "errors" in executed
    #With Auth
    executed = gql_request(query=query_book_mul_params,headers=headers_auth,variables=var)
    data = executed["data"]["bibleBooks"]
    assert data[0]["bookName"] == '1 samuel'
    assert data[0]["bookCode"] == '1sa'

def test_get_notavailable_code():
    ''' request a not available book, with code'''
    var = {
  "code": "BBB"
}
    #With Auth
    executed = gql_request(query=query_book_code,headers=headers_auth,variables=var)
    assert_not_available_content_gql(executed["data"]["bibleBooks"])

def test_get_incorrectvalue_book_code():
    '''book code should be as per defined pattern'''
    var = {
  "code": 110
}
    #With Auth
    executed = gql_request(query=query_book_code,headers=headers_auth,variables=var)
    assert_not_available_content_gql(executed["data"]["bibleBooks"])
