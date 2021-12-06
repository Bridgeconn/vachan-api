"""Test cases for dictionaries in GQL"""
from typing import Dict
#pylint: disable=E0401
from .test_gql_versions import GLOBAL_QUERY as version_query
from .test_gql_sources import SOURCE_GLOBAL_QUERY as source_query
from .test_gql_versions import check_post as version_add
from .test_gql_sources import check_post as source_add
from .test_infographics import assert_positive_get
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import gql_request,assert_not_available_content_gql,check_skip_limit_gql
from .conftest import initial_test_users
from . test_gql_auth_basic import login,SUPER_PASSWORD,SUPER_USER

headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
headers = {"contentType": "application/json", "accept": "application/json"}

VERSION_VAR  = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version for bibles"
    }
    }
SOURCE_VAR = {
  "object": {
    "contentType": "infographic",
    "language": "ur",
    "version": "TTT",
    "revision": "1",
    "year": 2020,
  }
}

ADD_INFOGRAPHIC = """
    mutation addinfographic($object:InputAddInfographic){
  addInfographic(infoArg:$object){
    message
    data{
      book{
        bookId
        bookName
        bookCode
      }
      title
      infographicLink
      active
    }
  }
}
"""
EDIT_INFOGRAPHIC = """
    mutation editinfographic($object:InputEditInfographic){
  editInfographic(infoArg:$object){
    message
    data{
      book{
        bookId
        bookName
        bookCode
      }
      title
      infographicLink
      active
    }
  }
}
"""

GET_INFOGRAPHIC = """
    {
  infographics(sourceName:"ur_TTT_1_infographic"){
    book{
      bookId
      bookName
      bookCode
    }
    title
    infographicLink
    active
  }
}
"""
headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
def check_post(query, variables):
    '''prior steps and post attempt, without checking the response'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    #add version
    version_add(version_query,VERSION_VAR)
    #add source
    src_executed = source_add(source_query,SOURCE_VAR)
    source_name = src_executed["data"]["addSource"]["data"]["sourceName"]
    #without auth
    executed = gql_request(query=query,operation="mutation", variables=variables)
    assert "errors" in executed
    #with auth
    executed = gql_request(query=query,operation="mutation", variables=variables,
      headers=headers_auth)
    assert not "errors" in executed
    return executed,source_name

def post_infographic(variable):
    '''post data and check successfull or not'''
    executed , source_name = check_post(ADD_INFOGRAPHIC,variable)
    assert executed["data"]["addInfographic"]["message"] == "Infographics added successfully"
    assert len(variable["object"]["data"]) ==\
       len(executed["data"]["addInfographic"]["data"])
    for item in executed["data"]["addInfographic"]["data"]:
        assert_positive_get(item)   
    return executed,source_name


def test_post_default():
    '''Positive test to upload Infographic'''
    variable = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": [
        {'bookCode':'gen', 'title':"creation", "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'gen', 'title':"abraham's family",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'exo', 'title':"Isarel's travel routes",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"the Gods reveals himself in new testament",
        "infographicLink":"http://somewhere.com/something"},
    ]
  }
} 
    post_infographic(variable=variable)

    #skip and limit check
    query_check = """
       query infographic($skip:Int, $limit:Int){
  infographics(sourceName:"ur_TTT_1_infographic",skip:$skip,limit:$limit){
  	title
  }
}
    """
    check_skip_limit_gql(query_check,"infographics",headers=headers_auth)

    #duplicate test
    executed = gql_request(ADD_INFOGRAPHIC,operation="mutation",variables=variable,
    headers=headers_auth)
    assert "errors" in executed.keys()

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    variable = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": 
     {'bookCode':'mat', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"http://somewhere.com/something"}
  }
}    
    executed = gql_request(ADD_INFOGRAPHIC,operation="mutation",variables=variable,
      headers=headers_auth)
    assert "errors" in executed.keys()

    # data object with missing mandatory fields
    variable2 = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": 
     [{'bookCode':'mat',
        "infographicLink":"http://somewhere.com/something"}]
  }
}  
    executed2 = gql_request(ADD_INFOGRAPHIC,operation="mutation",variables=variable2,
      headers=headers_auth)
    assert "errors" in executed2.keys()

    variable3 = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": 
     [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ"}
    ]
  }
}  
    executed3 = gql_request(ADD_INFOGRAPHIC,operation="mutation",variables=variable3,
      headers=headers_auth)
    assert "errors" in executed3.keys()

    # incorrect data values in fields
    variable4 = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": 
     [
        {'bookCode':'mathew', 'title':"the Geneology of Jesus Christ"}
    ]
  }
}  
    executed4 = gql_request(ADD_INFOGRAPHIC,operation="mutation",variables=variable4,
      headers=headers_auth)
    assert "errors" in executed4.keys()

    variable5 = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": 
     [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"no url"}
    ]
  }
}  
    executed5 = gql_request(ADD_INFOGRAPHIC,operation="mutation",variables=variable5,
      headers=headers_auth)
    assert "errors" in executed5.keys()

    #wrong source
    variable6 = {
  "object": {
    "sourceName": "ml_TT_1_infographic",
    "data": 
     [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ"}
    ]
  }
}  
    executed6 = gql_request(ADD_INFOGRAPHIC,operation="mutation",variables=variable6,
      headers=headers_auth)
    assert "errors" in executed6.keys()

def test_get_after_data_upload():
    '''Add some infographics data into the table and do all get tests'''
    variable = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": [
        {'bookCode':'gen', 'title':"creation",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'gen', 'title':"Noah's Ark",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'gen', 'title':"abraham's family",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'exo', 'title':"Isarel's travel routes",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'act', 'title':"Paul's travel routes",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"the Gods reveals himself in new testament",
        "infographicLink":"http://somewhere.com/something"}
    ]
  }
} 

    post_infographic(variable=variable)

    #filter by book
    query = """
        {
  infographics(sourceName:"ur_TTT_1_infographic",arg_text){
    title
  }
}
    """
    query1 = query.replace("arg_text",'bookCode:"gen"')
    executed1 = gql_request(query1,headers=headers_auth)
    assert len(executed1["data"]["infographics"]) == 3

    query2 = query.replace("arg_text",'bookCode:"exo"')
    executed2 = gql_request(query2,headers=headers_auth)
    assert len(executed2["data"]["infographics"]) == 1

    # filter with title introductions
    query3 = query.replace("arg_text",'title:"creation"')
    executed3 = gql_request(query3,headers=headers_auth)
    assert len(executed3["data"]["infographics"]) == 1

    # both title and book
    query4 = query.replace("arg_text",'bookCode:"gen",title:"Noah\'s Ark"')
    executed3 = gql_request(query4,headers=headers_auth)
    assert len(executed3["data"]["infographics"]) == 1

    # not available
    query5 = query.replace("arg_text",'book_code:"mat"')
    executed5 = gql_request(query5,headers=headers_auth)
    assert "errors" in executed5.keys()

def test_get_incorrect_data():
    '''Check for input validations in get'''    
    query = """
        {
  infographics(sourceName:"ur_T_1_info"){
    title
  }
}
    """
    executed = gql_request(query,headers=headers_auth)
    assert "errors" in executed.keys()

    query0 = """
        {
  infographics(sourceName:"ur_TTT_1_infographic",arg_text){
    title
  }
}
    """
    query1 = query0.replace("arg_text","book_code:60")
    executed1 = gql_request(query1,headers=headers_auth)
    assert "errors" in executed1.keys()

    query2 = query0.replace("arg_text","book_code:mark")
    executed2 = gql_request(query2,headers=headers_auth)
    assert "errors" in executed2.keys()

    query3 = query0.replace("arg_text","title:1")
    executed3 = gql_request(query3,headers=headers_auth)
    assert "errors" in executed3.keys()

def test_put_after_upload():
    '''Positive tests for put'''
    variable = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": [
        {"bookCode":"mat", "title":"12 apostles",
        "infographicLink":"http://somewhere.com/something"},
        {"bookCode":"mat", "title":"miracles",
        "infographicLink":"http://somewhere.com/something"}
    ]
  }
} 
    post_infographic(variable=variable)


    new_variable = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": [
        {"bookCode":"mat", "title":"12 apostles",
        "infographicLink":"http://anotherplace.com/something"},
        {"bookCode":"mat", "title":"miracles",
        "infographicLink":"http://somewhereelse.com/something"}
    ]
  }
} 
    #Without Auth
    executed = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=new_variable)
    assert "errors" in executed
    #with auth
    executed = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=new_variable,
      headers=headers_auth)
    assert executed["data"]["editInfographic"]["message"] == "Infographics updated successfully"
    assert len(executed["data"]["editInfographic"]["data"]) > 0
    for i,item in enumerate(executed["data"]["editInfographic"]["data"]):
        assert_positive_get(item)
        assert executed["data"]["editInfographic"]["data"][i]['infographicLink'] \
            == new_variable["object"]["data"][i]['infographicLink']
        assert executed["data"]["editInfographic"]["data"][i]["book"]["bookCode"]\
             == new_variable["object"]["data"][i]['bookCode']
        assert executed["data"]["editInfographic"]["data"][i]['title'] == \
            new_variable["object"]["data"][i]['title']

    # not available PUT
    variable2 = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": [
        {'bookCode':'mrk', 'title':"12 apostles",
        "infographicLink":"http://anotherplace.com/something"}
    ]
  }
}
    executed2 = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=variable2,
      headers=headers_auth)
    assert "errors" in executed2.keys()

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''
    variable = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": [
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"}
    ]
  }
} 
    post_infographic(variable=variable)

    # single data object instead of list
    variable = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": 
     {'bookCode':'mat', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"http://somewhere.com/something"}
  }
}    
    executed = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=variable,
      headers=headers_auth)
    assert "errors" in executed.keys()

    # data object with missing mandatory fields
    variable2 = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": 
     [{'bookCode':'mat',
        "infographicLink":"http://somewhere.com/something"}]
  }
}  
    executed2 = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=variable2,
      headers=headers_auth)
    assert "errors" in executed2.keys()

    variable3 = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": 
     [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ"}
    ]
  }
}  
    executed3 = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=variable3,
      headers=headers_auth)
    assert "errors" in executed3.keys()

    # incorrect data values in fields
    variable4 = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": 
     [
        {'bookCode':'mathew', 'title':"the Geneology of Jesus Christ"}
    ]
  }
}  
    executed4 = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=variable4,
      headers=headers_auth)
    assert "errors" in executed4.keys()

    variable5 = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": 
     [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"no url"}
    ]
  }
}  
    executed5 = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=variable5,
      headers=headers_auth)
    assert "errors" in executed5.keys()

    #wrong source
    variable6 = {
  "object": {
    "sourceName": "ml_TT_1_infographic",
    "data": 
     [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ"}
    ]
  }
}  
    executed6 = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=variable6,
      headers=headers_auth)
    assert "errors" in executed6.keys()

def test_soft_delete():
    '''check soft delete in infographics''' 
    variable = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"Words of Jesus",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"7 churches of Asia Minor",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"Creatures in Heaven",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"All the Sevens",
        "infographicLink":"http://somewhere.com/something"}
    ]
  }
} 
    post_infographic(variable=variable)

    executed = gql_request(GET_INFOGRAPHIC,headers=headers_auth)
    assert len(executed["data"]["infographics"]) == 6

    variable2 = {
  "object": {
    "sourceName": "ur_TTT_1_infographic",
    "data": [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something","active": False}
    ]
  }
} 
    executed2 = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=variable2,
      headers=headers_auth)
    executed3 = gql_request(GET_INFOGRAPHIC,headers=headers_auth)
    assert len(executed3["data"]["infographics"]) == 5

def test_created_user_can_only_edit():
    """only created user and SA can only edit"""
    """source edit can do by created user and Super Admin"""
    SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(SA_user_data)
    token =  response["data"]["login"]["token"]

    headers_SA = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token
                }
    
    #add version
    version_add(version_query,VERSION_VAR)
    #add source
    source_data = {
  "object": {
    "contentType": "infographic",
    "language": "gu",
    "version": "TTT",
    "revision": "1",
    "year": 2021
  }
}
    executed = gql_request(query=source_query,operation="mutation", variables=source_data,
      headers=headers_SA)
    assert isinstance(executed, Dict)
    assert executed["data"]["addSource"]["message"] == "Source created successfully"

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    #post data
    #Create With SA
    
    variable = {
  "object": {
    "sourceName": "gu_TTT_1_infographic",
    "data": [
        {"bookCode":"mat", "title":"12 apostles",
        "infographicLink":"http://somewhere.com/something"},
        {"bookCode":"mat", "title":"miracles",
        "infographicLink":"http://somewhere.com/something"}
    ]
  }
} 
    executed = gql_request(query=ADD_INFOGRAPHIC,operation="mutation", variables=variable,
      headers=headers_SA)
    assert executed["data"]["addInfographic"]["message"] == "Infographics added successfully"      

    new_variable = {
  "object": {
    "sourceName": "gu_TTT_1_infographic",
    "data": [
        {"bookCode":"mat", "title":"12 apostles",
        "infographicLink":"http://anotherplace.com/something"},
        {"bookCode":"mat", "title":"miracles",
        "infographicLink":"http://somewhereelse.com/something"}
    ]
  }
} 
    #Edit with SA created
    executed = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=new_variable,
      headers=headers_SA)
    assert executed["data"]["editInfographic"]["message"] == "Infographics updated successfully"
    #Edit with VA not created user
    executed = gql_request(EDIT_INFOGRAPHIC,operation="mutation",variables=new_variable,
      headers=headers_auth)
    assert "errors" in executed