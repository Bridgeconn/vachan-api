'''Test cases for Agmt projects related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_bibles import check_post as add_bible, gospel_books_data

UNIT_URL = '/v2/autographa/projects'
USER_URL = '/v2/autographa/project/user'
headers = {"contentType": "application/json", "accept": "application/json"}

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


def check_post(data):
    '''creates a projects'''
    response = client.post(UNIT_URL, headers=headers, json=data)
    return response

def test_default_post_put_get():
    '''Positive test to create a project'''

    resp = client.get(UNIT_URL+'?project_name=Test project 1')
    assert_not_available_content(resp)

    # create with minimum data
    post_data = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
    }
    response = client.post(UNIT_URL, headers=headers, json=post_data)
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
    "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
    }
    response2 = client.put(UNIT_URL, headers=headers, json=put_data)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Project updated successfully"
    updated_project = response2.json()['data']
    assert_positive_get(updated_project)

    assert new_project['projectId'] == updated_project['projectId']
    assert new_project['projectName'] == updated_project['projectName']
    assert updated_project['metaData']['books'] == ['mat', 'mrk']

    resp, source_name = add_bible(gospel_books_data)
    assert resp.status_code == 201

    put_data = {
        "projectId":new_project['projectId'],
        "selectedBooks": {
            "bible": source_name,
            "books": ["luk", "jhn" ]
          }
    }
    response2b = client.put(UNIT_URL, headers=headers, json=put_data)
    assert response2b.status_code == 201
    assert response2b.json()['message'] == "Project updated successfully"
    updated_project = response2b.json()['data']
    assert_positive_get(updated_project)
    assert updated_project['metaData']['books'] == ['mat', 'mrk', 'luk', 'jhn']

    # fetch projects
    response3 = client.get(UNIT_URL)
    assert len(response3.json()) >= 1
    fetched_project = response3.json()[-1]
    assert_positive_get(fetched_project)

    assert fetched_project['projectName'] == post_data['projectName']
    assert fetched_project['sourceLanguage']['code'] == post_data['sourceLanguageCode']
    assert fetched_project['targetLanguage']['code'] == post_data['targetLanguageCode']
    assert fetched_project['metaData']['books'] == ['mat', 'mrk', 'luk', 'jhn']

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
    response = client.post(UNIT_URL, headers=headers, json=post_data)
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
    resp = client.post(UNIT_URL, headers=headers, json=post_data)
    assert resp.status_code == 201
    post_data = {
      "projectName": "Test Project 4",
      "sourceLanguageCode": "hi",
      "targetLanguageCode": "ml"
    }
    resp = client.post(UNIT_URL, headers=headers, json=post_data)
    assert resp.status_code == 201
    check_default_get(UNIT_URL, assert_positive_get)


def test_post_invalid():
    '''test input validation for project create'''
    # Missing mandatory content
    data1 = {
    "projectName": "Test project 1",
    "targetLanguageCode": "ml"
    }
    res1 = client.post(UNIT_URL, headers=headers, json=data1)
    assert_input_validation_error(res1)

    data2 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    }
    res2 = client.post(UNIT_URL, headers=headers, json=data2)
    assert_input_validation_error(res2)

    data3 = {
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
    }
    res3 = client.post(UNIT_URL, headers=headers, json=data3)
    assert_input_validation_error(res3)

    # incorrect data in fields
    data1 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "2hindi",
    "targetLanguageCode": "ml"
    }
    res1 = client.post(UNIT_URL, headers=headers, json=data1)
    assert_input_validation_error(res1)

    data2 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "useDataForLearning": "use"
    }
    res2 = client.post(UNIT_URL, headers=headers, json=data2)
    assert_input_validation_error(res2)

    data3 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "stopwords": ["a", "mromal", "list"]
    }
    res3 = client.post(UNIT_URL, headers=headers, json=data3)
    assert_input_validation_error(res3)

    data4 = {
    "projectName": "Test project 1",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml",
    "punctuations": "+_*())^%$#<>?:'"
    }
    res4 = client.post(UNIT_URL, headers=headers, json=data4)
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
    resp = client.put(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(resp)

    # incorrect values in fields
    data = {"projectId": new_project['projectId'],
    "active": "delete"}
    resp = client.put(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(resp)

    data = {"projectId": new_project['projectId'],
    "uploadedBooks": "mat"}
    resp = client.put(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(resp)

    data = {"projectId": new_project['projectId'],
    "uploadedBooks": ["The contents of matthew in text"]}
    resp = client.put(UNIT_URL, headers=headers, json=data)
    assert resp.status_code == 415
    assert resp.json()['error'] == "Not the Required Type"

def check_project_user(project_name, user_id, role=None, status=None, metadata = None):
    '''Make sure the user is in project and if specified, check for other values'''
    response = client.get(UNIT_URL+'?project_name='+project_name)
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
        if user['userRole'] == "owner" :
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

    new_user_id = 5555
    response = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        ';user_id='+str(new_user_id))
    assert response.status_code == 201
    assert response.json()['message'] == "User added to project successfully"
    data = response.json()['data']
    assert data["project_id"] == new_project['projectId'] 
    assert data["userId"] == new_user_id 
    assert data["userRole"] == "member" 
    assert data['active']

    # fetch this project and check for new user
    check_project_user(project_data['projectName'], new_user_id, role='member')


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
    resp = client.post(USER_URL+'?user_id=11111')
    assert_input_validation_error(resp)

    # No User
    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId']))
    assert_input_validation_error(resp)

    # Invalid project
    resp = client.post(USER_URL+'?project_id='+str(new_project['projectName'])+
        ';user_id=111111')
    assert_input_validation_error(resp)

    # Invalid user
    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        ';user_id=some_name')
    assert_input_validation_error(resp)


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
    new_user_id = 7777

    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        ';user_id='+str(new_user_id))
    assert resp.json()['message'] == "User added to project successfully"

    update_data = {
        "project_id": new_project['projectId'],
        "userId": new_user_id
    }

    # change role
    update1 = update_data
    update1['userRole'] = 'owner'
    response1 = client.put(USER_URL, headers=headers, json=update1)
    assert response1.status_code == 201
    assert response1.json()['message'] == "User updated in project successfully"
    check_project_user(project_data['projectName'], new_user_id, role="owner")

    # change status
    update2 = update_data
    update2['active'] = False
    response2 = client.put(USER_URL, headers=headers, json=update2)
    assert response2.status_code == 201
    assert response2.json()['message'] == "User updated in project successfully"
    check_project_user(project_data['projectName'], new_user_id, status=False)

    # add metadata
    meta = {"last_filter": "mat"}
    update3 = update_data
    update3['metaData'] = meta
    response3 = client.put(USER_URL, headers=headers, json=update3)
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
    new_user_id = 8888

    resp = client.post(USER_URL+'?project_id='+str(new_project['projectId'])+
        ';user_id='+str(new_user_id))
    assert resp.json()['message'] == "User added to project successfully"


    # not the added user
    update_data = {
        "project_id": new_project['projectId'],
        "userId": new_user_id+1,
        "active": False
    }
    response = client.put(USER_URL, headers=headers, json=update_data)
    assert response.status_code == 404
    assert response.json()['details'] == "User-project pair not found"

    #non existant project
    update_data = {
        "project_id": new_project['projectId']+1,
        "userId": new_user_id,
        "active": False
    }
    response = client.put(USER_URL, headers=headers, json=update_data)
    assert response.status_code == 404
    assert response.json()['details'] == "User-project pair not found"

    # invalid status
    update_data = {
        "project_id": new_project['projectId']+1,
        "userId": new_user_id,
        "active": "Delete"
    }
    response = client.put(USER_URL, headers=headers, json=update_data)
    assert_input_validation_error(response)

    # invalid metadata
    update_data = {
        "project_id": new_project['projectId']+1,
        "userId": new_user_id,
        "metaData": "A normal string intead of json"
    }
    response = client.put(USER_URL, headers=headers, json=update_data)
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

    get_response1 = client.get(UNIT_URL)
    assert len(get_response1.json()) >= len(data)


    # positive PUT
    for item in delete_data:
        # find the project id
        resp = client.get(UNIT_URL+"?project_name="+item['project_name'])
        assert resp.status_code == 200
        project_id = resp.json()[0]['projectId']

        put_obj = {"active": False}
        put_obj['projectId'] = project_id
        response = client.put(UNIT_URL, headers=headers, json=put_obj)
        print(response.json())
        assert response.status_code == 201
        assert response.json()['message'] == 'Project updated successfully'
        assert not response.json()['data']['active']

    get_response2 = client.get(UNIT_URL)
    assert len(get_response2.json()) == len(get_response1.json()) - len(delete_data)

    get_response3 = client.get(UNIT_URL+'?active=false')
    assert len(get_response3.json()) >= len(delete_data)
