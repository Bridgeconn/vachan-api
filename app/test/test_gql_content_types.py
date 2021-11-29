'''Test cases for contentType related GraphQL APIs'''
from typing import Dict
#pylint: disable=E0611
from . import  gql_request,assert_not_available_content_gql,check_skip_limit_gql
#pylint: disable=E0401
from .test_content_types import assert_positive_get
from .conftest import initial_test_users

headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
headers =  {"contentType": "application/json",
                "accept": "application/json"}

def test_get_default():
    '''positive test case, without optional params'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    query = """
            {
    contentTypes{
        contentId
        contentType
    }
    }
    """
    executed = gql_request(query)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["contentTypes"])>0
    assert isinstance(executed["data"]["contentTypes"], list)
    for item in executed["data"]["contentTypes"]:
        if "contentId" in item.keys():
            item["contentId"] = int(item["contentId"])
        assert_positive_get(item)

    #with auth
    executed = gql_request(query,headers=headers_auth)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["contentTypes"])>0
    assert isinstance(executed["data"]["contentTypes"], list)

    query_check = """
          query contentTypes($skip:Int, $limit:Int){
  contentTypes(skip:$skip,limit:$limit){
    contentId
  }
}
    """
    check_skip_limit_gql(query_check,"contentTypes")    

def test_get_notavailable_content_type():
    ''' request a not available content, Ensure there is not partial matching'''
    query = """
        {
    contentTypes(contentType:"bib"){
        contentId
        contentType
    }
    }
    """
    executed = gql_request(query)
    assert isinstance(executed, Dict)
    assert_not_available_content_gql(executed["data"]["contentTypes"])

def test_post_default():
    '''positive test case, checking for correct return object'''

    variables = {
    "object": {
        "contentType": "altbible"
    }
    }
    query="""
        mutation content($object: InputContentType!){
        addContentType(contentType:$object){
            message
            data{
            contentId
            contentType
            }
        }
        }
    """
    operation="mutation"
    #without auth
    executed = gql_request(query=query, operation=operation, variables=variables)

    executed = gql_request(query=query, operation=operation, variables=variables)
    assert executed["data"]["addContentType"]["message"] == "Content type created successfully"
    assert isinstance(executed, Dict)
    data = executed["data"]["addContentType"]["data"]
    if 'contentId' in data.keys():
        data["contentId"] = int(data["contentId"])
    assert_positive_get(data)

def test_post_incorrectdatatype1():
    '''the input data object should a json with "contentType" key within it'''
    variables = {
    "object": {
        "content": "altbible"
    }
    }
    query="""
        mutation content($object: InputContentType!){
        addContentType(contentType:$object){
            message
            data{
            contentId
            contentType
            }
        }
        }
    """
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables)
    assert "errors" in executed.keys()

def test_post_incorrectdatatype2():
    '''contentType should not be integer, as per the Database datatype constarints'''
    variables = {
    "object": {
        "content": 78
    }
    }
    query="""
        mutation content($object: InputContentType!){
        addContentType(contentType:$object){
            message
            data{
            contentId
            contentType
            }
        }
        }
    """
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables)
    assert "errors" in executed.keys()

def test_post_missingvalue_contenttype():
    '''contentType is mandatory in input data object and input json should not be empty'''
    variables = {
    "object": {
    }
    }
    query="""
        mutation content($object: InputContentType!){
        addContentType(contentType:$object){
            message
            data{
            contentId
            contentType
            }
        }
        }
    """
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables)
    assert "errors" in executed.keys()

def test_post_incorrectvalue_contenttype():
    ''' The contentType name should not contain spaces,
    as this name would be used for creating tables'''
    variables = {
    "object": {
        "contentType": "Bible Contents"
    }
    }
    query="""
        mutation content($object: InputContentType!){
        addContentType(contentType:$object){
            message
            data{
            contentId
            contentType
            }
        }
        }
    """
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables)
    assert "errors" in executed.keys()
