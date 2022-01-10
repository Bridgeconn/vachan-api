"""Test cases for agmt project management in GQL"""
from typing import Dict
#pylint: disable=E0401
from .test_agmt_projects import assert_positive_get,bible_books
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import  gql_request,assert_not_available_content_gql
from .test_gql_versions import GLOBAL_QUERY as version_query
from .test_gql_bibles import BOOK_ADD_QUERY
from .test_gql_sources import SOURCE_GLOBAL_QUERY as source_query
from .test_gql_versions import check_post as version_add
from .test_gql_sources import check_post as source_add
from .conftest import initial_test_users
from app.graphql_api import types
from app.schema import schemas
from . test_gql_auth_basic import login,SUPER_PASSWORD,SUPER_USER

headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "app":"Autographa"}
headers = {"contentType": "application/json", "accept": "application/json", "app":"Autographa"}

PROJECT_CREATE_GLOBAL_QUERY = """
    mutation createproject($object:InputCreateAGMTProject){
  createAgmtProject(projectArg:$object){
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
  editAgmtProject(projectArg:$object){
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
  createAgmtProjectUser(userArg:$object){
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
  editAgmtProjectUser(userArg:$object){
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
headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
def check_post(query,variables):
  """positive post test"""
  headers_auth = {"contentType": "application/json",
              "accept": "application/json",
              "App":"Autographa"}
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  #without Auth
  executed = gql_request(query=query,operation="mutation", variables=variables)
  assert "errors" in executed
  #with auth
  executed = gql_request(query=query,operation="mutation", variables=variables,
    headers=headers_auth)
  assert isinstance(executed, Dict)
  assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
  item =executed["data"]["createAgmtProject"]["data"] 
  if item["projectId"]:
      item["projectId"] = int(item["projectId"])
  assert_positive_get(item)
  return executed

def test_default_post_put_get():
  '''Positive test to create a project'''
  get_non_exisitng_project = """{
agmtProjects(projectName:"Test project 1"){
  projectId
  projectName
}
}"""
  #without auth
  executed = gql_request(query=get_non_exisitng_project)
  assert "errors" in executed
  #with auth
  headers_auth["app"] = types.App.AG.value
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  executed = gql_request(query=get_non_exisitng_project,headers=headers_auth)
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


  #Get created project
  get_query_projectname = """
    query agmtfetch($projectname:String){
agmtProjects(projectName:$projectname){
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
  variable = {
  "projectname": post_data["object"]["projectName"],
}
  executed_get = gql_request(get_query_projectname,headers=headers_auth,variables=variable)
  assert len(executed_get["data"]["agmtProjects"]) > 0

# upload books  
  put_data = {
    "object": {
      "projectId":new_project['projectId'],
      "uploadedUSFMs": [bible_books['mat'], bible_books['mrk']]
}
}
  headers_auth['app'] = types.App.AG.value
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  executed2 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data,
      headers=headers_auth)
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
  version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version"
    }
    }
  #Create a version
  version_add(version_query,version_variable)

  source_data = {
  "object": {
    "contentType": "bible",
    "language": "gu",
    "version": "TTT",
    "year": 2020,
    "accessPermissions": [
      types.SourcePermissions.CONTENT.value,
      types.SourcePermissions.OPENACCESS.value
    ],
  }
}
  executed_src = source_add(source_query,source_data)
  table_name = executed_src["data"]["addSource"]["data"]["sourceName"]

  #add books with vachan admin
  headers_auth_content = {"contentType": "application/json",
                "accept": "application/json"
            }
  headers_auth_content['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
  bible_variable = {
    "object": {
        "sourceName": table_name,
        "books": [
        {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id mrk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
]
    }
    }
  executed = gql_request(query=BOOK_ADD_QUERY,operation="mutation", variables=bible_variable,
      headers=headers_auth_content)
  assert executed["data"]["addBibleBook"]["message"] == "Bible books uploaded and processed successfully"
  
  put_data = {
     "object": {
        "projectId":new_project['projectId'],
        "selectedBooks": {
            "bible": table_name,
            "books": ["luk", "jhn"]
          }
  }
}  
  executed3 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data,
      headers=headers_auth)
  assert isinstance(executed3, Dict)
  assert executed3["data"]["editAgmtProject"]["message"] == "Project updated successfully"
  updated_project =executed3["data"]["editAgmtProject"]["data"]
  if updated_project["projectId"]:
      updated_project["projectId"] = int(updated_project["projectId"])
  assert_positive_get(updated_project)
  assert updated_project['metaData']['books'] == ['mat', 'mrk', 'luk', 'jhn']

  # fetch projects
  executed4 = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
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
  executed5 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data,
    headers=headers_auth)
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


def test_post_invalid():
    '''test input validation for project create'''
    # Missing mandatory content
    data1 = {
     "object": {
        "projectName": "Test project 1",
        "targetLanguageCode": "ml"
  }
}
    executed1 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data1,
      headers=headers_auth)
    assert "errors" in executed1.keys()

    data2 = {
     "object": {
        "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
  }
}
    executed2 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data2,
      headers=headers_auth)
    assert "errors" in executed2.keys()

    data3 = {
     "object": {
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
  }
}
    executed3 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data3,
      headers=headers_auth)
    assert "errors" in executed3.keys()

    # incorrect data in fields
    data4 = {
     "object": {
        "projectName": "Test project 1",
    "sourceLanguageCode": "2hindi",
    "targetLanguageCode": "ml"
  }
}
    executed4 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data4,
      headers=headers_auth)
    assert "errors" in executed4.keys()

    data5 = {
     "object": {
        "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "documentFormat": 2
  }
}
    executed5 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data5,
      headers=headers_auth)
    assert "errors" in executed5.keys()

    data6 = {
     "object": {
        "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "stopwords": ["a", "mromal", "list"]
  }
}
    executed6 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data6,
      headers=headers_auth)
    assert "errors" in executed6.keys()

    data7 = {
     "object": {
        "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "punctuations": "+_*())^%$#<>?:'"
  }
}
    executed7 = gql_request(PROJECT_CREATE_GLOBAL_QUERY,operation="mutation",variables=data7,
      headers=headers_auth)
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
    executed1 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=data,
      headers=headers_auth)
    assert "errors" in executed1.keys()

    # incorrect values in fields
    data = {
     "object": {
        "projectId": int(new_project['projectId']),
        "documentFormat": 2
  }
}
    executed1 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=data,
      headers=headers_auth)
    assert "errors" in executed1.keys()

    data = {
     "object": {
       "projectId": int(new_project['projectId']),
        "uploadedUSFMs": "mat"
  }
}
    executed1 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=data,
      headers=headers_auth)
    assert "errors" in executed1.keys()

    data = {
     "object": {
        "projectId": int(new_project['projectId']),
    "uploadedUSFMs": ["The contents of matthew in text"]
  }
}
    executed1 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=data,
      headers=headers_auth)
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
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']  
  executed = gql_request(project_get_with_name,operation="query",variables=variable,
    headers=headers_auth)
  found_user = False
  found_owner = False
  resp = executed["data"]["agmtProjects"][0]
  for user in resp['users']:
      if user['userId'] == user_id:
          found_user = True
          if role:
              assert user['userRole'] == role
          if status is not None:
              assert user['active'] == status
          if metadata:
              assert user['metaData'] == metadata
      if user['userRole'] == "projectOwner" :
          found_owner = True
  assert found_owner
  assert found_user

def test_add_user():
  '''Positive test to add a user to a project'''
  project_data = {
    "object": {
  "projectName": "Test project new1",
  "sourceLanguageCode": "hi",
  "targetLanguageCode": "ml"
}
}
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=project_data,
    headers=headers_auth)
  assert isinstance(executed, Dict)
  assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
  new_project = executed["data"]["createAgmtProject"]["data"]
  user_data = {
  "object": {
    "projectId": new_project["projectId"],
    "userId": 5555
  }
}  

  #non exisitng user
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
    headers=headers_auth)
  assert "errors" in executed1

  #Exisiting User
  user_data["object"]["userId"] = initial_test_users['AgUser']['test_user_id']
  #without auth
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data)
  assert "errors" in executed1
  #with auth
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
      headers=headers_auth)
  data = executed1["data"]["createAgmtProjectUser"]["data"]
  assert executed1["data"]["createAgmtProjectUser"]["message"] == "User added to project successfully"
  assert int(data["projectId"]) == int(new_project['projectId']) 
  assert data["userId"] == user_data["object"]["userId"]
  assert data["userRole"] == "projectMember"
  assert data['active']

  # fetch this project and check for new user
  new_user_id = initial_test_users['AgUser']['test_user_id']
  variable = {
    "projectname": project_data["object"]['projectName'],
    "skip": 0,
    "limit": 10
  }
  check_project_user (variable,role='projectMember',user_id=new_user_id)

def test_add_user_invalid():
  '''Negative tests to add a user to a project'''
  post_data = {
    "object": {
      "projectName": "Test Project 3",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
}
}
  executed = check_post(PROJECT_CREATE_GLOBAL_QUERY,variables=post_data)
  new_project = executed["data"]["createAgmtProject"]["data"]


    # No projectId
  user_data = {
"object": {
  "userId": 11111
}
}
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
    headers=headers_auth)
  assert "errors" in executed1.keys()

  # No User
  user_data = {
"object": {
  "projectId": int(new_project["projectId"])
}
}
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
    headers=headers_auth)
  assert "errors" in executed1.keys()

# Invalid project
  user_data = {
"object": {
  "projectId": new_project["projectName"],
  "userId": 5555
}
}
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
    headers=headers_auth)
  assert "errors" in executed1.keys()

  # Invalid user
  user_data = {
"object": {
  "projectId": int(new_project["projectId"]),
  "userId": "some_user"
}
}
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
    headers=headers_auth)
  assert "errors" in executed1.keys()

def test_update_user():
  '''Positive tests to change role, status & metadata of a user'''

  project_data = {
    "object": {
  "projectName": "Test project 1",
  "sourceLanguageCode": "hi",
  "targetLanguageCode": "ml"
}}
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=project_data,
    headers=headers_auth)
  assert isinstance(executed, Dict)
  assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
  new_project = executed["data"]["createAgmtProject"]["data"]
  new_user_id = initial_test_users['AgUser']['test_user_id']

  user_data = {
"object": {
  "projectId": new_project["projectId"],
  "userId": new_user_id
}
}
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
    headers=headers_auth)
  data = executed1["data"]["createAgmtProjectUser"]["data"]
  assert executed1["data"]["createAgmtProjectUser"]["message"] == "User added to project successfully"
  assert int(data["projectId"]) == int(new_project['projectId']) 
  assert data["userId"] == user_data["object"]["userId"]

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
  update1["object"]['userRole'] = 'projectOwner'
  #With Auth
  executed1 = gql_request(USER_EDIT_GLOBAL_QUERY,operation="mutation",variables=update1,
    headers=headers_auth)  
  data = executed1["data"]["editAgmtProjectUser"]["data"]
  assert executed1["data"]["editAgmtProjectUser"]["message"] == "User updated in project successfully"
  check_project_user(variable,role="projectOwner",user_id=new_user_id)

  # change status
  update2 = update_data
  update2["object"]['active'] = False
  executed2 = gql_request(USER_EDIT_GLOBAL_QUERY,operation="mutation",variables=update2,
    headers=headers_auth)
  data = executed2["data"]["editAgmtProjectUser"]["data"]
  assert executed2["data"]["editAgmtProjectUser"]["message"] == "User updated in project successfully"
  check_project_user(variable,new_user_id, status=False)

  # add metadata
  meta = "{\"last_filter\":\"mat\"}"
  update3 = update_data
  update3["object"]['metaData'] = meta
  executed3 = gql_request(USER_EDIT_GLOBAL_QUERY,operation="mutation",variables=update3,
    headers=headers_auth)
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
    new_user_id = initial_test_users['AgUser']['test_user_id']

    user_data = {
  "object": {
    "projectId": new_project["projectId"],
    "userId": new_user_id
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
      headers=headers_auth)
    data = executed1["data"]["createAgmtProjectUser"]["data"]
    assert executed1["data"]["createAgmtProjectUser"]["message"] == "User added to project successfully"
    assert int(data["projectId"]) == int(new_project['projectId']) 
    assert data["userId"] == user_data["object"]["userId"]

    # not the added user
    update_data = {
  "object": {
    "projectId": new_project["projectId"],
    "userId": "not-a-valid-user-11233",
    "active": False
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=update_data,
      headers=headers_auth)
    assert "errors" in executed1.keys()

    #non existant project
    update_data = {
  "object": {
    "projectId": new_project["projectId"] +1,
    "userId": new_user_id,
    "active": False
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=update_data,
      headers=headers_auth)
    assert "errors" in executed1.keys()

    # invalid metadata
    update_data = {
  "object": {
    "projectId": new_project["projectId"],
    "userId": new_user_id,
    "metaData": "A normal string intead of json"
  }
}
    executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=update_data,
      headers=headers_auth)
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
      executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=project_data,
        headers=headers_auth)
      assert isinstance(executed, Dict)
      assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"

    executed_get  = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
    assert len(executed_get["data"]["agmtProjects"]) >= 5

    # Get 1 uploaded project
    get_project_0_qry = """
    {
  agmtProjects(projectName:"Test project0"){
    projectId
    projectName
    active
  }
}"""

    get_project_0 = gql_request(get_project_0_qry,headers=headers_auth)
    project0_data = get_project_0["data"]["agmtProjects"][0]

    put_data = {
     "object": {
        "projectId":int(project0_data['projectId']),
        "projectName":project0_data['projectName'],
        "active": False
    }
  }
    executed3 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data,
      headers=headers_auth)
    assert isinstance(executed3, Dict)
    assert executed3["data"]["editAgmtProject"]["message"] == "Project updated successfully"
    assert not executed3["data"]["editAgmtProject"]["data"]["active"]

    #get the project deleted
    get_project_0 = gql_request(get_project_0_qry,headers=headers_auth)
    assert get_project_0["data"]["agmtProjects"] == []

#Access Rules and related Test

#Project Access Rules based tests
def test_agmt_projects_access_rule():
  """create related access rule and auth"""
  post_data = {
     "object": {
    "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
  }
}
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert isinstance(executed, Dict)
  assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
  new_project = executed["data"]["createAgmtProject"]["data"]
  project1_id = new_project['projectId']

  #create from app other than Autographa
  post_data["object"]["projectName"] = "Test project 2"
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  headers_auth["app"] = types.App.API.value
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert "errors" in executed
  post_data["object"]["projectName"] = "Test project 3"
  headers_auth["app"] = types.App.VACHAN.value
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert "errors" in executed
  post_data["object"]["projectName"] = "Test project 4"
  headers_auth["app"] = types.App.VACHANADMIN.value
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert "errors" in executed

  #create project by not allowed users
  post_data["object"]["projectName"] = "Test project 5"
  headers_auth["app"] = types.App.AG.value
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert "errors" in executed
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert "errors" in executed
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert "errors" in executed
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert "errors" in executed

  #Super Admin
  SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
  response = login(SA_user_data)
  token =  response["data"]["login"]["token"]

  headers_SA = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token,
                    "app":types.App.AG.value
                }
  #create with AGUser and SA
  post_data["object"]["projectName"] = "Test project 6"
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
  new_project = executed["data"]["createAgmtProject"]["data"]
  project6_id = new_project['projectId']
  post_data["object"]["projectName"] = "Test project 7"
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_SA)
  assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
  new_project = executed["data"]["createAgmtProject"]["data"]
  project7_id = new_project['projectId']

  #update Project
  put_data = {
    "object": {
      "projectId":project6_id,
      "uploadedUSFMs": [bible_books['mat'], bible_books['mrk']]
}
}
  headers_auth['app'] = types.App.AG.value
  #update with Owner of project
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
  executed2 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data,
      headers=headers_auth)
  assert isinstance(executed2, Dict)
  assert executed2["data"]["editAgmtProject"]["message"] == "Project updated successfully"

  #aguser project can be updated by super admin and Ag admin
  put_data = {
    "object": {
      "projectId":project6_id,
      "projectName":"New name for old project6"
}
}
  executed2 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data,
      headers=headers_SA)
  assert isinstance(executed2, Dict)
  assert executed2["data"]["editAgmtProject"]["message"] == "Project updated successfully"

  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  executed2 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data,
      headers=headers_auth)
  assert isinstance(executed2, Dict)
  assert executed2["data"]["editAgmtProject"]["message"] == "Project updated successfully"

  #update project with not Owner
  put_data["object"]["projectId"] = project7_id
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
  executed2 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data,
      headers=headers_auth)
  assert "errors" in executed2

  #project user create
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  new_user_id = initial_test_users['AgUser']['test_user_id']
  user_data = {
  "object": {
    "projectId": project1_id,
    "userId": new_user_id
  }
}
  #add user from another app than Autographa
  headers_auth["app"] = types.App.VACHANADMIN.value
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
      headers=headers_auth)
  assert "errors" in executed1
  headers_auth["app"] = types.App.API.value
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
      headers=headers_auth)
  assert "errors" in executed1
  headers_auth["app"] = types.App.VACHAN.value
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
      headers=headers_auth)
  assert "errors" in executed1
  #add user by not owner
  headers_auth["app"] = types.App.AG.value
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
      headers=headers_auth)
  assert "errors" in executed1
  #add from Autograpaha by allowed user
  project_data = {
     "object": {
    "projectName": "Test project 8",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
  }
}
  executed = check_post(PROJECT_CREATE_GLOBAL_QUERY,project_data)
  new_project = executed["data"]["createAgmtProject"]["data"]
  project8_id = new_project['projectId']
  new_user_id = initial_test_users['AgUser']['test_user_id']

  user_data = {
"object": {
  "projectId": project8_id,
  "userId": new_user_id
}
}
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
    headers=headers_auth)
  data = executed1["data"]["createAgmtProjectUser"]["data"]
  assert executed1["data"]["createAgmtProjectUser"]["message"] == "User added to project successfully"
  assert int(data["projectId"]) == int(new_project['projectId']) 
  assert data["userId"] == user_data["object"]["userId"]
  #update user with not owner
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
  update_data = {
  "object": {
    "projectId": project7_id,
    "userId": new_user_id
  }
}
  # change role
  update_data["object"]['userRole'] = 'projectOwner'
  executed1 = gql_request(USER_EDIT_GLOBAL_QUERY,operation="mutation",variables=update_data,
    headers=headers_auth)  
  assert "errors" in executed1

def test_get_project_access_rules():
  """test for get project access rules"""
  post_data = {
     "object": {
    "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
  }
}
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert isinstance(executed, Dict)
  assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
  new_project = executed["data"]["createAgmtProject"]["data"]
  project1_id = new_project['projectId']

  post_data["object"]["projectName"] = "Test project 2"
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert isinstance(executed, Dict)
  assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
  new_project = executed["data"]["createAgmtProject"]["data"]
  project2_id = new_project['projectId']

  post_data["object"]["projectName"] = "Test project 3"
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_auth)
  assert isinstance(executed, Dict)
  assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
  new_project = executed["data"]["createAgmtProject"]["data"]
  project3_id = new_project['projectId']

  #Super Admin
  SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
  response = login(SA_user_data)
  token =  response["data"]["login"]["token"]

  headers_SA = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token,
                    "app":types.App.AG.value
                }
  #get project from apps other than autographa
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  headers_auth["app"] = types.App.API.value
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert "errors" in executed
  headers_auth["app"] = types.App.VACHANADMIN.value
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert "errors" in executed
  headers_auth["app"] = types.App.VACHAN.value
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert "errors" in executed

  #get project from Autographa with not allowed users get empty result
  headers_auth["app"] = types.App.AG.value
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert_not_available_content_gql(executed["data"]["agmtProjects"])
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert_not_available_content_gql(executed["data"]["agmtProjects"])
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert_not_available_content_gql(executed["data"]["agmtProjects"])

  #get all project by SA , AgAdmin, Bcs internal dev
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_SA)
  assert len(executed["data"]["agmtProjects"]) >= 3
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert len(executed["data"]["agmtProjects"]) >= 3
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert len(executed["data"]["agmtProjects"]) >= 3

  #get project by project owner Aguser only get owner project
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert len(executed["data"]["agmtProjects"]) >= 2

  #create project by SA and add Aguser as member to the project
  post_data["projectName"] = 'Test project 4'
  executed = gql_request(query=PROJECT_CREATE_GLOBAL_QUERY,operation="mutation", variables=post_data,
        headers=headers_SA)
  assert isinstance(executed, Dict)
  assert executed["data"]["createAgmtProject"]["message"] == "Project created successfully"
  new_project = executed["data"]["createAgmtProject"]["data"]
  project4_id = new_project['projectId']
  new_user_id = initial_test_users['AgUser']['test_user_id']
  user_data = {
"object": {
  "projectId": project4_id,
  "userId": new_user_id
}
}
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
  executed1 = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data,
    headers=headers_SA)
  data = executed1["data"]["createAgmtProjectUser"]["data"]
  assert executed1["data"]["createAgmtProjectUser"]["message"] == "User added to project successfully"

  #get after add as member
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert len(executed["data"]["agmtProjects"]) >= 3

  #A new Aguser requesting for all projecrts AGuser2
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser2']['token']
  executed = gql_request(PROJECT_GET_GLOBAL_QUERY,headers=headers_auth)
  assert_not_available_content_gql(executed["data"]["agmtProjects"])
