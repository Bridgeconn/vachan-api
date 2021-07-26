"""Test cases for agmt project management in GQL"""
from typing import Dict
#pylint: disable=E0401
from .test_agmt_projects import assert_positive_get,bible_books
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import  gql_request,assert_not_available_content_gql,check_skip_limit_gql
from .test_gql_bibles import add_bible

PROJECT_CREATE_GLOBAL_QUERY = """
    mutation createproject($object:InputCreateAGMTProject){
  createAgmtProject(agmtArg:$object){
    message
    data{
      projectId
      projectName
      sourceLanguage{
        languageId
        language
        code
        scriptDirection
        metaData
      }
      targetLanguage{
        languageId
        language
        code
        scriptDirection
        metaData
      }
      documentFormat
      users{
        projectId
        userId
        userRole
        metaData
        active
      }
      metaData
      active
    }
  }
}
"""
PROJECT_EDIT_GLOBAL_QUERY = """
    mutation editAGMTProject($object:InputEditAGMTProject){
  editAgmtProject(agmtArg:$object){
    message
    data{
      projectId
      projectName
      sourceLanguage{
        languageId
        language
        code
        scriptDirection
        metaData
      }
      targetLanguage{
        languageId
        language
        code
        scriptDirection
        metaData
      }
      documentFormat
      users{
        projectId
        userId
        userRole
        metaData
        active
      }
      metaData
      active
    }
  }
}
"""
PROJECT_GET_GLOBAL_QUERY = """
    {
  agmtProjects{
    projectId
    projectName
    sourceLanguage {
      languageId
      language
      code
      scriptDirection
      metaData
    }
    targetLanguage {
      languageId
      language
      code
      scriptDirection
      metaData
    }
    documentFormat
    users {
      projectId
      userId
      userRole
      metaData
      active
    }
    metaData
    active
  }
}
"""
USER_CREATE_GLOBAL_QUERY = """
    mutation createagmtuser($object:AGMTUserCreateInput){
  createAgmtProjectUser(agmtArg:$object){
    message
    data{
      projectId
      userId
      userRole
      metaData
      active
    }
  }
}

"""
USER_EDIT_GLOBAL_QUERY = """
        mutation editAGMTuser($object:AGMTUserEditInput){
  editAgmtProjectUser(agmtArg:$object){
    message
    data{
      projectId
      userId
      userRole
      metaData
      active
    }
  }
}
"""

def check_post(query,variables):
    """positive post test"""
    executed = gql_request(query=query,operation="mutation", variables=variables)
    assert isinstance(executed, Dict)
    assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
    item =executed["data"]["createAgmtProject"]["data"] 
    if item["projectId"]:
        item["projectId"] = int(item["projectId"])
    assert_positive_get(item)
    return executed


def test_default_post_put_get():
    '''Positive test to create a project'''
    executed = gql_request(query=PROJECT_GET_GLOBAL_QUERY)
    assert_not_available_content_gql(executed["data"]["agmtProjects"])

    # create with minimum data
    post_data = {
     "object": {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
  }
}
    executed1 = check_post(PROJECT_CREATE_GLOBAL_QUERY,post_data)
    new_project = executed1["data"]["createAgmtProject"]["data"]

    # check if all defaults are coming
    assert new_project['metaData']["useDataForLearning"]
    assert isinstance(new_project['metaData']['books'], list)
    assert len(new_project['metaData']['books']) == 0
    assert new_project['active']

    # upload books  
    put_data = {
     "object": {
        "projectId":int(new_project['projectId']),
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
  }
}  

    executed2 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data)
    assert isinstance(executed2, Dict)
    assert executed2["data"]["editAgmtProject"]["message"] == "Project updated successfully"
    updated_project =executed2["data"]["editAgmtProject"]["data"]
    if updated_project["projectId"]:
        updated_project["projectId"] = int(updated_project["projectId"])
    assert_positive_get(updated_project)

    assert new_project['projectId'] == updated_project['projectId']
    assert new_project['projectName'] == updated_project['projectName']
    assert updated_project['metaData']['books'] == ['mat', 'mrk']

    #add bible 
    executed_bible,source_name =  add_bible()

    put_data = {
     "object": {
        "projectId":new_project['projectId'],
        "selectedBooks": {
            "bible": source_name,
            "books": ["luk", "jhn" ]
          }
  }
}  
    executed3 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data)
    assert isinstance(executed3, Dict)
    assert executed3["data"]["editAgmtProject"]["message"] == "Project updated successfully"
    updated_project =executed3["data"]["editAgmtProject"]["data"]
    if updated_project["projectId"]:
        updated_project["projectId"] = int(updated_project["projectId"])
    assert_positive_get(updated_project)
    assert updated_project['metaData']['books'] == ['mat', 'mrk', 'luk', 'jhn']

    # fetch projects
