'''Test cases for SanketMAST projects related APIs'''
from schema import schema_auth
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_bibles import check_post as add_bible, gospel_books_data
from .test_resources import check_post as add_resource
from .test_versions import check_post as add_version
from .conftest import initial_test_users
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user

UNIT_URL = '/v2/text/translate/token-based/projects'
USER_URL = '/v2/text/translate/token-based/project/user'
SENTENCE_URL = '/v2/text/translate/token-based/project/sentences'
RESTORE_URL = '/v2/admin/restore'
headers = {"contentType": "application/json", "accept": "application/json", "app":"SanketMAST"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "app":"SanketMAST"
            }

bible_books = {
    "mat":  "\\id MAT\n\\c 1\n\\p\n\\v 1 इब्राहीम के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस "+
            "प्रकार है:\n\\v 2 इब्राहीम का पुत्र था इसहाक और इसहाक का पुत्र हुआ याकूब। फिर याकूब "+
            "से यहूदा और उसके भाई उत्पन्न हुए।\n\\v 3 यहूदा के बेटे थे फिरिस और जोरह। (उनकी माँ "+
            "का नाम तामार था।) फिरिस, हिस्रोन का पिता था। हिस्रोन राम का पिता था।",
    "mrk":    "\\id MRK\n\\c 1\n\\p\n\\v 1 यह परमेश्वर के पुत्र यीशु मसीह के शुभ संदेश का प्रारम्भ"+
            " है।\n\\v 2 भविष्यवक्ता यशायाह की पुस्तक में लिखा है कि: “सुन! मैं अपने दूत को तुझसे"+
            " पहले भेज रहा हूँ। वह तेरे लिये मार्ग तैयार करेगा।”\n\\v 3 “जंगल में किसी पुकारने "+
            "वाले का शब्द सुनाई दे रहा है: ‘प्रभु के लिये मार्ग तैयार करो। और उसके लिये राहें "+
            "सीधी बनाओ।’”\n\\v 4 यूहन्ना लोगों को जंगल में बपतिस्मा देते आया था। उसने लोगों से"+
            " पापों की क्षमा के लिए मन फिराव का बपतिस्मा लेने को कहा।\n\\v 5 फिर समूचे यहूदिया"+
            " देश के और यरूशलेम के लोग उसके पास गये और उस ने यर्दन नदी में उन्हें बपतिस्मा दिया"+
            "। क्योंकि उन्होंने अपने पाप मान लिये थे।"
}

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "projectId" in item
    assert isinstance(item['projectId'], int)
    assert "projectName" in item
    assert "sourceLanguage" in item
    assert "code" in item['sourceLanguage']
    assert "targetLanguage" in item
    assert "code" in item['targetLanguage']
    assert 'metaData' in item
    assert 'books' in item['metaData']
    assert 'useDataForLearning' in item['metaData']
    assert "active" in item
    assert "users" in item
    assert isinstance(item['users'], list)
    assert "createTime" in item
    assert "updateTime" in item


def check_post(data, auth_token=None):
    '''creates a projects'''
    headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "app":"SanketMAST"}
    if not auth_token:
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    else:
        headers_auth['Authorization'] = "Bearer"+" "+auth_token
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    return response

def test_default_post_put_get():
    '''Positive test to create a project'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.get(UNIT_URL+'?project_name=Test project 1',headers=headers_auth)
    assert_not_available_content(resp)

    # create with minimum data
    post_data = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    new_project = response.json()['data']
    assert_positive_get(new_project)

    # check if all defaults are coming
    assert new_project['metaData']["useDataForLearning"]
    assert isinstance(new_project['metaData']['books'], list)
    assert len(new_project['metaData']['books']) == 0
    assert new_project['active']

    # upload books
    put_data = {
    "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    response2 = client.put(UNIT_URL+'?project_id='+str(new_project['projectId']),\
         headers=headers_auth, json=put_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"
    updated_project = response2.json()['data']
    assert_positive_get(updated_project)

    assert new_project['projectId'] == updated_project['projectId']
    assert new_project['projectName'] == updated_project['projectName']
    assert updated_project['metaData']['books'] == ['mat', 'mrk']

    #add bible , create resource with open-access

    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for bibles",
    }
    add_version(version_data)
    resource_data = {
        "resourceType": "bible",
        "language": "gu",
        "version": "TTT",
        "year": 3030,
        "versionTag": 1,
        "accessPermissions": [
            "content","open-access"
        ],
    }
    resource = add_resource(resource_data)
    table_name = resource.json()['data']['resourceName']

    #add books with vachan admin
    headers_auth_content = {"contentType": "application/json",
                "accept": "application/json"
            }
    headers_auth_content['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    resp = client.post('/v2/bibles/'+table_name+'/books', headers=headers_auth_content, json=gospel_books_data)

    # resp, resource_name = add_bible(gospel_books_data)
    assert resp.status_code == 201

    put_data = {
        "selectedBooks": {
            "bible": table_name,
            "books": ["luk", "jhn"]
          }
    }
    response2b = client.put(UNIT_URL+'?project_id='+str(new_project['projectId']),\
         headers=headers_auth, json=put_data)
    assert response2b.status_code == 201
    assert response2b.json()['message'] == "Project updated successfully"
    updated_project = response2b.json()['data']
    assert_positive_get(updated_project)
    assert updated_project['metaData']['books'] == ['mat', 'mrk', 'luk', 'jhn']

    # fetch projects
    response3 = client.get(UNIT_URL,headers=headers_auth)
    assert len(response3.json()) >= 1
    found_project = False
    for proj in response3.json():
        if proj['projectName'] == post_data['projectName']:
            found_project = True
            fetched_project = proj
    assert found_project
    assert_positive_get(fetched_project)

    assert fetched_project['projectName'] == post_data['projectName']
    assert fetched_project['sourceLanguage']['code'] == post_data['sourceLanguageCode']
    assert fetched_project['targetLanguage']['code'] == post_data['targetLanguageCode']
    assert fetched_project['metaData']['books'] == ['mat', 'mrk', 'luk', 'jhn']

    # change name
    put_data = {
        "projectName":"New name for old project"}
    response4 = client.put(UNIT_URL+'?project_id='+str(new_project['projectId']),\
         headers=headers_auth, json=put_data)
    assert response4.status_code == 201
    assert response4.json()['message'] == "Project updated successfully"
    updated_project = response4.json()['data']
    assert_positive_get(updated_project)
    assert updated_project['projectName']== "New name for old project"


    # create with all possible options
    post_data = {
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
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    new_project = response.json()['data']
    assert_positive_get(new_project)

    # add a few more projects
    post_data = {
      "projectName": "Test Project 3",
      "sourceLanguageCode": "hi",
      "targetLanguageCode": "ml"
    }
    resp = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert resp.status_code == 201
    post_data = {
      "projectName": "Test Project 4",
      "sourceLanguageCode": "hi",
      "targetLanguageCode": "ml"
    }
    resp = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert resp.status_code == 201
    
    check_default_get(UNIT_URL,headers_auth, assert_positive_get)


def test_post_invalid():
    '''test input validation for project create'''
    # Missing mandatory content
    data1 = {
    "projectName": "Test project 1",
    "targetLanguageCode": "ml"
    }
    res1 = client.post(UNIT_URL, headers=headers_auth, json=data1)
    assert_input_validation_error(res1)

    data2 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    }
    res2 = client.post(UNIT_URL, headers=headers_auth, json=data2)
    assert_input_validation_error(res2)

    data3 = {
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
    }
    res3 = client.post(UNIT_URL, headers=headers_auth, json=data3)
    assert_input_validation_error(res3)

    # incorrect data in fields
    data1 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "2hindi",
    "targetLanguageCode": "ml"
    }
    res1 = client.post(UNIT_URL, headers=headers_auth, json=data1)
    assert_input_validation_error(res1)

    data2 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "useDataForLearning": "use"
    }
    res2 = client.post(UNIT_URL, headers=headers_auth, json=data2)
    assert_input_validation_error(res2)

    data3 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "stopwords": ["a", "mromal", "list"]
    }
    res3 = client.post(UNIT_URL, headers=headers_auth, json=data3)
    assert_input_validation_error(res3)

    data4 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "punctuations": "+_*())^%$#<>?:'"
    }
    res4 = client.post(UNIT_URL, headers=headers_auth, json=data4)
    assert_input_validation_error(res4)

def test_put_invalid():
    '''Give incorrect data for project update'''
    post_data = {"projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"}
    resp = check_post(post_data)
    assert resp.json()['message'] == "Project created successfully"
    new_project = resp.json()['data']

    # missing projectId
    data = {"active": False}
    resp = client.put(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(resp)

    # incorrect values in fields
    data = {"active": "delete"}
    resp = client.put(UNIT_URL+'?project_id='+str(new_project['projectId']), \
        headers=headers_auth, json=data)
    assert_input_validation_error(resp)

    data = {"uploadedUSFMs": "mat"}
    resp = client.put(UNIT_URL+'?project_id='+str(new_project['projectId']), \
        headers=headers_auth, json=data)
    assert_input_validation_error(resp)

    data = {"uploadedUSFMs": ["The contents of matthew in text"]}
    resp = client.put(UNIT_URL+'?project_id='+str(new_project['projectId']), \
        headers=headers_auth, json=data)
    assert resp.status_code == 415
    assert resp.json()['error'] == "Not the Required Type"

def check_project_user(project_name, user_id, role=None, status=None, metadata = None):
    '''Make sure the user is in project and if specified, check for other values'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    response = client.get(UNIT_URL+'?project_name='+project_name,headers=headers_auth)
    found_user = False
    found_owner = False

    for user in response.json()[0]['users']:
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
        "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
    }
    resp = check_post(project_data)
    assert resp.status_code == 201
    new_project = resp.json()['data']

    #not exising user id 
    new_user_id = str(5555)
    response = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert response.status_code == 404
    assert response.json()['error'] == 'Requested Content Not Available'
    #exising user
    new_user_id = initial_test_users['SanketMASTUser']['test_user_id']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    response = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert response.status_code == 201
    assert response.json()['message'] == "User added to project successfully"
    data = response.json()['data']
    assert data["project_id"] == new_project['projectId']
    assert data["userId"] == new_user_id
    assert data["userRole"] == "projectMember"
    assert data['active']

    # fetch this project and check for new user
    check_project_user(project_data['projectName'], new_user_id, role='projectMember')


def test_add_user_invalid():
    '''Negative tests to add a user to a project'''
    project_data = {
        "projectName": "Test project 10",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
    }
    resp = check_post(project_data)
    assert resp.status_code == 201
    new_project = resp.json()['data']

    # No projectId
    resp = client.post(USER_URL+'?user_id=11111',headers=headers_auth)
    assert_input_validation_error(resp)

    # No User
    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId']),headers=headers_auth)
    assert_input_validation_error(resp)

    # Invalid project
    resp = client.post(USER_URL+'?project_id='+str(new_project['projectName'])+
        '&user_id=111111',headers=headers_auth)
    assert_input_validation_error(resp)

    # Invalid user
    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id=some_name',headers=headers_auth)
    assert resp.status_code == 404
    assert resp.json()['error'] == 'Requested Content Not Available'


def test_update_user():
    '''Positive tests to change role, status & metadata of a user'''
    project_data = {
        "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
    }
    resp = check_post(project_data)
    assert resp.json()['message'] == "Project created successfully"
    new_project = resp.json()['data']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    new_user_id = initial_test_users['SanketMASTUser']['test_user_id']

    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert resp.json()['message'] == "User added to project successfully"

    update_data = {
        # "project_id": new_project['projectId'],
        "userId": new_user_id
    }

    # change role
    update1 = update_data
    update1['userRole'] = 'projectOwner'
    # response1 = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
    #     '&user_id='+str(new_user_id),headers=headers_auth)
    response1 = client.put(USER_URL+'?project_id='+str(new_project['projectId']), headers=headers_auth, json=update1)
    assert response1.status_code == 201
    assert response1.json()['message'] == "User updated in project successfully"
    check_project_user(project_data['projectName'], new_user_id, role="projectOwner")

    # change status
    update2 = update_data
    update2['active'] = False
    response2 = client.put(USER_URL+'?project_id='+str(new_project['projectId']), headers=headers_auth, json=update2)
    assert response2.status_code == 201
    assert response2.json()['message'] == "User updated in project successfully"
    check_project_user(project_data['projectName'], new_user_id, status=False)

    # add metadata
    meta = {"last_filter": "mat"}
    update3 = update_data
    update3['metaData'] = meta
    response3 = client.put(USER_URL+'?project_id='+str(new_project['projectId']), headers=headers_auth, json=update3)
    assert response3.status_code == 201
    assert response3.json()['message'] == "User updated in project successfully"
    check_project_user(project_data['projectName'], new_user_id, metadata=meta)


def test_update_user_invlaid():
    '''Negative test for update user'''
    project_data = {
        "projectName": "Test project 101",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
    }
    resp = check_post(project_data)
    assert resp.json()['message'] == "Project created successfully"
    new_project = resp.json()['data']
    new_user_id = initial_test_users['SanketMASTUser']['test_user_id']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert resp.json()['message'] == "User added to project successfully"


    # not the added user
    update_data = {
        "userId": "not-a-valid-user-11233",
        "active": False
    }
    response = client.put(USER_URL+'?project_id='+str(new_project['projectId']), headers=headers_auth, json=update_data)
    assert response.status_code == 404
    assert response.json()['details'] == "User-project pair not found"

    #non existant project
    update_data = {
        "userId": new_user_id,
        "active": False
    }
    response = client.put(USER_URL+'?project_id='+str(new_project['projectId']+1), headers=headers_auth, json=update_data)
    assert response.status_code == 404
    assert response.json()['details'] == f"Project with id, {new_project['projectId']+1}, not present"


    # invalid status
    update_data = {
        "userId": new_user_id,
        "active": "Delete"
    }
    response = client.put(USER_URL+'?project_id='+str(new_project['projectId']+1), headers=headers_auth, json=update_data)
    assert_input_validation_error(response)

    # invalid metadata
    update_data = {
        "userId": new_user_id,
        "metaData": "A normal string intead of json"
    }
    response = client.put(USER_URL+'?project_id='+str(new_project['projectId']+1), headers=headers_auth, json=update_data)
    assert_input_validation_error(response)


def test_soft_delete():
    '''Check if unsetting active status works the desired way'''
    data = [
        {
          "projectName": "Test Project 1",
          "sourceLanguageCode": "hi",
          "targetLanguageCode": "ml"
        },
        {
          "projectName": "Test Project 2",
          "sourceLanguageCode": "hi",
          "targetLanguageCode": "ml"
        },
        {
          "projectName": "Test Project 3",
          "sourceLanguageCode": "hi",
          "targetLanguageCode": "ml"
        },
        {
          "projectName": "Test Project 4",
          "sourceLanguageCode": "hi",
          "targetLanguageCode": "ml"
        },
        {
          "projectName": "Test Project 5",
          "sourceLanguageCode": "hi",
          "targetLanguageCode": "ml"
        }
    ]

    delete_data = [
    {"project_name": "Test Project 4"},
    {"project_name": "Test Project 5"}
    ]
    for item in data:
        response = check_post(item)
        assert response.status_code == 201
        assert response.json()['message'] == "Project created successfully"

    get_response1 = client.get(UNIT_URL,headers=headers_auth)
    assert len(get_response1.json()) >= len(data)


    # positive PUT
    for item in delete_data:
        # find the project id
        resp = client.get(UNIT_URL+"?project_name="+item['project_name'],headers=headers_auth)
        assert resp.status_code == 200
        project_id = resp.json()[0]['projectId']

        put_obj = {"active": False}
        response = client.put(UNIT_URL+'?project_id='+str(project_id), headers=headers_auth, json=put_obj)
        assert response.status_code == 201
        assert response.json()['message'] == 'Project updated successfully'
        assert not response.json()['data']['active']

    get_response2 = client.get(UNIT_URL,headers=headers_auth)
    assert len(get_response2.json()) == len(get_response1.json()) - len(delete_data)

    get_response3 = client.get(UNIT_URL+'?active=false',headers=headers_auth)
    assert len(get_response3.json()) >= len(delete_data)


#Access Rules and related Test

#Project Access Rules based tests
def test_agmt_projects_access_rule():
    """create related access rule and auth"""
    #with and without auth
    post_data = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
    }
    response = client.post(UNIT_URL, headers=headers, json=post_data)
    assert response.status_code == 401
    assert 'error' in response.json()
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project1_id = response.json()['data']['projectId']

    #create from app other than SanketMAST
    post_data["projectName"] = "Test project 2"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    headers_auth["app"] = "API-user"
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    post_data["projectName"] = "Test project 3"
    headers_auth["app"] = "Vachan-online or vachan-app"
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    post_data["projectName"] = "Test project 4"
    headers_auth["app"] = "VachanAdmin"
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

    #create project by not allowed users
    post_data["projectName"] = "Test project 5"
    headers_auth["app"] = "SanketMAST"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

    #Super Admin
    SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(SA_user_data)
    assert response.json()['message'] == "Login Succesfull"
    test_SA_token = response.json()["token"]

    #create with AGUser and SA
    post_data["projectName"] = "Test project 6"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project6_id = response.json()['data']['projectId']
    post_data["projectName"] = "Test project 7"
    headers_auth['Authorization'] = "Bearer"+" "+test_SA_token
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project7_id = response.json()['data']['projectId']

    #update Project
    put_data = {
    "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    #update with Owner of project
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    response2 = client.put(UNIT_URL+'?project_id='+str(project6_id), headers=headers_auth, json=put_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"
    updated_project = response2.json()['data']
    assert updated_project['metaData']['books'] == ['mat', 'mrk']

    #aguser project can be updated by super admin and SanketMAST admin
    put_data = {
        "projectName":"New name for old project6"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    response2 = client.put(UNIT_URL+'?project_id='+str(project6_id), headers=headers_auth, json=put_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"
    assert response2.json()['data']['projectName'] == put_data["projectName"]
    put_data["projectName"] = "New name for project7 by SA"
    headers_auth['Authorization'] = "Bearer"+" "+test_SA_token
    response2 = client.put(UNIT_URL+'?project_id='+str(project6_id), headers=headers_auth, json=put_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"
    assert response2.json()['data']['projectName'] == put_data["projectName"]

    #update project with not Owner
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    response2 = client.put(UNIT_URL+'?project_id='+str(project7_id), headers=headers_auth, json=put_data)
    assert response2.status_code == 403
    assert response2.json()['error'] == 'Permission Denied'

    #project user create
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    new_user_id = initial_test_users['SanketMASTUser']['test_user_id']
    #add user from another app than SanketMAST
    headers_auth["app"] = "VachanAdmin"
    response = client.post(USER_URL+'?project_id='+str(project1_id)+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    headers_auth["app"] = "Vachan-online or vachan-app"
    response = client.post(USER_URL+'?project_id='+str(project1_id)+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    headers_auth["app"] = "API-user"
    response = client.post(USER_URL+'?project_id='+str(project1_id)+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    #add user by not owner
    headers_auth["app"] = "SanketMAST"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    response = client.post(USER_URL+'?project_id='+str(project1_id)+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    #add from Autograpaha by allowed user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    post_data["projectName"] = "Test project 8"
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project8_id = response.json()['data']['projectId']

    response = client.post(USER_URL+'?project_id='+str(project8_id)+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert response.status_code == 201
    assert response.json()['message'] == "User added to project successfully"
    data = response.json()['data']
    assert data["project_id"] == project8_id
    assert data["userId"] == new_user_id
    assert data["userRole"] == "projectMember"
    assert data['active']

    #update user with not owner
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    update_data = {
        "userId": new_user_id
    }
    # add metadata
    meta = {"last_filter": "luk"}
    update_data['metaData'] = meta
    response3 = client.put(USER_URL+'?project_id='+str(project8_id), headers=headers_auth, json=update_data)
    assert response3.status_code == 403
    assert response3.json()['error'] == 'Permission Denied'
    #update with owner
    post_data['projectName'] = 'Test project 1'
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    response3 = client.put(USER_URL+'?project_id='+str(project8_id), headers=headers_auth, json=update_data)
    assert response3.status_code == 201
    assert response3.json()['message'] == "User updated in project successfully"

def test_get_project_access_rules():
    """test for get project access rules"""
    #create projects
    post_data = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project1_id = response.json()['data']['projectId']

    post_data["projectName"] = "Test project 2"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project2_id = response.json()['data']['projectId']

    post_data["projectName"] = "Test project 3"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project3_id = response.json()['data']['projectId']

    #Super Admin
    SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(SA_user_data)
    assert response.json()['message'] == "Login Succesfull"
    test_SA_token = response.json()["token"]

    #get project from apps other than autographa
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    headers_auth["app"] = "API-user"
    response = client.get(UNIT_URL,headers=headers_auth)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    headers_auth["app"] = "Vachan-online or vachan-app"
    response = client.get(UNIT_URL,headers=headers_auth)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    headers_auth["app"] = "VachanAdmin"
    response = client.get(UNIT_URL,headers=headers_auth)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

    #get project from SanketMAST with not allowed users get empty result
    headers_auth["app"] = "SanketMAST"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) == 0
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) == 0
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) == 0

    #get all project by SA , SanketMASTAdmin, Bcs internal dev
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) >= 3

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) >= 3

    headers_auth['Authorization'] = "Bearer"+" "+ test_SA_token
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) >= 3

    #get project by project owner SanketMASTuser only get owner project
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) >= 2

    #create project by SA and add SanketMASTuser as member to the project
    post_data["projectName"] = 'Test project 4'
    headers_auth['Authorization'] = "Bearer"+" "+ test_SA_token
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project4_id = response.json()['data']['projectId']

    new_user_id = initial_test_users['SanketMASTUser']['test_user_id']
    response = client.post(USER_URL+'?project_id='+str(project4_id)+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert response.status_code == 201
    assert response.json()['message'] == "User added to project successfully"
    data = response.json()['data']
    assert data["project_id"] == project4_id
    assert data["userId"] == new_user_id
    assert data["userRole"] == "projectMember"
    assert data['active']

    #get after add as member
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    response = client.get(UNIT_URL+"?user_id="+new_user_id,headers=headers_auth)
    assert len(response.json()) >= 3
    for proj in response.json():
        assert proj['projectName'] in ["Test project 4","Test project 3","Test project 2"]

   #A new SanketMASTuser requesting for all projecrts
    # test_ag_user_data = {
    #     "email": "testaguser@test.com",
    #     "password": "passwordag@1"
    # }
    # response = register(test_ag_user_data, apptype='SanketMAST')
    # ag_user_id = [response.json()["registered_details"]["id"]]
    # ag_user_token = response.json()["token"]

    #get projects where user have no projects result is []
    headers_auth["app"] = "SanketMAST"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser2']['token']
    # headers_auth['Authorization'] = "Bearer"+" "+ag_user_token
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) == 0
    # delete_user_identity(ag_user_id)


def test_create_n_update_times():
    '''Test to ensure created time and last updated time are included in project GET response'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.get(UNIT_URL+'?project_name=Test project 1',headers=headers_auth)
    assert_not_available_content(resp)

    # create with minimum data
    post_data = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
    }
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    new_project = response.json()['data']
    assert_positive_get(new_project)
    project_id = response.json()['data']['projectId']

    response = client.get(f"{UNIT_URL}?project_name={post_data['projectName']}",headers=headers_auth)
    assert response.json()[0]["createTime"] is not None
    assert response.json()[0]['updateTime'] is not None
    assert response.json()[0]["createTime"] == response.json()[0]["updateTime"]

    # Make an update to project
    update_data = {
        "metaData": {"last_filter": "luk"}
    }
    response2 = client.put(UNIT_URL+'?project_id='+str(project_id), headers=headers_auth, json=update_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"

    response = client.get(f"{UNIT_URL}?project_name={post_data['projectName']}",headers=headers_auth)
    assert response.json()[0]["createTime"] != response.json()[0]["updateTime"]
 

def test_delete_project():
    '''Test the removal a project'''

    #Create Project
    project_data = {
        "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
    }
    resp = check_post(project_data, auth_token=initial_test_users['SanketMASTAdmin']['token'])
    assert resp.status_code == 201
    assert resp.json()['message'] == "Project created successfully"
    new_project = resp.json()['data']
    project_id = new_project['projectId']
    assert_positive_get(new_project)

    # fetch project
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    get_response = client.get(UNIT_URL,headers=headers_auth)
    assert len(get_response.json()) >= 1
    found_project = False
    for proj in get_response.json():
        if proj['projectName'] == project_data['projectName']:
            found_project = True
            fetched_project = proj
    assert found_project
    assert_positive_get(fetched_project)

    assert fetched_project['projectName'] == project_data['projectName']
    assert fetched_project['sourceLanguage']['code'] == project_data['sourceLanguageCode']
    assert fetched_project['targetLanguage']['code'] == project_data['targetLanguageCode']

    #Delete Project with no auth
    resp = client.delete(UNIT_URL+'?project_id='+str(new_project['projectId']),headers=headers)
    assert resp.status_code == 401
    assert resp.json()['details'] == "Access token not provided or user not recognized."

    # deleting non existing  project
    invalid_project_id = 9999
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.delete(UNIT_URL+'?project_id='+str(invalid_project_id),headers=headers_auth)
    assert resp.status_code == 404
    assert resp.json()['details'] == f"Project with id, {invalid_project_id}, not present"

    # Delete as unauthorized users
    for user in ['APIUser','VachanAdmin','VachanUser','BcsDev','VachanContentAdmin','VachanContentViewer']:
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users[user]['token']
        response =client.delete(UNIT_URL+'?project_id='+str(project_id),headers=headers_auth)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    # Delete as SanketMASTAdmin- Positive test
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.delete(UNIT_URL+'?project_id='+str(project_id),headers=headers_auth)
    assert resp.status_code == 201
    assert "successfull" in resp.json()['message']

    #Ensure deleted project is not present
    resp = client.get(UNIT_URL+'?project_name=Test project 1',headers=headers_auth)
    assert_not_available_content(resp)

    #Create and Delete Project with SanketMASTUser - Positive Test
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    post_resp_aguser = check_post(project_data, auth_token=initial_test_users['SanketMASTUser']['token'])
    assert post_resp_aguser.status_code == 201
    #Ensure presence of created project
    get_response = client.get(UNIT_URL,headers=headers_auth)
    assert len(get_response.json()) >= 1
    found_project = False
    for proj in get_response.json():
        if proj['projectName'] == project_data['projectName']:
            found_project = True
            fetched_project = proj
    assert found_project
    assert_positive_get(fetched_project)
    #Get project Id
    new_project = post_resp_aguser.json()['data']
    project_id = new_project['projectId']
    #Delete
    delete_resp_aguser = client.delete(UNIT_URL+'?project_id='+str(project_id),headers=headers_auth)
    assert delete_resp_aguser.status_code == 201
    #Ensure deleted project is not present
    resp = client.get(UNIT_URL+'?project_name=Test project 1',headers=headers_auth)
    assert_not_available_content(resp)

     #Create and Delete Project with SuperAdmin - Positive Test
    #Login as Super Admin
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth['Authorization'] = "Bearer"+" "+test_user_token
    post_resp_sa = check_post(project_data, auth_token=test_user_token)
    assert post_resp_sa.status_code == 201
    #Ensure presence of created project
    get_response = client.get(UNIT_URL,headers=headers_auth)
    assert len(get_response.json()) >= 1
    found_project = False
    for proj in get_response.json():
        if proj['projectName'] == project_data['projectName']:
            found_project = True
            fetched_project = proj
    assert found_project
    assert_positive_get(fetched_project)
    #Get project Id
    new_project = post_resp_sa.json()['data']
    project_id = new_project['projectId']
    #Delete
    delete_resp_sa= client.delete(UNIT_URL+'?project_id='+str(project_id),headers=headers_auth)
    assert delete_resp_sa.status_code == 201
    #Ensure deleted project is not present
    resp = client.get(UNIT_URL+'?project_name=Test project 1',headers=headers_auth)
    assert_not_available_content(resp)
    logout_user(test_user_token)

def test_restore_project():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deleting project
    project_data = {
        "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
    }
    post_resp= check_post(project_data, auth_token=initial_test_users['SanketMASTAdmin']['token'])
    assert post_resp.status_code == 201

    #Get project Id
    project_id = post_resp.json()['data']['projectId']

    #Delete
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    delete_resp= client.delete(UNIT_URL+'?project_id='+str(project_id),headers=headers_auth)
    assert delete_resp.status_code == 201
    #Ensure deleted project is not present
    resp = client.get(UNIT_URL+'?project_name=Test project 1',headers=headers_auth)
    assert_not_available_content(resp)

    deleteditem_id = delete_resp.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring data
    #Restore without authentication - Negative Test
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore project with other API user,VachanAdmin,SanketMASTAdmin,SanketMASTUser,VachanUser,BcsDev and APIUSer2 - Negative Test
    for user in ['APIUser','VachanAdmin','SanketMASTAdmin','SanketMASTUser','VachanUser','BcsDev','APIUser2','VachanContentAdmin','VachanContentViewer']:
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users[user]['token']
        response = client.put(RESTORE_URL, headers=headers_auth, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Restore Project with Super Admin - Positive Test
     # Login as Super Admin
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth['Authorization'] = "Bearer"+" "+test_user_token

    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleteditem_id} restored successfully"

    #Ensure presence of restored project
    get_response = client.get(UNIT_URL,headers=headers_auth)
    assert len(get_response.json()) >= 1
    found_project = False
    for proj in get_response.json():
        if proj['projectName'] == project_data['projectName']:
            found_project = True
            fetched_project = proj
    assert found_project
    assert_positive_get(fetched_project)

    #restore with missing data - Negative Test
    data = {}
    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #Restore with invalid item id - Negative Test
    data = {"itemId":9999}
    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    logout_user(test_user_token)

def test_delete_user():
    '''Test the removal of a user from a project'''
    project_data = {
        "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
    }
    resp = check_post(project_data, auth_token=initial_test_users['SanketMASTAdmin']['token'])
    assert resp.json()['message'] == "Project created successfully"
    new_project = resp.json()['data']
    new_user_id = initial_test_users['SanketMASTUser']['test_user_id']

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert resp.json()['message'] == "User added to project successfully"

    # fetch this project and check for new user
    check_project_user(project_data['projectName'], new_user_id, role='projectMember')

    #no auth
    resp = client.delete(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(new_user_id),headers=headers)
    assert resp.status_code == 401
    assert resp.json()['details'] == "Access token not provided or user not recognized."
    check_project_user(project_data['projectName'], new_user_id, role='projectMember')

    # deleting non existing user
    second_user_id = initial_test_users['SanketMASTUser2']['test_user_id']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.delete(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(second_user_id),headers=headers_auth)
    assert resp.status_code == 404
    assert resp.json()['details'] == "User-project pair not found"

    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(second_user_id),headers=headers_auth)
    assert resp.json()['message'] == "User added to project successfully"
    check_project_user(project_data['projectName'], second_user_id, role='projectMember')

    #  as non-owner user
    user_id = initial_test_users['SanketMASTUser2']['test_user_id']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.delete(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(user_id),headers=headers_auth)
    assert resp.status_code == 403
    assert resp.json()['error'] == "Permission Denied"
    check_project_user(project_data['projectName'], user_id, role='projectMember')

    # as same user
    user_id = initial_test_users['SanketMASTAdmin']['test_user_id']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.delete(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(user_id),headers=headers_auth)
    assert resp.status_code == 403
    assert resp.json()['details'] == "A user cannot remove oneself from a project."
    check_project_user(project_data['projectName'], user_id, role='projectOwner')

    # as project owner - Positive test
    user_id = initial_test_users['SanketMASTUser2']['test_user_id']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp =client.delete(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(user_id),headers=headers_auth)
    assert resp.status_code == 201
    assert "successfull" in resp.json()['message']

    # Check get project to ensure deleted user is not present
    get_project_response = client.get(UNIT_URL+'?project_id='+str(new_project['projectId']),headers=headers_auth)
    found_user = False

    for user in get_project_response.json()[0]['users']:
        if user['userId'] == user_id:
            found_user = True
            assert user['userRole'] is 'projectMember'
            assert user['active'] is True
            assert user['metaData'] is None
    assert not found_user

def test_restore_user():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deleting project user
    project_data = {
        "projectName": "Test project 1",
        "sourceLanguageCode": "hi",
        "targetLanguageCode": "ml"
    }
    resp = check_post(project_data, auth_token=initial_test_users['SanketMASTAdmin']['token'])
    assert resp.json()['message'] == "Project created successfully"
    #  Get project Id
    project_id = resp.json()['data']['projectId']
    new_project = resp.json()['data']
    user_id = initial_test_users['SanketMASTUser']['test_user_id']

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(user_id),headers=headers_auth)
    assert resp.json()['message'] == "User added to project successfully"

    # fetch this project and check for new user
    check_project_user(project_data['projectName'], user_id, role='projectMember')
    
    #Delete
    # user_id = initial_test_users['SanketMASTUser']['test_user_id']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    delete_resp = client.delete(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(user_id),headers=headers_auth)
    assert delete_resp.status_code == 201
    assert "successfull" in delete_resp.json()['message']

    #Ensure deleted user is not present
    get_project_response = client.get(UNIT_URL+'?project_id='+str(new_project['projectId']),headers=headers_auth)
    found_user = False

    for user in get_project_response.json()[0]['users']:
        if user['userId'] == user_id:
            found_user = True
            assert user['userRole'] is 'projectMember'
            assert user['active'] is True
            assert user['metaData'] is None
    assert not found_user



    deleteditem_id = delete_resp.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring data
    #Restore user without authentication - Negative Test
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore project user with other API user,VachanAdmin,SanketMASTAdmin,SanketMASTUser,VachanUser,BcsDev and APIUSer2 - Negative Test
    for user in ['APIUser','VachanAdmin','SanketMASTAdmin','SanketMASTUser','VachanUser','BcsDev','APIUser2','VachanContentAdmin','VachanContentViewer']:
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users[user]['token']
        response = client.put(RESTORE_URL, headers=headers_auth, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Restore Project User with Super Admin - Positive Test
     # Login as Super Admin
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth['Authorization'] = "Bearer"+" "+test_user_token

    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleteditem_id} restored successfully"

    #Ensure presence of restored user
    check_project_user(project_data['projectName'], user_id, role='projectMember')

    #restore with missing data - Negative Test
    data = {}
    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #Restore with invalid item id - Negative Test
    data = {"itemId":9999}
    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    logout_user(test_user_token)

def test_bugfix_split_n_merged_verse():
    '''BUg fix for https://github.com/Bridgeconn/vachan-api/issues/543'''
    post_data = {
    "projectName": "Test project usfm upload",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project_id = response.json()['data']['projectId']

    prj_book_data = {
      "uploadedUSFMs": [
          "\\id REV\n\\c 1\n\\p\n\\v 1 some text\n\\v 2-10 merged text\n\\v 11a split text\n\\v 11b rest"
      ]
    }
    prj_update_resp = client.put(UNIT_URL+'?project_id='+str(project_id), json=prj_book_data, headers=headers_auth)
    assert prj_update_resp.status_code == 201
    resp_obj = prj_update_resp.json()
    assert resp_obj['message'] == 'Project updated successfully'

    sentences_resp = client.get(f"{SENTENCE_URL}?project_id={project_id}", headers=headers_auth)
    assert sentences_resp.status_code == 200
    sentences = sentences_resp.json()
    assert len(sentences) == 3
    assert sentences[0]['sentenceId'] == 67001001
    assert sentences[0]['surrogateId'] == 'rev 1:1'
    assert sentences[0]["sentence"] == 'some text'
    assert sentences[1]['sentenceId'] == 67001002
    assert sentences[1]['surrogateId'] == 'rev 1:2-10'
    assert sentences[1]["sentence"] == 'merged text'
    assert sentences[2]['sentenceId'] == 67001011
    assert sentences[2]['surrogateId'] == 'rev 1:11a-b'
    assert sentences[2]["sentence"] == 'split text rest'

def test_post_put_app_compatibility():
    '''Positive test to check app compatibility
    * Only SanketMAST app can access translation APIs'''
    headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "app":"SanketMAST"
            }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']

    # create with minimum data
    post_data = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
    }

    #Creating new project with out adding compatibleWith field - Positive Test
    #app value in the header will be auto assigned as compatibleWith field
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    response.json()['data']['compatibleWith'] = ["SanketMAST"]
    assert_positive_get( response.json()['data'])

    # Creating new project with compatible app which is not passed as a list - Negative Test
    post_data['compatibleWith'] = "SanketMAST"
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert_input_validation_error(response)

    # Creating new project with compatible app passed as a list - Positive Test
    post_data["projectName"] = "Test Project 2"
    post_data["compatibleWith"] = ["SanketMAST","Autographa"]
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    new_project = response.json()['data']
    assert_positive_get(new_project)

    # check if all defaults are coming
    assert new_project['metaData']["useDataForLearning"]
    assert isinstance(new_project['metaData']['books'], list)
    assert len(new_project['metaData']['books']) == 0
    assert new_project['active']

    # update data with compatible app not passed as a list - negative test
    put_data = {
    "uploadedUSFMs":[bible_books['mat']]
    }
    put_data["compatibleWith"] =  "SanketMAST"
    response2 = client.put(UNIT_URL+'?project_id='+str(new_project['projectId']),\
         headers=headers_auth, json=put_data)
    assert_input_validation_error(response2)

    # update data with compatible app passed as a list - positive test
    put_data = {
    "uploadedUSFMs":[bible_books['mat']]
    }
    put_data["compatibleWith"] =  ["Autographa","VachanAdmin"]
    response2 = client.put(UNIT_URL+'?project_id='+str(new_project['projectId']), \
        headers=headers_auth, json=put_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"
    updated_project = response2.json()['data']
    assert_positive_get(updated_project)

    assert new_project['projectId'] == updated_project['projectId']
    assert new_project['projectName'] == updated_project['projectName']
    assert updated_project['metaData']['books'] == ['mat']

    # update project with incompatible app - Negative Test
    put_data = {
    "uploadedUSFMs":[bible_books['mrk']],
    "compatibleWith": ["VachanAdmin"]
    }
    response2 = client.put(UNIT_URL+'?project_id='+str(new_project['projectId']), \
        headers=headers_auth, json=put_data)
    assert response2.status_code == 403
    assert response2.json()['details'] == "Incompatible app"

def test_delete_with_compatible_app():
    '''Test to delete project based on app compatibiblty'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    data_1 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "compatibleWith": ["SanketMAST"]
    }
    data_2 = {
    "projectName": "Test project 2",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "compatibleWith": ["SanketMAST","Autographa"]
    }
    # creating two projects
    response1 = client.post(UNIT_URL, headers=headers_auth, json=data_1)
    project1 = response1.json()['data']
    project_id_1 = project1['projectId']
    response2 = client.post(UNIT_URL, headers=headers_auth, json=data_2)
    project2 = response2.json()['data']
    project_id_2 = project2['projectId']

    # delete project1 with compatible app - Positive Test
    resp = client.delete(UNIT_URL+'?project_id='+str(project_id_1),headers=headers_auth)
    assert resp.status_code == 201
    assert resp.json()['message'] == f"Project with identity {project_id_1} deleted successfully"
    # update compatibility of project 2
    put_data = {
    "compatibleWith": ["VachanAdmin"]
    }
    response2 = client.put(UNIT_URL+'?project_id='+str(project_id_2), \
        headers=headers_auth, json=put_data)

    # delete project with incompatible app - Negative Test
    resp = client.delete(UNIT_URL+'?project_id='+str(project_id_2),headers=headers_auth)
    assert resp.status_code == 403
    assert resp.json()['details'] == "Incompatible app"

def test_get_filter_with_app_compatibility():
    '''Test  to filter with app compatibility'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    data_1 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "compatibleWith": ["SanketMAST"]
    }
    data_2 = {
    "projectName": "Test project 2",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
    }
    data_3 = {
    "projectName": "Test project 3",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "compatibleWith": ["SanketMAST","Autographa"]
    }
    # Creating new project with compatible app - Positive Test
    response1 = client.post(UNIT_URL, headers=headers_auth, json=data_1)
    # Creating new project without mentioning compatible_with field - Positive test
    response2 = client.post(UNIT_URL, headers=headers_auth, json=data_2)
    # Creating new project with multiple items in compatible_with field - Positive test
    response3 = client.post(UNIT_URL, headers=headers_auth, json=data_3)
    
    #filtering with single app - passing app not as a list - Negative test
    app = "SanketMAST"
    params = []
    for item in app:
        params.append(("compatible_with", item))
    get_resp = client.get(UNIT_URL ,params=params,headers=headers_auth)
    assert_input_validation_error(get_resp)
    
    # filtering with single app - positive test
    app = ["SanketMAST"]
    params = []
    for item in app:
        params.append(("compatible_with", item))
    get_resp = client.get(UNIT_URL ,params=params,headers=headers_auth)
    for item in get_resp.json():
        assert_positive_get(item)
    assert len(get_resp.json()) == 3
    assert"SanketMAST" in  get_resp.json()[0]['compatibleWith']
    assert"SanketMAST" in  get_resp.json()[1]['compatibleWith']
    assert"SanketMAST" in  get_resp.json()[2]['compatibleWith']

    #filtering with multiple apps - positive test
    app_list = [schema_auth.App.SMAST.value, schema_auth.App.AG.value]
    params = []
    for app in app_list:
        params.append(("compatible_with", app))
    get_resp2 = client.get(UNIT_URL, params=params, headers=headers_auth)
    for item in get_resp2.json():
        assert_positive_get(item)
    assert len(get_resp2.json()) == 1
    for item in get_resp2.json():
        assert_positive_get(item)
        assert "SanketMAST" in item['compatibleWith']
        assert "Autographa" in item['compatibleWith']

    #filtering with app not in the list
    get_resp = client.get(UNIT_URL + "?compatible_with=VachanAdmin",headers=headers_auth)
    assert_not_available_content(get_resp)
