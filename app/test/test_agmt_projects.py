'''Test cases for Agmt projects related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_bibles import check_post as add_bible, gospel_books_data
from .test_sources import check_post as add_source
from .test_versions import check_post as add_version
from .conftest import initial_test_users
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER

UNIT_URL = '/v2/translation/projects' 
USER_URL = '/v2/translation/project/user'
headers = {"contentType": "application/json", "accept": "application/json", "app":"Autographa"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "app":"Autographa"
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
                "app":"Autographa"}
    if not auth_token:
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    else:
        headers_auth['Authorization'] = "Bearer"+" "+auth_token
    response = client.post(UNIT_URL, headers=headers_auth, json=data)
    return response

def test_default_post_put_get():
    '''Positive test to create a project'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
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
    "projectId":new_project['projectId'],
    "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    response2 = client.put(UNIT_URL, headers=headers_auth, json=put_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"
    updated_project = response2.json()['data']
    assert_positive_get(updated_project)

    assert new_project['projectId'] == updated_project['projectId']
    assert new_project['projectName'] == updated_project['projectName']
    assert updated_project['metaData']['books'] == ['mat', 'mrk']

    #add bible , create source with open-access

    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for bibles",
    }
    add_version(version_data)
    source_data = {
        "contentType": "bible",
        "language": "gu",
        "version": "TTT",
        "year": 3030,
        "versionTag": 1,
        "accessPermissions": [
            "content","open-access"
        ],
    }
    source = add_source(source_data)
    table_name = source.json()['data']['sourceName']

    #add books with vachan admin
    headers_auth_content = {"contentType": "application/json",
                "accept": "application/json"
            }
    headers_auth_content['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    resp = client.post('/v2/bibles/'+table_name+'/books', headers=headers_auth_content, json=gospel_books_data)

    # resp, source_name = add_bible(gospel_books_data)
    assert resp.status_code == 201

    put_data = {
        "projectId":new_project['projectId'],
        "selectedBooks": {
            "bible": table_name,
            "books": ["luk", "jhn"]
          }
    }
    response2b = client.put(UNIT_URL, headers=headers_auth, json=put_data)
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
        "projectId":new_project['projectId'],
        "projectName":"New name for old project"}
    response4 = client.put(UNIT_URL, headers=headers_auth, json=put_data)
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
    data = {"projectId": new_project['projectId'],
    "active": "delete"}
    resp = client.put(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(resp)

    data = {"projectId": new_project['projectId'],
    "uploadedUSFMs": "mat"}
    resp = client.put(UNIT_URL, headers=headers_auth, json=data)
    assert_input_validation_error(resp)

    data = {"projectId": new_project['projectId'],
    "uploadedUSFMs": ["The contents of matthew in text"]}
    resp = client.put(UNIT_URL, headers=headers_auth, json=data)
    assert resp.status_code == 415
    assert resp.json()['error'] == "Not the Required Type"

def check_project_user(project_name, user_id, role=None, status=None, metadata = None):
    '''Make sure the user is in project and if specified, check for other values'''
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
    new_user_id = initial_test_users['AgUser']['test_user_id']
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
    new_user_id = initial_test_users['AgUser']['test_user_id']

    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert resp.json()['message'] == "User added to project successfully"

    update_data = {
        "project_id": new_project['projectId'],
        "userId": new_user_id
    }

    # change role
    update1 = update_data
    update1['userRole'] = 'projectOwner'
    response1 = client.put(USER_URL, headers=headers_auth, json=update1)
    assert response1.status_code == 201
    assert response1.json()['message'] == "User updated in project successfully"
    check_project_user(project_data['projectName'], new_user_id, role="projectOwner")

    # change status
    update2 = update_data
    update2['active'] = False
    response2 = client.put(USER_URL, headers=headers_auth, json=update2)
    assert response2.status_code == 201
    assert response2.json()['message'] == "User updated in project successfully"
    check_project_user(project_data['projectName'], new_user_id, status=False)

    # add metadata
    meta = {"last_filter": "mat"}
    update3 = update_data
    update3['metaData'] = meta
    response3 = client.put(USER_URL, headers=headers_auth, json=update3)
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
    new_user_id = initial_test_users['AgUser']['test_user_id']

    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert resp.json()['message'] == "User added to project successfully"


    # not the added user
    update_data = {
        "project_id": new_project['projectId'],
        "userId": "not-a-valid-user-11233",
        "active": False
    }
    response = client.put(USER_URL, headers=headers_auth, json=update_data)
    assert response.status_code == 404
    assert response.json()['details'] == "User-project pair not found"

    #non existant project
    update_data = {
        "project_id": new_project['projectId']+1,
        "userId": new_user_id,
        "active": False
    }
    response = client.put(USER_URL, headers=headers_auth, json=update_data)
    assert response.status_code == 404
    assert response.json()['details'] == "User-project pair not found"

    # invalid status
    update_data = {
        "project_id": new_project['projectId']+1,
        "userId": new_user_id,
        "active": "Delete"
    }
    response = client.put(USER_URL, headers=headers_auth, json=update_data)
    assert_input_validation_error(response)

    # invalid metadata
    update_data = {
        "project_id": new_project['projectId']+1,
        "userId": new_user_id,
        "metaData": "A normal string intead of json"
    }
    response = client.put(USER_URL, headers=headers_auth, json=update_data)
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
        put_obj['projectId'] = project_id
        response = client.put(UNIT_URL, headers=headers_auth, json=put_obj)
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
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project1_id = response.json()['data']['projectId']

    #create from app other than Autographa
    post_data["projectName"] = "Test project 2"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
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
    headers_auth["app"] = "Autographa"
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
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
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
    "projectId":project6_id,
    "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    #update with Owner of project
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    response2 = client.put(UNIT_URL, headers=headers_auth, json=put_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"
    updated_project = response2.json()['data']
    assert updated_project['metaData']['books'] == ['mat', 'mrk']

    #aguser project can be updated by super admin and Ag admin
    put_data = {
        "projectId":project6_id,
        "projectName":"New name for old project6"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    response2 = client.put(UNIT_URL, headers=headers_auth, json=put_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"
    assert response2.json()['data']['projectName'] == put_data["projectName"]
    put_data["projectName"] = "New name for project7 by SA"
    headers_auth['Authorization'] = "Bearer"+" "+test_SA_token
    response2 = client.put(UNIT_URL, headers=headers_auth, json=put_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"
    assert response2.json()['data']['projectName'] == put_data["projectName"]

    #update project with not Owner
    put_data["projectId"] = project7_id
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    response2 = client.put(UNIT_URL, headers=headers_auth, json=put_data)
    assert response2.status_code == 403
    assert response2.json()['error'] == 'Permission Denied'

    #project user create
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    new_user_id = initial_test_users['AgUser']['test_user_id']
    #add user from another app than Autographa
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
    headers_auth["app"] = "Autographa"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    response = client.post(USER_URL+'?project_id='+str(project1_id)+
        '&user_id='+str(new_user_id),headers=headers_auth)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'
    #add from Autograpaha by allowed user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
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
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    update_data = {
        "project_id": project1_id,
        "userId": new_user_id
    }
    # add metadata
    meta = {"last_filter": "luk"}
    update_data['metaData'] = meta
    response3 = client.put(USER_URL, headers=headers_auth, json=update_data)
    assert response3.status_code == 403
    assert response3.json()['error'] == 'Permission Denied'
    #update with owner
    post_data['projectName'] = 'Test project 1'
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    response3 = client.put(USER_URL, headers=headers_auth, json=update_data)
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
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project1_id = response.json()['data']['projectId']

    post_data["projectName"] = "Test project 2"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project2_id = response.json()['data']['projectId']

    post_data["projectName"] = "Test project 3"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
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
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
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

    #get project from Autographa with not allowed users get empty result
    headers_auth["app"] = "Autographa"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) == 0
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) == 0
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) == 0

    #get all project by SA , AgAdmin, Bcs internal dev
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) >= 3

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) >= 3

    headers_auth['Authorization'] = "Bearer"+" "+ test_SA_token
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) >= 3

    #get project by project owner Aguser only get owner project
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) >= 2

    #create project by SA and add Aguser as member to the project
    post_data["projectName"] = 'Test project 4'
    headers_auth['Authorization'] = "Bearer"+" "+ test_SA_token
    response = client.post(UNIT_URL, headers=headers_auth, json=post_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Project created successfully"
    project4_id = response.json()['data']['projectId']

    new_user_id = initial_test_users['AgUser']['test_user_id']
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
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    response = client.get(UNIT_URL+"?user_id="+new_user_id,headers=headers_auth)
    assert len(response.json()) >= 3
    for proj in response.json():
        assert proj['projectName'] in ["Test project 4","Test project 3","Test project 2"]

   #A new Aguser requesting for all projecrts
    # test_ag_user_data = {
    #     "email": "testaguser@test.com",
    #     "password": "passwordag@1"
    # }
    # response = register(test_ag_user_data, apptype='Autographa')
    # ag_user_id = [response.json()["registered_details"]["id"]]
    # ag_user_token = response.json()["token"]

    #get projects where user have no projects result is []
    headers_auth["app"] = "Autographa"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser2']['token']
    # headers_auth['Authorization'] = "Bearer"+" "+ag_user_token
    response = client.get(UNIT_URL,headers=headers_auth)
    assert len(response.json()) == 0
    # delete_user_identity(ag_user_id)


def test_create_n_update_times():
    '''Test to ensure created time and last updated time are included in project GET response'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
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
        "projectId": project_id,
        "metaData": {"last_filter": "luk"}
    }
    response2 = client.put(UNIT_URL, headers=headers_auth, json=update_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"

    response = client.get(f"{UNIT_URL}?project_name={post_data['projectName']}",headers=headers_auth)
    assert response.json()[0]["createTime"] != response.json()[0]["updateTime"]
 