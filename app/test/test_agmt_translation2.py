'''tests for the translation workflow within AgMT projects continued'''

from . import client
from .test_agmt_projects import check_post as add_project
from .conftest import initial_test_users
from . test_agmt_translation import UNIT_URL, assert_positive_get_sentence

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
            assert meta[1] == [resp.json()[0]['draft'].index("കാട്"), len("കാട്")]
        elif meta[2] == "untranslated":
            found_untranslated = True
    assert found_jungle_meta
    assert found_untranslated
