'''Test cases for language related GraphQL'''
from typing import Dict

#pylint: disable=E0611
from . import gql_request,check_skip_limit_gql
#pylint: disable=E0401
from .test_languages import assert_positive_get
from .conftest import initial_test_users

headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
headers = {"contentType": "application/json", "accept": "application/json"}

def test_get_all_data():
    """test for get all data as per the following query"""
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    default_get_query = """
        {
    languages{
        languageId
        language
        code
        scriptDirection
        metaData
    }
    }
    """
    #without auth
    executed = gql_request(default_get_query)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"])>0
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)

    #with auth
    executed = gql_request(default_get_query,headers=headers_auth)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"])>0
    assert isinstance(executed["data"]["languages"], list)

    query_check = """
           query languages($skip:Int, $limit:Int){
  languages(skip:$skip,limit:$limit){
    languageId
  }
}
    """    
    check_skip_limit_gql(query_check,"languages")

def test_get_one_language_with_argument():
    """test for get only 1 field data with  name"""
    default_get_query = """
        {
    languages(languageName:"Afar"){
        language
    }
    }
    """
    executed = gql_request(default_get_query,headers=headers_auth)
    assert executed == {"data": {"languages": [{"language": "Afar"}]}}

def test_get_by_code():
    "test for get by code argument"
    query = """
            {
    languages(languageCode:"ml"){
        languageId
        language
        code
        scriptDirection
        metaData
    }
    }
    """
    executed = gql_request(query, headers=headers_auth)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"])>0
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)
        assert item["code"] == "ml"

def test_get_language_code_upper_case():
    '''positive test case, with one optional params, code in upper case'''
    query = """
            {
    languages(languageCode:"ML"){
        languageId
        language
        code
        scriptDirection
        metaData
    }
    }
    """
    executed = gql_request(query, headers=headers_auth)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"])>0
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)
        assert item["code"] == "ml"

def test_get_language_name_mixed_case():
    '''positive test case, with one optional params, name, with first letter capital'''
    query = """
            {
    languages(languageName:"Malayalam"){
        languageId
        language
        code
        scriptDirection
        metaData
    }
    }
    """
    executed = gql_request(query, headers=headers_auth)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"]) == 1
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)
        assert item["language"].lower() == "malayalam"

def test_get_multiple_params():
    '''positive test case, with two optional params'''
    query = """
            {
    languages(languageName:"Malayalam",languageCode:"ml"){
        languageId
        language
        code
        scriptDirection
        metaData
    }
    }
    """
    executed = gql_request(query, headers=headers_auth)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"]) == 1
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)
        assert item["language"].lower() == "malayalam"


def test_get_notavailable_language_code():
    ''' request a not available language, with code'''
    query = """
    {
    languages(languageCode:"aaj"){
        languageId
        language
        code
        }
    }
    """
    executed = gql_request(query, headers=headers_auth)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"]) == 0

def test_get_notavailable_language_name():
    ''' request a not available language, with name'''
    query = """
    {
    languages(languageName:"not-a-language"){
        languageId
        language
        code
        }
    }
    """
    executed = gql_request(query, headers=headers_auth)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"]) == 0

def test_get_incorrectvalue_language_code():
    '''language code should be letters'''
    query = """
    {
    languages(languageCode:110){
        languageId
        language
        code
        }
    }
    """
    executed = gql_request(query, headers=headers_auth)
    assert isinstance(executed, Dict)
    assert "errors" in executed.keys()

##### Mutation Tests ####

def test_post_default():
    """Test case for create a langugae and check return dict"""
    variables = {
    "object": {
        "language": "new-lang",
        "code": "x-aaj",
        "scriptDirection": "left-to-right"
        }
    }
    create_query = """
        mutation create($object:InputAddLang!){
        addLanguage(languageAddargs:$object){
                message
            data{
            languageId
            language
            code
            scriptDirection
            metaData
            }
        }
        }
    """
    operation="mutation"
    #Registered user can only add content type
    #without auth
    executed = gql_request(query=create_query, operation=operation, variables=variables)
    assert "errors" in executed.keys()
    #with auth
    executed = gql_request(query=create_query, operation=operation, variables=variables,
    headers=headers_auth)
    assert executed["data"]["addLanguage"]["message"] == "Language created successfully"
    item =executed["data"]["addLanguage"]["data"]
    assert_positive_get(item)
    assert item["code"] == "x-aaj"

def test_post_upper_case_code():
    """positive test case, checking for case conversion of code"""
    variables = {
    "object": {
        "language": "new-lang",
        "code": "X-AAJ",
        "scriptDirection": "left-to-right"
        }
    }
    create_query = """
         mutation create($object:InputAddLang!){
        addLanguage(languageAddargs:$object){
                message
            data{
            languageId
            language
            code
            scriptDirection
            metaData
            }
        }
        }
    """
    operation="mutation"
    executed = gql_request(query=create_query, operation=operation, variables=variables,
    headers=headers_auth)
    assert executed["data"]["addLanguage"]["message"] == "Language created successfully"
    item =executed["data"]["addLanguage"]["data"]
    assert_positive_get(item)
    assert item["code"] == "X-AAJ"

def test_post_optional_script_direction():
    '''positive test case, checking for correct return object'''
    variables = {
    "object": {
        "language": "new-lang",
        "code": "x-aaj"
        }
    }
    query = """
         mutation create($object:InputAddLang!){
        addLanguage(languageAddargs:$object){
                message
            data{
            languageId
            language
            code
            scriptDirection
            metaData
            }
        }
        }
    """
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables,
    headers=headers_auth)
    assert executed["data"]["addLanguage"]["message"] == "Language created successfully"
    item =executed["data"]["addLanguage"]["data"]
    assert_positive_get(item)
    assert item["code"] == "x-aaj"

def test_post_incorrectdatatype1():
    '''code should have letters only'''
    variables = {
    "object": {
      "language": "new-lang",
      "code": "123",
      "scriptDirection": "left-to-right"
     }
    }
    query = """
                mutation create($object:InputAddLang!){
            addLanguage(languageAddargs:$object){
                finalout{
                    msg
                    languageType{
                        languageId
                        language
                    }
                    }
                }
        }
        """
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables,
    headers=headers_auth)
    assert "errors" in executed.keys()

def test_post_incorrectdatatype2():
    '''scriptDirection should be either left-to-right or right-to-left'''
    variables = {
    "object": {
      "language": "new-lang",
      "code": "MMM",
      "scriptDirection": "regular"
     }
    }
    query = """
                mutation create($object:InputAddLang!){
            addLanguage(languageAddargs:$object){
                finalout{
                    msg
                    languageType{
                        languageId
                        language
                    }
                    }
                }
        }
        """
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables,
    headers=headers_auth)
    assert "errors" in executed.keys()

def test_post_missingvalue_language():
    '''language name should be present'''
    variables = {
    "object": {
       "code": "MMM",
      "scriptDirection": "left-to-right"
     }
    }
    query = """
                mutation create($object:InputAddLang!){
            addLanguage(languageAddargs:$object){
                finalout{
                    msg
                    languageType{
                        languageId
                        language
                    }
                    }
                }
        }
        """
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables,
    headers=headers_auth)
    assert "errors" in executed.keys()

#### text search test #####
def test_searching():
    '''Being able to query languages with code, name, country of even other info'''
    query = """
        {
    languages(searchWord:"ml"){
        languageId
        language
        code
        scriptDirection
        metaData
    }
    }
    """
    executed = gql_request(query)
    found = False
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"]) > 0
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)
        if item['code'] == "ml":
            found = True
    assert found

    query2 = """
        {
    languages(searchWord:"India"){
        languageId
        language
        code
        scriptDirection
        metaData
    }
    }
    """
    executed = gql_request(query2)
    found = False
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"]) > 0
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)
        if item['code'] == "mr":
            found = True
    assert found

    query3 = """
        {
    languages(searchWord:"sri lanka"){
        languageId
        language
        code
        scriptDirection
        metaData
    }
    }
    """
    executed = gql_request(query3)
    found = False
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"]) > 0
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)
        if item['language'] == "Sinhala":
            found = True
    assert found

def test_put_languages():
    """put test for languages"""
    #create a new langauge
    variables = {
    "object": {
        "language": "new-lang-test",
        "code": "x-abc",
        "scriptDirection": "left-to-right"
        }
    }
    create_query = """
        mutation create($object:InputAddLang!){
        addLanguage(languageAddargs:$object){
                message
            data{
            languageId
            language
            code
            scriptDirection
            metaData
            }
        }
        }
    """
    operation="mutation"
    #with auth
    executed = gql_request(query=create_query, operation=operation, variables=variables,
    headers=headers_auth)
    assert executed["data"]["addLanguage"]["message"] == "Language created successfully"

    #get language id
    query = """
            {
    languages(languageCode:"x-abc"){
        languageId
    }
    }
    """
    executed = gql_request(query, headers=headers_auth)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"])>0
    item = executed["data"]["languages"]
    language_id = item[0]['languageId']

    #edit
    up_qry = """
    mutation edit($object:InputUpdateLang!){
        updateLanguage(languageUpdateargs:$object){
                message
            data{
            languageId
            language
            code
            scriptDirection
            metaData
            }
        }
        }
    """
    up_variables = {
    "object": {
        "languageId":language_id,
        "language": "new-lang-test-edited"
        }
    }
    executed = gql_request(query=up_qry, operation=operation, variables=up_variables,
    headers=headers_auth)
    assert executed["data"]["updateLanguage"]["message"] == "Language edited successfully"
    item =executed["data"]["updateLanguage"]["data"]
    assert_positive_get(item)
    assert item["language"] == up_variables["object"]["language"]

    #edit without auth
    executed = gql_request(query=up_qry, operation=operation, variables=up_variables)
    assert "errors" in executed.keys()

    #edit with not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    executed = gql_request(query=up_qry, operation=operation, variables=up_variables,
    headers=headers_auth)
    assert "errors" in executed.keys()



