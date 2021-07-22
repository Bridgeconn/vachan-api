'''Test cases for contentType related GraphQL APIs'''
from typing import Dict
#pylint: disable=E0611
from . import check_skip_gql, gql_request,assert_not_available_content_gql
#pylint: disable=E0401
from .test_content_types import assert_positive_get


def test_get_default():
    '''positive test case, without optional params'''
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

    query_check = """
            {
    contentTypes(arg_text){
        contentId
        contentType
    }
    }
    """
    check_skip_gql(query_check,"contentTypes")    

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
