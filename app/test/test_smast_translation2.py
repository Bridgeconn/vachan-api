'''tests for the translation workflow within SMAST projects continued'''
import json
from . import client
from .conftest import initial_test_users
from . import assert_input_validation_error, assert_not_available_content
from . test_agmt_translation import UNIT_URL, assert_positive_get_sentence
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user

RESTORE_URL = '/v2/admin/restore'
PROJECT_URL = '/v2/text/translate/token-based/projects'
headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "app":"SanketMAST"
            }
headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']

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
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.post(PROJECT_URL, headers=headers_auth, json=project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "sentenceList":source_sentences
    }
    resp = client.put("/v2/text/translate/token-based/projects"+'?project_id='+str(project_id),\
         headers=headers_auth, json=put_data)
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
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data)
    sents = resp.json()
    assert len(sents) == 1
    assert_positive_get_sentence(sents[0])
    assert sents[0]["draft"] == "കാട്"
    assert sents[0]["draftMeta"] == put_data[0]['draftMeta']

    #fetch sentences to make sure
    data_str = json.dumps(put_data)
    resp = client.get(
    "/v2/text/translate/token-based/project/sentences",
    params={
        "project_id": project_id,
        "sentence_id_list": "100",
        "with_draft": "true",
        "data": data_str
    },
    headers=headers_auth
    )
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
                  [ [5,5], [3,4], "confirmed"],
                  [ [5,11], [4,11], "confirmed"],
                  [ [11,11], [11,13], "confirmed"],
                  [ [32,33], [13,16], "confirmed"],
                  [ [33,33], [16,18], "confirmed"],
                  [ [35,38], [18,26], "confirmed"],
                  [ [38,38], [26,43], "untranslated"],
                ]
            }
    ]
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data2)
    sents = resp.json()
    assert_positive_get_sentence(sents[0])
    assert sents[0]["draft"] == "ഒരു കാട്ടില്‍ ഒരു കുറുക്കന്‍ ജീവിച്ചിരുന്നു"
    assert sents[0]["draftMeta"] == put_data2[0]['draftMeta']

    #fetch sentences again
    data_str2 = json.dumps(put_data2)
    resp = client.get(
            "/v2/text/translate/token-based/project/sentences",
            params={
                "project_id": project_id,
                "sentence_id_list": "100",
                "with_draft": "true",
                "data2": data_str2
            },
            headers=headers_auth)
    sents = resp.json()
    assert sents[0]["draft"] == put_data2[0]['draft']
    assert sents[0]["draftMeta"] == put_data2[0]['draftMeta']

def test_draft_update_negative():
    '''Checking effective validations and error messages'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.post(PROJECT_URL, headers=headers_auth, json=project_data)
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
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id+1}",
        headers=headers_auth, json=put_data)
    assert resp.json()['details'] == f"Project with id, {project_id+1}, not present"

    # non existing sentence
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data)
    assert resp.json()['error'] == "Requested Content Not Available"

    # upload source and repeat last action
    put_data_source = {
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.put("/v2/text/translate/token-based/projects"+'?project_id='+str(project_id),\
         headers=headers_auth, json=put_data_source)
    assert resp.json()['message'] == "Project updated successfully"

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data)
    assert resp.json()[0]["draft"] == put_data[0]['draft']

    # incorrect user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser2']['token']
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data)
    assert resp.json()['error'] == "Permission Denied"

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']

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
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
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
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
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
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
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
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data2)
    assert resp.status_code == 422
    assert resp.json()['details'] == "Incorrect metadata:Target segment [0, 10], is improper!"


def test_empty_draft_initalization():
    '''Bugfix test for #452 after the changes in #448'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.post(PROJECT_URL, headers=headers_auth, json=project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.put("/v2/text/translate/token-based/projects"+'?project_id='+str(project_id),\
         headers=headers_auth, json=put_data)
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
    response = client.post('/v2/nlp/gloss?source_language=en&target_language=ml',
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
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.post(PROJECT_URL, headers=headers_auth, json=project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.put("/v2/text/translate/token-based/projects"+'?project_id='+str(project_id),\
         headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    #Get suggestions
    resp = client.put(f"/v2/text/translate/token-based/project/suggestions?project_id={project_id}&sentenceIdList=100",
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
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
        headers=headers_auth, json=json_data)
    assert resp.status_code == 201

def test_space_in_suggested_draft():
    '''BUgfix text for #485, after changes in PR #486'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.post(PROJECT_URL, headers=headers_auth, json=project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.put("/v2/text/translate/token-based/projects"+'?project_id='+str(project_id),\
         headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # Add a gloss to ensure some suggestion in output
    tokens_trans = [
        {"token":"jungle", "translations":["കാട്"]},
        {"token":"far", "translations":["ദൂരെ"]},
        {"token":"fox", "translations":["കുറുക്കന്‍"]}
    ]
    response = client.post('/v2/nlp/gloss?source_language=en&target_language=ml',
        headers=headers_auth, json=tokens_trans)
    assert response.status_code == 201
    assert response.json()['message'] == "Added to glossary"


    #Get suggestions
    resp = client.put(f"/v2/text/translate/token-based/project/suggestions?project_id={project_id}&sentenceIdList=100", 
        headers=headers_auth)
    assert resp.status_code == 201
    resp_obj = resp.json()
    assert resp_obj[0]['draft'] != ""
    assert not resp_obj[0]['draft'].startswith(" ")

    #Get suggestions again
    resp = client.put(f"/v2/text/translate/token-based/project/suggestions?project_id={project_id}&sentenceIdList=100", 
        headers=headers_auth)
    assert resp.status_code == 201
    resp_obj = resp.json()
    assert resp_obj[0]['draft'] != ""
    assert not resp_obj[0]['draft'].startswith(" ")

def test_delete_sentence():
    '''Test the removal of a sentence from project'''

    #Adding Project and sentences into it
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.post(PROJECT_URL, headers=headers_auth, json=project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.put("/v2/text/translate/token-based/projects"+'?project_id='+str(project_id),\
         headers=headers_auth, json=put_data)
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
                "app":"SanketMAST"
            }
    resp = client.delete(f"{UNIT_URL}/sentences?project_id={project_id}&sentence_id={sentence_id1}",
            headers=headers)
    assert resp.status_code == 401
    assert resp.json()['details'] == "Access token not provided or user not recognized."

    #Deleting Sentence with unauthorized users - Negative Test
    for user in ['APIUser','VachanAdmin','VachanUser','BcsDev','SanketMASTUser','VachanContentAdmin','VachanContentViewer']:
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users[user]['token']
        response = client.delete(f"{UNIT_URL}/sentences?project_id={project_id}&sentence_id={sentence_id1}",
                headers=headers_auth)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    # Delete as SanketMASTAdmin - Positive test
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
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
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.post(PROJECT_URL, headers=headers_auth, json=project_data)
    project_id = resp.json()['data']['projectId']

    put_data = {
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.put("/v2/text/translate/token-based/projects"+'?project_id='+str(project_id),\
         headers=headers_auth, json=put_data)
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
                "app":"SanketMAST"
            }
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore project user with other API user,VachanAdmin,SanketMASTAdmin,SanketMASTUser,VachanUser,BcsDev - Negative Test
    for user in ['APIUser','VachanAdmin','SanketMASTAdmin','SanketMASTUser','VachanUser','BcsDev','VachanContentAdmin','VachanContentViewer']:
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

def test_suggestion_when_token_overlaps_confirmed_segment():
    # Testing bug fix https://github.com/Bridgeconn/vachan-api/issues/542
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    resp = client.post(PROJECT_URL, headers=headers_auth, json=project_data)
    project_id = resp.json()['data']['projectId']

    put_data = {
        "sentenceList": [
            {
            "sentenceId": 57001002,
            "surrogateId": "tit 1:2",
            "sentence":"This faith and knowledge make us sure that we have eternal life. God promised that life to us before time began—and God does not lie."
            }
        ]
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    resp = client.put("/v2/text/translate/token-based/projects"+'?project_id='+str(project_id),\
         headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # add a translation for just "not" when it occurs as "doesnot"
    update_draft_url = f"/v2/text/translate/token-based/project/draft?project_id={project_id}"
    data = [{ "draft": "they this",
        "draftMeta": [ [ [ 0, 4 ], [ 9, 9 ], "untranslated" ],
                       [ [ 4, 5 ], [ 9, 9 ], "untranslated" ],
                       [ [ 5, 10 ], [ 9, 9 ], "untranslated" ],
                       [ [ 10, 11 ], [ 9, 9 ], "untranslated" ],
                       [ [ 11, 24 ], [ 9, 9 ], "untranslated" ],
                       [ [ 24, 25 ], [ 9, 9 ], "untranslated" ],
                       [ [ 25, 29 ], [ 9, 9 ], "untranslated" ],
                       [ [ 29, 30 ], [ 9, 9 ], "untranslated" ],
                       [ [ 30, 32 ], [ 9, 9 ], "untranslated" ],
                       [ [ 32, 33 ], [ 9, 9 ], "untranslated" ],
                       [ [ 33, 37 ], [ 9, 9 ], "untranslated" ],
                       [ [ 37, 38 ], [ 9, 9 ], "untranslated" ],
                       [ [ 38, 42 ], [ 9, 9 ], "untranslated" ],
                       [ [ 42, 43 ], [ 9, 9 ], "untranslated" ],
                       [ [ 43, 45 ], [ 9, 9 ], "untranslated" ],
                       [ [ 45, 46 ], [ 9, 9 ], "untranslated" ],
                       [ [ 46, 58 ], [ 9, 9 ], "untranslated" ],
                       [ [ 58, 59 ], [ 9, 9 ], "untranslated" ],
                       [ [ 59, 63 ], [ 9, 9 ], "untranslated" ],
                       [ [ 63, 65 ], [ 9, 9 ], "untranslated" ],
                       [ [ 65, 68 ], [ 9, 9 ], "untranslated" ],
                       [ [ 68, 69 ], [ 9, 9 ], "untranslated" ],
                       [ [ 69, 77 ], [ 9, 9 ], "untranslated" ],
                       [ [ 77, 78 ], [ 9, 9 ], "untranslated" ],
                       [ [ 78, 82 ], [ 9, 9 ], "untranslated" ],
                       [ [ 82, 83 ], [ 9, 9 ], "untranslated" ],
                       [ [ 83, 87 ], [ 9, 9 ], "untranslated" ],
                       [ [ 87, 88 ], [ 9, 9 ], "untranslated" ],
                       [ [ 88, 93 ], [ 9, 9 ], "untranslated" ],
                       [ [ 93, 94 ], [ 9, 9 ], "untranslated" ],
                       [ [ 94, 105 ], [ 9, 9 ], "untranslated" ],
                       [ [ 105, 106 ], [ 9, 9 ], "untranslated" ],
                       [ [ 106, 111 ], [ 9, 9 ], "untranslated" ],
                       [ [ 111, 112 ], [ 9, 9 ], "untranslated" ],
                       [ [ 112, 119 ], [ 9, 9 ], "untranslated" ],
                       [ [ 119, 120 ], [ 9, 9 ], "untranslated" ],
                       [ [ 132, 133 ], [ 9, 9 ], "untranslated" ],
                       [ [ 125, 128 ], [ 5, 9 ], "confirmed" ],
                       [ [ 129, 132 ], [ 0, 4 ], "confirmed" ],
                       [ [ 125, 125 ], [ 4, 5 ], "confirmed" ] ],
        "sentenceId": 57001002 }]
    update_resp = client.put(update_draft_url,
                           json=data,
                             headers={'Authorization': f'bearer {initial_test_users["SanketMASTAdmin"]["token"]}',
                                      'app':"SanketMAST"})
    assert update_resp.status_code == 201


    # Suggestion call 1
    suggest_url =  f"/v2/text/translate/token-based/project/suggestions?project_id={project_id}&sentence_id_list=57001002"
    suggest_resp = client.put(suggest_url, 
                             headers={'Authorization': f"bearer {initial_test_users['SanketMASTAdmin']['token']}",
                                      'app':"SanketMAST"})
    assert suggest_resp.status_code == 201

    # Suggestion call 2
    suggest_url =  f"/v2/text/translate/token-based/project/suggestions?project_id={project_id}&sentence_id_list=57001002"
    suggest_resp = client.put(suggest_url, 
                             headers={'Authorization': f"bearer {initial_test_users['SanketMASTAdmin']['token']}",
                                      'app':"SanketMAST"})
    assert suggest_resp.status_code == 201

def test_draftmeta_validation():
    '''All protions of the draft should have a draftmeta segment
    issue #602'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.post(PROJECT_URL, headers=headers_auth, json=project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "sentenceList":source_sentences
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    resp = client.put("/v2/text/translate/token-based/projects"+'?project_id='+str(project_id),\
         headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    ## Spaces not accounted for
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
    resp = client.put(f"/v2/text/translate/token-based/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data2)
    assert resp.status_code == 422
    assert "error" in resp.json()
    assert resp.json()['error'] == "Unprocessable Data"