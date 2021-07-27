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
    executed4 = gql_request(PROJECT_GET_GLOBAL_QUERY)
    assert len(executed4["data"]["agmtProjects"]) >= 1
    found_project = False
    for proj in executed4["data"]["agmtProjects"]:
        if proj['projectName'] == post_data["object"]['projectName']:
            found_project = True
            if proj["projectId"]:
                proj["projectId"] = int(proj["projectId"])
            fetched_project = proj
    assert found_project
    assert_positive_get(fetched_project)

    assert fetched_project['projectName'] == post_data["object"]['projectName']
    assert fetched_project['sourceLanguage']['code'] == post_data["object"]['sourceLanguageCode']
    assert fetched_project['targetLanguage']['code'] == post_data["object"]['targetLanguageCode']
    assert fetched_project['metaData']['books'] == ['mat', 'mrk', 'luk', 'jhn']

    # change name
    put_data = {
     "object": {
        "projectId":int(new_project['projectId']),
        "projectName":"New name for old project"
  }
}
    executed5 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data)
    assert isinstance(executed5, Dict)
    assert executed5["data"]["editAgmtProject"]["message"] == "Project updated successfully"
    updated_project =executed5["data"]["editAgmtProject"]["data"]
    if updated_project["projectId"]:
        updated_project["projectId"] = int(updated_project["projectId"])
    assert_positive_get(updated_project)
    assert updated_project['projectName']== "New name for old project"

    # create with all possible options
    post_data = {
     "object": {
        "projectName": "Test Project 2",
      "sourceLanguageCode": "hi",
      "targetLanguageCode": "ml",
      "useDataForLearning": True,
      "stopwords": {
        "prepositions": [ "कोई", "यह", "इस", "इसे", "उस", "कई", "इसी", "अभी", "जैसे" ],
        "postpositions": [  "के",  "का",  "में",  "की",  "है",  "और",  "से",  "हैं",  "को",  "पर"]
      },
      "punctuations": [",","\"","!",".",":",";","\n","\\","“","”","“","*","।","?",";","'",
        "’","(",")","‘","—" ],
      "active": True
  }
}
    check_post(PROJECT_CREATE_GLOBAL_QUERY,variables=post_data)

    # add a few more projects
    post_data = {
     "object": {
        "projectName": "Test Project 3",
      "sourceLanguageCode": "hi",
      "targetLanguageCode": "ml"
  }
}
    check_post(PROJECT_CREATE_GLOBAL_QUERY,variables=post_data)

    post_data = {
     "object": {
        "projectName": "Test Project 4",
      "sourceLanguageCode": "hi",
      "targetLanguageCode": "ml"
  }
}
    check_post(PROJECT_CREATE_GLOBAL_QUERY,variables=post_data)

    check_query = """
        query agmtfetch($skip:Int, $limit:Int){
  agmtProjects(skip:$skip,limit:$limit){
    projectName
  }
}
    """
    check_skip_limit_gql(check_query,"agmtProjects")

def test_post_invalid():
    '''test input validation for project create'''
    # Missing mandatory content
    data1 = {
     "object": {
        "projectName": "Test project 1",
        "targetLanguageCode": "ml"
  }
}
    executed1 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data1)
    assert "errors" in executed1.keys()

    data2 = {
     "object": {
        "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
  }
}
    executed2 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data2)
    assert "errors" in executed2.keys()

    data3 = {
     "object": {
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
  }
}
    executed3 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data3)
    assert "errors" in executed3.keys()

    # incorrect data in fields
    data4 = {
     "object": {
        "projectName": "Test project 1",
    "sourceLanguageCode": "2hindi",
    "targetLanguageCode": "ml"
  }
}
    executed4 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data4)
    assert "errors" in executed4.keys()

    data5 = {
     "object": {
        "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "documentFormat": 2
  }
}
    executed5 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data5)
    assert "errors" in executed5.keys()

    data6 = {
     "object": {
        "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "stopwords": ["a", "mromal", "list"]
  }
}
    executed6 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data6)
    assert "errors" in executed6.keys()

    data7 = {
     "object": {
        "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "punctuations": "+_*())^%$#<>?:'"
  }
}
    executed7 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data7)
    assert "errors" in executed7.keys()

def test_put_invalid():
    '''Give incorrect data for project update'''
    post_data = {
     "object": {
       "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
  }
}
    executed = check_post(PROJECT_CREATE_GLOBAL_QUERY,variables=post_data)
    new_project = executed["data"]["createAgmtProject"]["data"]

    # missing projectId
    data = {
     "object": {
        "active": False
  }
}
    executed1 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=data)
    assert "errors" in executed1.keys()

    # incorrect values in fields
    data = {
     "object": {
        "projectId": int(new_project['projectId']),
        "documentFormat": 2
  }
}
    executed1 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=data)
    assert "errors" in executed1.keys()

    data = {
     "object": {
       "projectId": int(new_project['projectId']),
        "uploadedBooks": "mat"
  }
}
    executed1 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=data)
    assert "errors" in executed1.keys()

    data = {
     "object": {
        "projectId": int(new_project['projectId']),
    "uploadedBooks": ["The contents of matthew in text"]
  }
}
    executed1 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=data)
    assert "errors" in executed1.keys()

def check_project_user(variable, user_id, role=None, status=None, metadata = None):
    '''Make sure the user is in project and if specified, check for other values'''
    project_get_with_name = """
        query agmtfetch($projectname:String,$skip:Int, $limit:Int){
  agmtProjects(projectName:$projectname,skip:$skip,limit:$limit){
    projectName
    projectId
    users{
      projectId
      userId
      userRole
      metaData
      active
    }
    active
}
}
    """
    executed = gql_request(project_get_with_name,operation="query",variables=variable)
    found_user = False
    found_owner = False
    resp = executed["data"]["agmtProjects"][0]
    for user in resp['users']:
        if int(user['userId']) == int(user_id):
            found_user = True
            if role:
                assert user['userRole'] == role
            if status is not None:
                assert user['active'] == status
            if metadata:
                assert user['metaData'] == metadata
        if user['userRole'] == "owner" :
            found_owner = True
    assert found_owner
    assert found_user

def test_add_user():
    '''Positive test to add a user to a project'''
    project_data = {
     "object": {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
  }
}
    executed = check_post(PROJECT_CREATE_GLOBAL_QUERY,project_data)
    new_project = executed["data"]["createAgmtProject"]["data"]

    
    user_data = {
  "object": {
    "projectId": new_project["projectId"],
    "userId": 5555
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data)
    data = executed1["data"]["createAgmtProjectUser"]["data"]
    assert executed1["data"]["createAgmtProjectUser"]["message"] == "User added in project successfully"
    assert int(data["projectId"]) == int(new_project['projectId']) 
    assert int(data["userId"]) == int(user_data["object"]["userId"]) 
    assert data["userRole"] == "member"
    assert data['active']

    # fetch this project and check for new user
    new_user_id = int(user_data["object"]["userId"])
    variable = {
    "projectname": project_data["object"]['projectName'],   
    "skip": 0,
  "limit": 10
}

    check_project_user (variable,role='member',user_id=new_user_id)

def test_add_user_invalid():
    '''Negative tests to add a user to a project'''
    project_data = {
     "object": {
    "projectName": "Test project 10",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
  }
}
    executed = check_post(PROJECT_CREATE_GLOBAL_QUERY,project_data)
    new_project = executed["data"]["createAgmtProject"]["data"]

    # No projectId
    user_data = {
  "object": {
    "userId": 11111
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data)
    assert "errors" in executed1.keys()

    # No User
    user_data = {
  "object": {
    "projectId": int(new_project["projectId"])
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data)
    assert "errors" in executed1.keys()

  # Invalid project
    user_data = {
  "object": {
    "projectId": new_project["projectName"],
    "userId": 5555
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data)
    assert "errors" in executed1.keys()

    # Invalid user
    user_data = {
  "object": {
    "projectId": int(new_project["projectId"]),
    "userId": "some_user"
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data)
    assert "errors" in executed1.keys()

def test_update_user():
    '''Positive tests to change role, status & metadata of a user'''
    project_data = {
     "object": {
    "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
  }
}
    executed = check_post(PROJECT_CREATE_GLOBAL_QUERY,project_data)
    new_project = executed["data"]["createAgmtProject"]["data"]
    new_user_id = 7777

    user_data = {
  "object": {
    "projectId": new_project["projectId"],
    "userId": new_user_id
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data)
    data = executed1["data"]["createAgmtProjectUser"]["data"]
    assert executed1["data"]["createAgmtProjectUser"]["message"] == "User added in project successfully"
    assert int(data["projectId"]) == int(new_project['projectId']) 
    assert int(data["userId"]) == int(user_data["object"]["userId"])

    update_data = {
  "object": {
    "projectId": int(new_project["projectId"]),
    "userId": new_user_id
  }
}

    variable = {
    "projectname": project_data["object"]['projectName'],   
    "skip": 0,
  "limit": 10
}

    # change role
    update1 = update_data
    update1["object"]['userRole'] = 'owner'
    executed1 = gql_request(USER_EDIT_GLOBAL_QUERY,operation="mutation",variables=update1)
    data = executed1["data"]["editAgmtProjectUser"]["data"]
    assert executed1["data"]["editAgmtProjectUser"]["message"] == "User updated in project successfully"
    check_project_user(variable,new_user_id, role="owner")

    # change status
    update2 = update_data
    update2["object"]['active'] = False
    executed2 = gql_request(USER_EDIT_GLOBAL_QUERY,operation="mutation",variables=update2)
    data = executed2["data"]["editAgmtProjectUser"]["data"]
    assert executed2["data"]["editAgmtProjectUser"]["message"] == "User updated in project successfully"
    check_project_user(variable,new_user_id, status=False)

    # add metadata
    meta = "{\"last_filter\":\"mat\"}"
    update3 = update_data
    update3["object"]['metaData'] = meta
    executed3 = gql_request(USER_EDIT_GLOBAL_QUERY,operation="mutation",variables=update3)
    data = executed3["data"]["editAgmtProjectUser"]["data"]
    assert executed3["data"]["editAgmtProjectUser"]["message"] == "User updated in project successfully"
    check_project_user(variable,new_user_id,metadata={"last_filter":"mat"})

def test_update_user_invlaid():
    '''Negative test for update user'''
    project_data = {
     "object": {
    "projectName": "Test project 101",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
  }
}
    executed = check_post(PROJECT_CREATE_GLOBAL_QUERY,project_data)
    new_project = executed["data"]["createAgmtProject"]["data"]
    new_user_id = 8888

    user_data = {
  "object": {
    "projectId": new_project["projectId"],
    "userId": new_user_id
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data)
    data = executed1["data"]["createAgmtProjectUser"]["data"]
    assert executed1["data"]["createAgmtProjectUser"]["message"] == "User added in project successfully"
    assert int(data["projectId"]) == int(new_project['projectId']) 
    assert int(data["userId"]) == int(user_data["object"]["userId"])

    # not the added user
    update_data = {
  "object": {
    "projectId": new_project["projectId"],
    "userId": new_user_id+1,
    "active": False
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=update_data)
    assert "errors" in executed1.keys()

    #non existant project
    update_data = {
  "object": {
    "projectId": new_project["projectId"] +1,
    "userId": new_user_id,
    "active": False
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=update_data)
    assert "errors" in executed1.keys()

    # invalid metadata
    update_data = {
  "object": {
    "projectId": new_project["projectId"],
    "userId": new_user_id,
    "metaData": "A normal string intead of json"
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=update_data)
    assert "errors" in executed1.keys()

def test_soft_delete():
    '''Check if unsetting active status works the desired way'''
    project_data = {
     "object": {
    "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
  }
}
    for i in range(5):
      project_data["object"]["projectName"] = "Test project" + str(i)
      executed = check_post(PROJECT_CREATE_GLOBAL_QUERY,project_data)

    executed_get  = gql_request(PROJECT_GET_GLOBAL_QUERY)
    assert len(executed_get["data"]["agmtProjects"]) == 5

    get_project = executed_get["data"]["agmtProjects"][0]
    put_data = {
     "object": {
        "projectId":int(get_project['projectId']),
        "projectName":get_project['projectName'],
        "active": False
  }
}
    executed3 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data)
    assert isinstance(executed3, Dict)
    assert executed3["data"]["editAgmtProject"]["message"] == "Project updated successfully"
    assert not executed3["data"]["editAgmtProject"]["data"]["active"]

    executed_get  = gql_request(PROJECT_GET_GLOBAL_QUERY)
    assert len(executed_get["data"]["agmtProjects"]) == 4

