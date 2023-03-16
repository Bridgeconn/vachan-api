'''tests for the translation workflow within AgMT projects continued'''

from . import client
from .test_agmt_projects import check_post as add_project
from .conftest import initial_test_users
from . import assert_input_validation_error, assert_not_available_content
from . test_agmt_translation import UNIT_URL, assert_positive_get_sentence
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user

RESTORE_URL = '/v2/restore'
headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "app":"Autographa"
            }
headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']

project_data = {
    "projectName": "Test agmt draft",
    "sourceLanguageCode": "en",
    "targetLanguageCode": "ml"
}

source_sentences = [
    {"sentenceId": 100,
     "sentence": "In a jungle far away there lived a fox"},
    {"sentenceId": 101,
     "sentence": "The fox was friends with a tiger."},
    {"sentenceId": 102,
     "sentence": "They used to play together."},
    {"sentenceId": 103,
     "sentence": "One day the fox wished he had tiger's striped coat."},
    {"sentenceId": 104,
     "sentence": "The good friend tiger lent it to him."},
    {"sentenceId": 105,
     "sentence": "Tharjima illatha thettu vaakkukal mathram."},
    {"sentenceId": 106,
     "sentence": "Oru jungle allathe mattellam tharjima illatha thettu vaakkukal mathram."}     
]

def test_draft_update_positive():
    '''Positive test for updating draft and draftMeta(Alignment) in a project'''
    resp = add_project(project_data, auth_token=initial_test_users['AgUser']['token'])
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.put("/v2/autographa/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    resp = client.get(f"{UNIT_URL}/sentences?project_id={project_id}", headers=headers_auth)
    for sent in resp.json():
        assert_positive_get_sentence(sent)

    # translate just one word
    put_data = [
            {"sentenceId":100,
             "draft": "കാട്",
             "draftMeta":[
                  [ [5,11], [0,4], "confirmed"]
                ]
            }
    ]
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data)
    sents = resp.json()
    assert len(sents) == 1
    assert_positive_get_sentence(sents[0])
    assert sents[0]["draft"] == "കാട്"
    assert sents[0]["draftMeta"] == put_data[0]['draftMeta']

    #fetch sentences to make sure
    resp = client.get("/v2/autographa/project/sentences?"+\
        f"project_id={project_id}&sentence_id_list=100&with_draft=True",
        headers=headers_auth, json=put_data)
    sents = resp.json()
    print(sents)
    assert sents[0]["draft"] == "കാട്"
    assert sents[0]["draftMeta"] == put_data[0]['draftMeta']

    # edit the existing draft
    put_data2 = [
            {"sentenceId":100,
             "draft": "ഒരു കാട്ടില്‍ ഒരു കുറുക്കന്‍ ജീവിച്ചിരുന്നു",
             "draftMeta":[
                  [ [3,4], [0,3], "confirmed"],
                  [ [5,11], [4,11], "confirmed"],
                  [ [32,33], [13,16], "confirmed"],
                  [ [35,38], [18,26], "confirmed"]
                ]
            }
    ]
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data2)
    sents = resp.json()
    assert_positive_get_sentence(sents[0])
    assert sents[0]["draft"] == "ഒരു കാട്ടില്‍ ഒരു കുറുക്കന്‍ ജീവിച്ചിരുന്നു"
    assert sents[0]["draftMeta"] == put_data2[0]['draftMeta']

    #fetch sentences again
    resp = client.get("/v2/autographa/project/sentences?"+\
        f"project_id={project_id}&sentence_id_list=100&with_draft=True",
        headers=headers_auth, json=put_data2)
    sents = resp.json()
    assert sents[0]["draft"] == put_data2[0]['draft']
    assert sents[0]["draftMeta"] == put_data2[0]['draftMeta']

def test_draft_update_negative():
    '''Checking effective validations and error messages'''
    resp = add_project(project_data, auth_token=initial_test_users['AgUser']['token'])
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # incorrect project id
    put_data = [
            {"sentenceId":100,
             "draft": "കാട്",
             "draftMeta":[
                  [ [5,11], [0,4], "confirmed"]
                ]
            }
    ]
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id+1}",
        headers=headers_auth, json=put_data)
    assert resp.json()['error'] == "Requested Content Not Available"

    # non existing sentence
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data)
    assert resp.json()['error'] == "Requested Content Not Available"

    # upload source and repeat last action
    put_data_source = {
        "projectId": project_id,
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.put("/v2/autographa/projects", headers=headers_auth, json=put_data_source)
    assert resp.json()['message'] == "Project updated successfully"

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data)
    assert resp.json()[0]["draft"] == put_data[0]['draft']

    # incorrect user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser2']['token']
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data)
    assert resp.json()['error'] == "Permission Denied"

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']

    # incorrect payloads
    put_data2 = [
            {
             # "sentenceId":100, no sentenceId
             "draft": "കാട്",
             "draftMeta":[
                  [ [5,11], [0,4], "confirmed"]
                ]
            }
    ]
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data2)
    assert resp.status_code == 422

    put_data2 = [
            {
             "sentenceId":100, 
             # "draft": "കാട്", no draft
             "draftMeta":[
                  [ [5,11], [0,4], "confirmed"]
                ]
            }
    ]
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data2)
    assert resp.status_code == 422

    put_data2 = [
            {
             "sentenceId":100, 
             "draft": "കാട്",
             # "draftMeta":[  no draft
             #      [ [5,11], [0,4], "confirmed"]
             #    ]
            }
    ]
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data2)
    assert resp.status_code == 422

    # incorrect index of target segment
    put_data2 = [
            {
             "sentenceId":100, 
             "draft": "കാട്",
             "draftMeta":[  
                  [ [5,11], [0,10], "confirmed"]
                ]
            }
    ]
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data2)
    assert resp.status_code == 422
    assert resp.json()['details'] == "Incorrect metadata:Target segment (0, 10), is improper!"


def test_empty_draft_initalization():
    '''Bugfix test for #452 after the changes in #448'''
    resp = add_project(project_data, auth_token=initial_test_users['AgUser']['token'])
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.put("/v2/autographa/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # Ensure draft is set to ""
    resp = client.get(f"{UNIT_URL}/sentences?project_id={project_id}&with_draft=True",
        headers=headers_auth)
    for sent in resp.json():
        assert_positive_get_sentence(sent)
        assert sent["draft"] == ""

    #Ensure draft if still empty when there is no suggestion
    resp = client.put(f"{UNIT_URL}/suggestions?project_id={project_id}&sentence_id_list={105}",
        headers=headers_auth)
    assert resp.status_code == 201
    assert resp.json()[0]['draft'] == ""

    # Add a gloss to make sure there will be suggestions
    tokens_trans = [
        {"token":"jungle", "translations":["കാട്"]}
    ]
    response = client.post('/v2/nlp/learn/gloss?source_language=en&target_language=ml',
        headers=headers_auth, json=tokens_trans)
    assert response.status_code == 201
    assert response.json()['message'] == "Added to glossary"

    resp = client.put(f"{UNIT_URL}/suggestions?project_id={project_id}&sentence_id_list=100"+\
        "&sentence_id_list=106",
        headers=headers_auth)
    assert resp.status_code == 201
    assert resp.json()[1]['draft'] == "കാട്" # only one suggestion
    assert "കാട്" in resp.json()[0]['draft'] # at least one suggestion
    found_jungle_meta = False
    found_untranslated = False
    for meta in resp.json()[0]['draftMeta']:
        if meta[0] == [5,11] and meta[2] == "suggestion":
            found_jungle_meta = True
            print("draft:", resp.json()[0]['draft'])
            print("draft.index('കാട്'')",resp.json()[0]['draft'].index("കാട്"))
            trans_index = resp.json()[0]['draft'].index("കാട്")
            assert meta[1][0] == trans_index
        elif meta[2] == "untranslated":
            found_untranslated = True
    assert found_jungle_meta
    assert found_untranslated

def test_draft_meta_validation():
    '''Bugfix test for #479 after the changes in PR #481'''
    resp = add_project(project_data, auth_token=initial_test_users['AgUser']['token'])
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.put("/v2/autographa/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    #Get suggestions
    resp = client.put(f"/v2/autographa/project/suggestions?project_id={project_id}&sentenceIdList=100", 
        headers=headers_auth)
    assert resp.status_code == 201
    resp_draft_meta = resp.json()[0]['draftMeta']
    print("draftMeta:", resp_draft_meta)
    empty_seg = False
    for seg in resp_draft_meta:
        if seg[0][0] == seg[0][1] or seg[1][0] == seg[1][1]:
            empty_seg = True
            break
    # assert empty_seg
    
    # PUT the draft meta back to server
    json_data = [{
        "sentenceId":100,
        "draft":resp.json()[0]['draft'],
        "draftMeta":resp_draft_meta
    }]
    resp = client.put(f"/v2/autographa/project/draft?project_id={project_id}",
        headers=headers_auth, json=json_data)
    assert resp.status_code == 201

def test_space_in_suggested_draft():
    '''BUgfix text for #485, after changes in PR #486'''
    resp = add_project(project_data, auth_token=initial_test_users['AgUser']['token'])
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.put("/v2/autographa/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # Add a gloss to ensure some suggestion in output
    tokens_trans = [
        {"token":"jungle", "translations":["കാട്"]},
        {"token":"far", "translations":["ദൂരെ"]},
        {"token":"fox", "translations":["കുറുക്കന്‍"]}
    ]
    response = client.post('/v2/nlp/learn/gloss?source_language=en&target_language=ml',
        headers=headers_auth, json=tokens_trans)
    assert response.status_code == 201
    assert response.json()['message'] == "Added to glossary"


    #Get suggestions
    resp = client.put(f"/v2/autographa/project/suggestions?project_id={project_id}&sentenceIdList=100", 
        headers=headers_auth)
    assert resp.status_code == 201
    resp_obj = resp.json()
    assert resp_obj[0]['draft'] != ""
    assert not resp_obj[0]['draft'].startswith(" ")

    #Get suggestions again
    resp = client.put(f"/v2/autographa/project/suggestions?project_id={project_id}&sentenceIdList=100", 
        headers=headers_auth)
    assert resp.status_code == 201
    resp_obj = resp.json()
    assert resp_obj[0]['draft'] != ""
    assert not resp_obj[0]['draft'].startswith(" ")

def test_delete_sentence():
    '''Test the removal of a sentence from project'''

    #Adding Project and sentences into it
    resp = add_project(project_data, auth_token=initial_test_users['AgUser']['token'])
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.put("/v2/autographa/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # Check sentences are added
    resp = client.get(f"{UNIT_URL}/sentences?project_id={project_id}", headers=headers_auth)
    sentence_id1 = resp.json()[0]['sentenceId']
    sentence_id2 = resp.json()[1]['sentenceId']
    for sent in resp.json():
        assert_positive_get_sentence(sent)


    #deleting sentence with no auth
    headers = {"contentType": "application/json",
                "accept": "application/json",
                "app":"Autographa"
            }
    resp = client.delete(f"{UNIT_URL}/sentences?project_id={project_id}&sentence_id={sentence_id1}",
            headers=headers)
    assert resp.status_code == 401
    assert resp.json()['details'] == "Access token not provided or user not recognized."

    #Deleting Sentence with unauthorized users - Negative Test
    for user in ['APIUser','VachanAdmin','VachanUser','BcsDev','AgUser']:
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users[user]['token']
        response = client.delete(f"{UNIT_URL}/sentences?project_id={project_id}&sentence_id={sentence_id1}",
                headers=headers_auth)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    # Delete as AgAdmin - Positive test
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    response = client.delete(f"{UNIT_URL}/sentences?project_id={project_id}&sentence_id={sentence_id1}",
            headers=headers_auth)
    assert response.status_code == 201
    assert "successfull" in response.json()['message']

    # Check get sentence to ensure deleted sentence is not present
    get_response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&sentence_id_list="+str(sentence_id1),headers=headers_auth)
    assert_not_available_content(get_response)
   
    #Create and Delete sentence with superadmin - Positive test
    # Login as Super Admin
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth['Authorization'] = "Bearer"+" "+test_user_token

    response = client.delete(f"{UNIT_URL}/sentences?project_id={project_id}&sentence_id={sentence_id2}",
            headers=headers_auth)
    assert response.status_code == 201
    assert "successfull" in response.json()['message']

    # Check get sentence to ensure deleted sentence is not present
    get_response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&sentence_id_list="+str(sentence_id2),headers=headers_auth)
    assert_not_available_content(get_response)

    #Delete not available sentence
    response = client.delete(f"{UNIT_URL}/sentences?project_id={project_id}&sentence_id=9999",
            headers=headers_auth)
    assert response.status_code == 404
    assert "Requested Content Not Available" in response.json()['error']


def test_restore_sentence():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deleting project sentence
    #Adding Project and sentences into it
    resp = add_project(project_data, auth_token=initial_test_users['AgAdmin']['token'])
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    resp = client.put("/v2/autographa/projects", headers=headers_auth, json=put_data)
    delete_resp = client.delete(f"{UNIT_URL}/sentences?project_id={project_id}&sentence_id=100",
            headers=headers_auth)

    #Ensure deleted sentence is not present
    get_response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&sentence_id_list=100",headers=headers_auth)
    assert_not_available_content(get_response)
    
    deleteditem_id = delete_resp.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring data
    #Restore user without authentication - Negative Test
    headers = {"contentType": "application/json",
                "accept": "application/json",
                "app":"Autographa"
            }
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore project user with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev - Negative Test
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev']:
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

     #Ensure deleted sentence is not present
    get_response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&sentence_id_list=100",headers=headers_auth)
    assert get_response.status_code ==200
    assert len(get_response.json())== 1
    for item in get_response.json():
        assert_positive_get_sentence(item)

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
