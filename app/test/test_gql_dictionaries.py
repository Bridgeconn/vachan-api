"""Test cases for commentaries in GQL"""
from typing import Dict
#pylint: disable=E0401
from .test_gql_versions import GLOBAL_QUERY as version_query
from .test_gql_sources import SOURCE_GLOBAL_QUERY as source_query
from .test_gql_versions import check_post as version_add
from .test_gql_sources import check_post as source_add
from .test_dictionaries import assert_positive_get
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import gql_request,assert_not_available_content_gql,check_skip_gql,check_limit_gql

VERSION_VAR  = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version for bibles"
    }
    }
SOURCE_VAR = {
  "object": {
    "contentType": "dictionary",
    "language": "gu",
    "version": "TTT",
    "revision": "1",
    "year": 2020,
  }
}

ADD_DICTIONARY = """
mutation adddictionary($object:InputAddDictionary){
  addDictionary(dictArg:$object){
   message
    data{
      word
      details
      active
    }
  }
}
"""
EDIT_DICTIONARY = """
    mutation editdictionary($object:InputEditDictionary){
  editDictionary(dictArg:$object){
   message
    data{
      word
      details
      active
    }
  }
}
"""
def check_post(query, variables):
    '''prior steps and post attempt, without checking the response'''
    #add version
    version_add(version_query,VERSION_VAR)
    #add source
    src_executed = source_add(source_query,SOURCE_VAR)
    source_name = src_executed["data"]["addSource"]["data"]["sourceName"]
    executed = gql_request(query=query,operation="mutation", variables=variables)
    return executed,source_name

def post_dictionary(variable):
    '''post data and check successfull or not'''
    executed , source_name = check_post(ADD_DICTIONARY,variable)
    assert executed["data"]["addDictionary"]["message"] == "Dictionary words added successfully"
    assert len(variable["object"]["wordList"]) ==\
       len(executed["data"]["addDictionary"]["data"])
    for item in executed["data"]["addDictionary"]["data"]:
        assert_positive_get(item)
    return executed,source_name

def test_post_default():
    '''Positive test to upload dictionary words'''
    variable = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": [
        {"word": "one", "details":"{\"digit\":1,\"type\":\"odd\"}"},
    	{"word": "two", "details":"{\"digit\":2,\"type\":\"even\"}"},
    	{"word": "three", "details":"{\"digit\":3,\"type\":\"even\"}"},
    	{"word": "four", "details":"{\"digit\":4,\"type\":\"even\"}"},
    	{"word": "five", "details":"{\"digit\":5,\"type\":\"even\"}"}
    ]
  }
}    
    post_dictionary(variable)

    #test_post_duplicate

    executed = gql_request(ADD_DICTIONARY,operation="mutation",variables=variable)
    assert "errors" in executed.keys()

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''
    #add version
    version_add(version_query,VERSION_VAR)
    #add source
    src_executed = source_add(source_query,SOURCE_VAR)
    # single data object instead of list
    variable ={
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": 
        {"word": "one", "details":"{\"digit\":1,\"type\":\"odd\"}"},
    
  }
}

    executed = gql_request(ADD_DICTIONARY,operation="mutation",variables=variable)
    assert "errors" in executed.keys()

    # data object with missing mandatory fields
    variable2 ={
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": [
        {"details":"{\"digit\":1,\"type\":\"odd\"}"},
    ]
  }
}
    executed2 = gql_request(ADD_DICTIONARY,operation="mutation",variables=variable2)
    assert "errors" in executed2.keys()

    # incorrect data value for details
    variable3 = variable ={
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList":[ 
        {"word": "one", "details":"\"digit\":1,\"type\":\"odd\""},
    ]
  }
}
    executed3 = gql_request(ADD_DICTIONARY,operation="mutation",variables=variable3)
    assert "errors" in executed3.keys()

    # wrong source name
    variable4 ={
  "object": {
    "sourceName": "kj_TTT_1_dictionary",
    "wordList": [
        {"word": "one", "details":"{\"digit\":1,\"type\":\"odd\"}"},
    ]
  }
}
    executed4 = gql_request(ADD_DICTIONARY,operation="mutation",variables=variable4)
    assert "errors" in executed4.keys()

def test_get_after_data_upload():
    '''Add some data into the table and do all get tests'''
    variable = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": [
      {"word": "one", "details":"{\"digit\":1,\"type\":\"odd\"}"},
    	{"word": "two", "details":"{\"digit\":2,\"type\":\"even\"}"},
    	{"word": "three", "details":"{\"digit\":3,\"type\":\"even\"}"},
    	{"word": "four", "details":"{\"digit\":4,\"type\":\"even\"}"},
    	{"word": "five", "details":"{\"digit\":5,\"type\":\"even\"}"}
    ]
  }
}    
    post_dictionary(variable)

    #skip and limit
    query = """
    {
  dictionaryWords(sourceName:"gu_TTT_1_dictionary",arg_text){
    word
  }
}
    """

    check_skip_gql(query,"dictionaryWords")
    check_limit_gql(query,api_name="dictionaryWords")

    # search with first letter
    query1 = """
      {
  dictionaryWords(sourceName:"gu_TTT_1_dictionary",searchWord:"f"){
    word
  }
}
    """
    executed1 = gql_request(query1)
    assert isinstance(executed1,Dict)
    assert isinstance(executed1["data"]["dictionaryWords"],Dict)
    assert len(executed1["data"]["dictionaryWords"]) == 2

    # search with starting two letters
    query2 = """
      {
  dictionaryWords(sourceName:"gu_TTT_1_dictionary",searchWord:"fi"){
    word
  }
}
    """
    executed2 = gql_request(query2)
    assert len(executed2["data"]["dictionaryWords"]) == 1

    # search for not available
    query3 = """
      {
  dictionaryWords(sourceName:"gu_TTT_1_dictionary",searchWord:"ten"){
    word
  }
}
    """
    executed3 = gql_request(query3)
    assert_not_available_content_gql(executed3["data"]["dictionaryWords"])

    # full word match
    query4 = """
      {
  dictionaryWords(sourceName:"gu_TTT_1_dictionary",searchWord:"two",exactMatch:true){
    word
  }
}
    """
    executed4 = gql_request(query4)
    assert len(executed4["data"]["dictionaryWords"]) == 1
    assert executed4["data"]["dictionaryWords"][0]["word"] == "two"

def test_get_incorrect_data():
    '''Check for input validations in get'''
    #wrong source
    query1 = """
      {
  dictionaryWords(sourceName:"gu_TTT_1_"){
    word
  }
}
    """
    executed1 = gql_request(query=query1)
    assert "errors" in executed1.keys()

    #search word should be string 
    query2 = """
      {
  dictionaryWords(sourceName:"gu_TTT_1_dictionary",searchWord:10){
    word
  }
}
    """
    executed2 = gql_request(query2)
    assert "errors" in executed2.keys()

    #exeact match should be true or false
    query3 = """
      {
  dictionaryWords(sourceName:"gu_TTT_1_dictionary",exactMatch:non){
    word
  }
}
    """
    executed3 = gql_request(query3)
    assert "errors" in executed3.keys()

def test_put_after_upload():
    '''Tests for put'''
    variable = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": [
    	{"word": "Adam", "details":"{\"description\":\"Frist man\"}"},
    	{"word": "Eve", "details":"{\"description\":\"Wife of Adam\"}"}
    ]
  }
}    
    post_dictionary(variable)

    update_var = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": [
    	{"word": "Adam", "details":"{\"description\":\"Frist man God created\"}"},
    	{"word": "Eve", "details":"{\"description\":\"Wife of Adam, and Mother of mankind\"}"}
    ]
  }
}    

    executed = gql_request(EDIT_DICTIONARY,operation="mutation",variables=update_var)
    assert executed["data"]["editDictionary"]["message"] == "Dictionary words updated successfully"
    for i,item in enumerate(executed["data"]["editDictionary"]["data"]):
        assert_positive_get(item)
    assert executed["data"]["editDictionary"]['data'][0]['details']["description"] ==\
           update_var["object"]["wordList"][0]['details'][16:37]

    # not available PUT
    variable2 = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": [
    	{"word": "Moses", "details":"{\"description\":\"Leader of Isreal\"}"}
    ]
  }
}           
    executed2 = gql_request(EDIT_DICTIONARY,operation="mutation",variables=variable2)
    assert "errors" in executed2.keys()

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''
    variable = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": [
      {"word": "one", "details":"{\"digit\":1,\"type\":\"odd\"}"},
    	{"word": "two", "details":"{\"digit\":2,\"type\":\"even\"}"},
    	{"word": "three", "details":"{\"digit\":3,\"type\":\"even\"}"},
    	{"word": "four", "details":"{\"digit\":4,\"type\":\"even\"}"},
    	{"word": "five", "details":"{\"digit\":5,\"type\":\"even\"}"}
    ]
  }
}    
    post_dictionary(variable)

    # single data object instead of list
    variable = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": 
      {"word": "one", "details":"{\"digit\":1,\"type\":\"odd\"}"}
    
  }
}    
    executed = gql_request(EDIT_DICTIONARY,operation="mutation",variables=variable)
    assert "errors" in executed.keys()

    # data object with missing mandatory fields
    variable1 = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList":[ 
      {"details":"{\"digit\":1,\"type\":\"odd\"}"}
    ]
  }
}
    executed1 = gql_request(EDIT_DICTIONARY,operation="mutation",variables=variable1)
    assert "errors" in executed1.keys()

    # incorrect data value for details
    variable2 = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList":[ 
      {"word": "one","details":"\"digit\":1,\"type\":\"odd\""}
    ]
  }
}    
    executed2 = gql_request(EDIT_DICTIONARY,operation="mutation",variables=variable2)
    assert "errors" in executed2.keys()

    #wrong source
    variable3 = {
  "object": {
    "sourceName": "gu_TTT_1_dic",
    "wordList":[ 
      {"word": "one","details":"{\"digit\":1,\"type\":\"odd\"}"}
    ]
  }
}
    executed3 = gql_request(EDIT_DICTIONARY,operation="mutation",variables=variable3)
    assert "errors" in executed3.keys()

def test_soft_delete():
    '''check soft delete in dictionaries'''
    variable = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": [
      {"word": "one", "details":"{\"digit\":1,\"type\":\"odd\"}"},
    	{"word": "two", "details":"{\"digit\":2,\"type\":\"even\"}"},
    	{"word": "three", "details":"{\"digit\":3,\"type\":\"even\"}"},
    	{"word": "four", "details":"{\"digit\":4,\"type\":\"even\"}"},
    	{"word": "five", "details":"{\"digit\":5,\"type\":\"even\"}"}
    ]
  }
}    
    post_dictionary(variable)

    query = """
      {
  dictionaryWords(sourceName:"gu_TTT_1_dictionary"){
    word
    active}
}
    """
    executed = gql_request(query)
    assert len(executed["data"]["dictionaryWords"]) == 5

    variable1 = {
  "object": {
    "sourceName": "gu_TTT_1_dictionary",
    "wordList": [
      {
        "word": "one",
        "details": "{\"description\":\"Frist man God created\"}",
        "active": False
      }
    ]
  }
}
    executed_put = gql_request(EDIT_DICTIONARY,operation="mutation",variables=variable1)
    executed1 = gql_request(query)
    assert len(executed1["data"]["dictionaryWords"]) == 4