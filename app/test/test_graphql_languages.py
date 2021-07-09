'''Test cases for language related GraphQL'''
import os
import sys
from typing import Dict

#pylint: disable=E0611
#pylint: disable=E0401
from test.test_languages import assert_positive_get
from graphene.test import Client
import graphene
current_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
#pylint: disable=C0413
#pylint: disable=E0401
from graphql_api import queries, mutations

schema=graphene.Schema(query=queries.Query,mutation=mutations.VachanMutations)
client = Client(schema)

##### Query Tests ####

def test_get_all_data():
    """test for get all data as per the following query"""
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
    executed = client.execute(default_get_query)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"])>0
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)


def test_get_one_language_with_argument():
    """test for get only 1 field data with  name"""
    default_get_query = """
        {
    languages(languageName:"Afar"){
        language
    }
    }
    """
    executed = client.execute(default_get_query)
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
    executed = client.execute(query)
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
    executed = client.execute(query)
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
    executed = client.execute(query)
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
    executed = client.execute(query)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"]) == 1
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)
        assert item["language"].lower() == "malayalam"

def test_check_gql_skip():
    '''Skip Test for languages'''
    query_skip0 = """
            {
    languages(skip:0){
        languageId
        language
    }
    }
    """
    query_skip1 = """
            {
    languages(skip:1){
        languageId
        language
    }
    }
    """
    executed = client.execute(query_skip0)
    assert isinstance(executed, Dict)
    if len(executed["data"]["languages"]) > 1:
        executed2 = client.execute(query_skip1)
        assert isinstance(executed2, Dict)
        assert executed["data"]["languages"][1] == executed2["data"]["languages"][0]

def test_check_gql_limit():
    '''limit Test for languages'''
    query_limit = """
            {
    languages(limit:3){
       languageId
        language
        code
        scriptDirection
        metaData
    }
    }
    """
    executed = client.execute(query_limit)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"]) <= 3

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
    executed = client.execute("""
            mutation create($object:InputAddLang!){
    addLanguage(languageAddargs:$object){
        finalout{
        msg
        languageType{
            languageId
            language
            code
            scriptDirection
            metaData
        }
        }
    }
    }
    """,None,None,variables)
    assert executed["data"]["addLanguage"]["finalout"]["msg"] == "Language Added successfully"
    item =executed["data"]["addLanguage"]["finalout"]["languageType"]
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
    executed = client.execute("""
            mutation create($object:InputAddLang!){
        addLanguage(languageAddargs:$object){
            finalout{
                msg
                languageType{
                    languageId
                    language
                    code
                    scriptDirection
                    metaData
                }
                }
            }
    }
    """,None,None,variables)
    assert executed["data"]["addLanguage"]["finalout"]["msg"] == "Language Added successfully"
    item =executed["data"]["addLanguage"]["finalout"]["languageType"]
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
    executed = client.execute("""
            mutation create($object:InputAddLang!){
        addLanguage(languageAddargs:$object){
            finalout{
                msg
                languageType{
                    languageId
                    language
                    code
                    scriptDirection
                    metaData
                }
                }
            }
    }
    """,None,None,variables)
    assert executed["data"]["addLanguage"]["finalout"]["msg"] == "Language Added successfully"
    item =executed["data"]["addLanguage"]["finalout"]["languageType"]
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
    executed = client.execute("""
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
        """,None,None,variables)
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
    executed = client.execute("""
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
        """,None,None,variables)
    assert "errors" in executed.keys()

def test_post_missingvalue_language():
    '''language name should be present'''
    variables = {
    "object": {
       "code": "MMM",
      "scriptDirection": "left-to-right"
     }
    }
    executed = client.execute("""
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
        """,None,None,variables)
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
    executed = client.execute(query)
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
    executed = client.execute(query2)
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
    executed = client.execute(query3)
    found = False
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"]) > 0
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)
        if item['language'] == "Sinhala":
            found = True
    assert found
