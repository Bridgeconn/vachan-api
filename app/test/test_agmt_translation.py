'''tests for the translation workflow within AgMT projects'''
import json
import re
from math import ceil, floor
from . import client
from . import assert_input_validation_error, assert_not_available_content
from .test_agmt_projects import bible_books, check_post as add_project
from .conftest import initial_test_users
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER


UNIT_URL = '/v2/translation/project'
headers = {"contentType": "application/json", "accept": "application/json","app":"Autographa"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "app":"Autographa"
            }

project_data = {
    "projectName": "Test agmt workflow",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
}

sample_stopwords = ["के", "की"]

def assert_positive_get_tokens(item):
    '''common tests for a token response object'''
    assert "token" in item
    assert "occurrences" in item
    assert len(item['occurrences']) > 0
    assert "translations" in item
    for trans in item['translations']:
        assert isinstance(item['translations'][trans], (int, float))
    if "metaData" in item and item['metaData'] is not None:
        assert isinstance(item['metaData'], dict)

def assert_positive_get_sentence(item):
    '''common test for senstence object'''
    assert "sentenceId" in item
    assert "sentence" in item
    assert isinstance(item['sentence'], str)
    if "draft" in item:
        assert isinstance(item['draft'], str)
        assert "draftMeta" in item
        assert isinstance(item['draftMeta'], list)

def test_get_tokens():
    '''Positive tests for tokenization process'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # before adding books
    get_response1 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id),headers=headers_auth)
    assert_not_available_content(get_response1)

    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # after adding books
    #without auth
    get_response2 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id), headers=headers)
    assert get_response2.json()['error'] == 'Authentication Error'
    get_response2 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id),headers=headers)
    assert get_response2.status_code == 401
    assert get_response2.json()['error'] == 'Authentication Error'
    #with auth
    get_response2 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id),headers=headers_auth)
    assert get_response2.status_code == 200
    assert isinstance(get_response2.json(), list)
    for item in get_response2.json():
        assert_positive_get_tokens(item)

    # with book filter
    get_response3 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+"&books=mat"
    ,headers=headers_auth)
    assert get_response3.status_code == 200
    assert len(get_response3.json()) < len(get_response2.json())

    get_response4 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+"&books=mrk"
    ,headers=headers_auth)
    assert get_response4.status_code == 200
    all_tokens = [item['token'] for item in get_response3.json() + get_response4.json()]
    assert len(get_response2.json()) == len(set(all_tokens))

    # with range filter
    get_response5 = client.get(UNIT_URL+'/tokens?project_id='+str(project_id)+
        "&sentence_id_range=0&sentence_id_range=10",headers=headers_auth)
    # print(get_response5.json())
    assert_not_available_content(get_response5)

    get_response6 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_range=41000000&sentence_id_range=41999999",headers=headers_auth)
    assert get_response6.status_code ==200
    assert get_response6.json() == get_response3.json()

    # with list filter
    get_response7 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_list=41000000",headers=headers_auth)
    assert_not_available_content(get_response7)

    get_response7 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_list=41001001",headers=headers_auth)
    assert get_response7.status_code == 200
    assert 0 < len(get_response7.json()) < 25

    # translation_memory flag
    get_response8 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&use_translation_memory=true",headers=headers_auth)
    assert get_response8.json() == get_response2.json()

    get_response9 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&use_translation_memory=false",headers=headers_auth)
    assert get_response9.status_code == 200
    assert len(get_response9.json()) > 0

    # include_phrases flag
    get_response10 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_phrases=true",headers=headers_auth)
    assert get_response10.json() == get_response2.json()

    get_response11 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_phrases=false",headers=headers_auth)
    assert get_response11.status_code == 200
    assert len(get_response11.json()) <= len(get_response10.json())
    for item in get_response11.json():
        assert " " not in item['token']

    # include_stopwords flag
    get_response12 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=false",headers=headers_auth)
    assert get_response12.json() == get_response2.json()
    for item in get_response12.json():
        assert item['token'] not in sample_stopwords

    get_response13 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=True&include_phrases=false",headers=headers_auth)
    all_tokens = [item['token'] for item in get_response13.json()]
    assert sample_stopwords[0] in all_tokens


def test_tokenization_invalid():
    '''Negative tests for tokenization'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # non existant project
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id+1),headers=headers_auth)
    assert response.status_code == 404
    assert response.json()['details'] == "Project with id, %s, not found"%(project_id+1)

    #invalid book
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+"&books=mmm"
    ,headers=headers_auth)
    assert response.status_code == 404
    assert response.json()['details'] == 'Book, mmm, not in database'

    # only one value for range
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_range=41000000",headers=headers_auth)
    assert_input_validation_error(response)

    # incorrect value for range
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_range=gen&sentence_id_range=num",headers=headers_auth)
    assert_input_validation_error(response)

    # incorrect value for id
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_list=first",headers=headers_auth)
    assert_input_validation_error(response)

    # incorrect value for flags
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=Few",headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_phrases=10",headers=headers_auth)
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&use_translation_memory=always",headers=headers_auth)
    assert_input_validation_error(response)

def test_save_translation():
    '''Positive tests for PUT tokens method'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }

    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    resp = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=true",headers=headers_auth)
    assert resp.status_code == 200
    all_tokens = resp.json()

    # one occurence
    post_obj_list = [
      {
        "token": all_tokens[0]['token'],
        "occurrences": [all_tokens[0]["occurrences"][0]],
        "translation": "test translation"
      }
    ]
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert response.status_code == 201
    assert response.json()['message'] == 'Token translations saved'
    assert response.json()['data'][0]['draft'].startswith("test translation")
    assert response.json()['data'][0]['draftMeta'][0][2] == "confirmed"
    for segment in response.json()['data'][0]['draftMeta'][1:]:
        assert segment[2] != "confirmed"

    # multiple occurances
    post_obj_list = [
      {
        "token": all_tokens[0]['token'],
        "occurrences": all_tokens[0]["occurrences"],
        "translation": "test translation"
      }
    ]
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert response.status_code == 201
    assert response.json()['message'] == 'Token translations saved'
    for sent in response.json()['data']:
        assert "test translation" in sent['draft']

    #Without auth
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
    json=post_obj_list, headers=headers)
    assert response.json()['error'] == 'Authentication Error'

    # all tokens at once
    post_obj_list = []
    for item in all_tokens:
        obj = {
            "token": item['token'],
            "occurrences": item["occurrences"],
            "translation": "test"
        }
        post_obj_list.append(obj)
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert response.status_code == 201
    for sent in response.json()['data']:
        words = re.findall(r'\w+', sent['draft'])
        for wrd in words:
            assert wrd == 'test'

def test_save_translation_invalid():
    '''Negative tests for PUT tokens method'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    resp = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=true",headers=headers_auth)
    assert resp.status_code == 200
    all_tokens = resp.json()

    # incorrect project id
    obj = {
        "token": all_tokens[0]['token'],
        "occurrences": all_tokens[0]["occurrences"],
        "translation": "sample translation"
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id+1),
        headers=headers_auth, json=[obj])
    assert response.status_code == 404
    assert response.json()['details'] == 'Project with id, %s, not present'%(project_id+1)

    # without token
    obj = {
        "occurrences": all_tokens[0]["occurrences"],
        "translation": "sample translation"
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id+1),
        headers=headers_auth, json=[obj])
    assert_input_validation_error(response)

    # without occurences
    obj = {
        "token": all_tokens[0]['token'],
        "translation": "sample translation"
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id+1),
        headers=headers_auth, json=[obj])
    assert_input_validation_error(response)

    # without translation
    obj = {
        "token": all_tokens[0]['token'],
        "occurrences": all_tokens[0]["occurrences"]
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id+1),
        headers=headers_auth, json=[obj])
    assert_input_validation_error(response)

    # incorrect occurences
    wrong_occur = all_tokens[0]["occurrences"][0]
    wrong_occur['sentenceId'] = 0
    obj = {
        "token": all_tokens[0]['token'],
        "occurrences": [wrong_occur],
        "translation": "sample translation"
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=[obj])
    assert response.status_code ==404
    assert response.json()['details'] == "Sentence id, 0, not found for the selected project"

    # wrong token-occurence pair
    obj = {
        "token": all_tokens[0]['token'],
        "occurrences": all_tokens[1]['occurrences'],
        "translation": "sample translation"
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=[obj])
    assert response.status_code == 500
    assert response.json()['details'] ==\
         'Token, %s, and its occurence, not matching'%(all_tokens[0]['token'])

def test_drafts():
    '''End to end test from tokenization to draft generation'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    resp = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=true",headers=headers_auth)
    assert resp.status_code == 200
    all_tokens = resp.json()

    # translate all tokens at once
    post_obj_list = []
    for item in all_tokens:
        obj = {
            "token": item['token'],
            "occurrences": item["occurrences"],
            "translation": "test"
        }
        post_obj_list.append(obj)
    resp = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Token translations saved"

    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id),headers=headers_auth)
    assert response.status_code ==200
    assert isinstance(response.json(), list)
    assert "\\v 1 test test test" in response.json()[0]

    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
        "&books=mat",headers=headers_auth)
    assert len(response.json()) == 1
    assert "\\id MAT" in response.json()[0]

    #Without Auth
    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
        "&books=mat", headers=headers)
    assert response.json()['error'] == 'Authentication Error'
    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
        "&books=mat",headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    # To be added: proper tests for alignment json drafts
    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
        "&output_format=alignment-json",headers=headers_auth)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_get_token_sentences():
    '''Check if draft-meta is properly segemneted according to specifed token occurence'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    resp = client.get("/v2/translation/project/tokens?project_id="+str(project_id)
        ,headers=headers_auth)
    tokens = resp.json()
    our_token = tokens[0]['token']
    occurrences = tokens[0]['occurrences']

    #before translating
    response = client.put('/v2/translation/project/token-sentences?project_id='+
        str(project_id)+'&token='+our_token,
        json=occurrences, headers=headers_auth)
    assert response.status_code == 200
    for sent, occur in zip(response.json(), occurrences):
        assert_positive_get_sentence(sent)
        found_slice = False
        if sent['sentenceId'] == occur["sentenceId"]:
            for meta in sent['draftMeta']:
                if meta[0] == occur['offset']:
                    found_slice = True
        assert found_slice

    post_obj_list = [
      {
        "token": our_token,
        "occurrences": occurrences,
        "translation": "sample"
      }
    ]
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert response.status_code == 201
    assert response.json()['message'] == 'Token translations saved'

    # after translation
    response2 = client.put('/v2/translation/project/token-sentences?project_id='+
        str(project_id)+'&token='+our_token, headers=headers_auth,
        json=occurrences)
    assert response2.status_code == 200
    for sent, occur in zip(response2.json(), occurrences):
        found_slice = False
        if sent['sentenceId'] == occur["sentenceId"]:
            for meta in sent['draftMeta']:
                if meta[0] == occur['offset']:
                    found_slice = True
                    assert meta[2] == "confirmed"
        assert found_slice

    #Without auth
    response2 = client.put('/v2/translation/project/token-sentences?project_id='+
        str(project_id)+'&token='+our_token, json=occurrences)
    assert response2.json()['error'] == 'Permission Denied'

def test_get_sentence():
    '''Positive test for agmt sentence/draft fetch API'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # before adding books
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)
    ,headers=headers_auth)
    assert_not_available_content(response)

    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # before translation
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&with_draft=True",headers=headers_auth)
    assert response.status_code ==200
    assert len(response.json()) > 1
    for item in response.json():
        assert_positive_get_sentence(item)
        assert item['sentence'] != ""
        assert item['draft'] == ""


    # translate all tokens at once
    resp = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=true",headers=headers_auth)
    assert resp.status_code == 200
    all_tokens = resp.json()
    post_obj_list = []
    for item in all_tokens:
        obj = {
            "token": item['token'],
            "occurrences": item["occurrences"],
            "translation": "test"
        }
        post_obj_list.append(obj)
    resp = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Token translations saved"

    # after token translation
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&with_draft=True",headers=headers_auth)
    assert response.status_code ==200
    for item in response.json():
        assert_positive_get_sentence(item)
        words = re.findall(r'\w+',item['draft'])
        for wrd in words:
            assert wrd == "test"

    #without auth        
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&with_draft=True", headers=headers)
    assert response.json()['error'] == 'Authentication Error'
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&with_draft=True",headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    # With only_ids
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&only_ids=True",headers=headers_auth)
    assert response.status_code ==200
    for item in response.json():
        assert "sentenceId" in item
        assert "surrogateId" in item
        assert "sentence" not in item
        assert "draft" not in item
        assert "draftMeta" not in item

def test_progress_n_suggestion():
    '''tests for project progress API of AgMT'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # before adding books
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id)
    ,headers=headers_auth)
    assert response.status_code ==200
    assert response.json()['confirmed'] == 0
    assert response.json()['untranslated'] == 0
    assert response.json()['suggestion'] == 0

    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # before translation
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id)
    ,headers=headers_auth)
    assert response.status_code ==200
    assert response.json()['confirmed'] == 0
    assert response.json()['untranslated'] == 1
    assert response.json()['suggestion'] == 0

    # # Apply suggestions
    # resp = client.put(UNIT_URL+"/suggestions?project_id="+str(project_id))
    # assert resp.status_code ==201
    # found_suggestion = False
    # [print(sent['draft']) for sent in resp.json()]
    # for sent in resp.json():
    #     for meta in sent['draftMeta']:
    #         if meta[2] == 'suggestion':
    #             found_suggestion = True
    #             break
    # assert found_suggestion

    # # after suggestions
    # response = client.get(UNIT_URL+"/progress?project_id="+str(project_id))
    # assert response.status_code ==200
    # assert response.json()['suggestion'] > 0

    # translate all tokens at once
    resp = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=true",headers=headers_auth)
    assert resp.status_code == 200
    all_tokens = resp.json()
    post_obj_list = []
    for item in all_tokens:
        obj = {
            "token": item['token'],
            "occurrences": item["occurrences"],
            "translation": "test"
        }
        post_obj_list.append(obj)
    resp = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Token translations saved"

    # after token translation
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id)
    ,headers=headers_auth)
    assert response.status_code ==200
    assert ceil(response.json()['confirmed']) == 1
    assert floor(response.json()['untranslated']) == 0

    #Without Auth
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id), headers=headers)
    assert response.json()['error'] == 'Authentication Error'
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id)
    ,headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

def test_get_versification():
    '''Positive test for agmt sentence/draft fetch API'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # before adding books
    response = client.get(UNIT_URL+"/versification?project_id="+str(project_id)
    ,headers=headers_auth)
    for key in response.json():
        assert len(response.json()[key]) == 0

    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    response = client.get(UNIT_URL+"/versification?project_id="+str(project_id)
    ,headers=headers_auth)
    found_mat = False
    found_mrk = False
    for book in response.json()['maxVerses']:
        if book == "mat":
            found_mat = True
        if book == "mrk":
            found_mrk = True
    assert found_mat and found_mrk

    #without auth
    response = client.get(UNIT_URL+"/versification?project_id="+str(project_id), headers=headers)
    assert response.json()['error'] == 'Authentication Error'
    #without auth but from Autographa
    response = client.get(UNIT_URL+"/versification?project_id="+str(project_id)
    ,headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

#Project translation Access Rules based tests
def test_agmt_translation_access_rule_app():
    """project translation related access rule and auth"""
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    #create a project
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    #get tokens
    #without auth not from Autographa
    resp = client.get("/v2/translation/project/tokens?project_id="+str(project_id))
    assert resp.json()['error'] == "Permission Denied"
    #without auth and from Autographa
    resp = client.get("/v2/translation/project/tokens?project_id="+str(project_id)
        ,headers=headers)
    assert resp.status_code == 401
    assert resp.json()['error'] == 'Authentication Error'
    #With Auth and From Autographa
    resp = client.get("/v2/translation/project/tokens?project_id="+str(project_id)
        ,headers=headers_auth)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    for item in resp.json():
        assert_positive_get_tokens(item)

    #Apply token translations PUT
    all_tokens = resp.json()
    our_token = all_tokens[0]['token']
    occurrences = all_tokens[0]['occurrences']

    post_obj_list = [
      {
        "token": all_tokens[0]['token'],
        "occurrences": [all_tokens[0]["occurrences"][0]],
        "translation": "test translation"
      }
    ]
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert response.status_code == 201
    assert response.json()['message'] == 'Token translations saved'
    #Wihout Auth from Autographa
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers, json=post_obj_list)
    assert response.json()['error'] == "Authentication Error"
    #Outside Autographa wihtou Auth
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
    json=post_obj_list)
    assert response.json()['error'] == "Permission Denied"

    #get token translation
    ##################################################################################
    ########################################
    data_str = json.dumps(post_obj_list)
    params={
            "project_id": str(project_id),
            "token": all_tokens[0]['token'],
            "sentence_id": "41001001",
            "offset": ["0", "4"],
            "data": data_str
        }

    response = client.get(UNIT_URL + "/token-translations",
        params=params,
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) > 0
    #Without Auth from Autographa
    
    response = client.get(UNIT_URL + "/token-translations",
        params=params,
        headers=headers
        )
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Without Auth and not from Autographa
    
    response = client.get(
         UNIT_URL + "/token-translations",
            params=params)
    assert response.json()['error'] == "Permission Denied"

    #Get Token Sentences PUT
    response = client.put('/v2/translation/project/token-sentences?project_id='+
        str(project_id)+'&token='+our_token,
        json=occurrences, headers=headers_auth)
    assert response.status_code == 200
    #Without Auth and from Autographa
    response = client.put('/v2/translation/project/token-sentences?project_id='+
        str(project_id)+'&token='+our_token,
        json=occurrences, headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == "Authentication Error"
    #Without Auth and not from Autographa
    response = client.put('/v2/translation/project/token-sentences?project_id='+
        str(project_id)+'&token='+our_token,
        json=occurrences)
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

    #Get Draft
    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
        "&output_format=alignment-json",headers=headers_auth)
    assert response.status_code == 200
    #Without Auth and From Autographa
    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
        "&output_format=alignment-json",headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Without Auth and not From Autographa
    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
        "&output_format=alignment-json")
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

    #Project Resource Get
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&with_draft=True",headers=headers_auth)
    assert response.status_code ==200
    #Without Auth and From Autographa
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&with_draft=True",headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Without Auth and not From Autographa
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&with_draft=True")
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

    #Project Progress
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id),
    headers=headers_auth)
    assert response.status_code ==200
    #Without Auth and From Autographa
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id),
    headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Without Auth and not From Autographa
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id))
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

    #Project Versification
    response = client.get(UNIT_URL+"/versification?project_id="+str(project_id)
    ,headers=headers_auth)
    assert response.status_code ==200
    #Without Auth and From Autographa
    response = client.get(UNIT_URL+"/versification?project_id="+str(project_id)
    ,headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #Without Auth and not From Autographa
    response = client.get(UNIT_URL+"/versification?project_id="+str(project_id))
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

def test_data_updated_time():
    '''Bugfix of issue #563:https://github.com/Bridgeconn/vachan-api/issues/563 '''

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']

    #create an empty project
    create_project_resp = add_project(project_data)
    assert create_project_resp.json()['message'] == "Project created successfully"
    project_id = create_project_resp.json()['data']['projectId']
    project_name =create_project_resp.json()['data']['projectName']
    project_create_time = create_project_resp.json()['data']['createTime']

    # Add book into empty project
    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat']]
    }
    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # Get tokens
    resp = client.get("/v2/translation/project/tokens?project_id="+str(project_id)
         ,headers=headers_auth)

    # Case 1:PUT Tokens
    #Apply token translations
    all_tokens = resp.json()
    post_obj_list = [
      {
        "token": all_tokens[0]['token'],
        "occurrences": [all_tokens[0]["occurrences"][0]],
        "translation": "test translation"
      }
    ]
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)

    # Get project details
    project_url = f"/v2/translation/projects?project_name={project_name}"
    project_resp = client.get(project_url, headers=headers_auth)
    project_update_time = project_resp.json()[0]['updateTime']
    assert not project_create_time == project_update_time

    # Check sentences are added
    resp = client.get(f"{UNIT_URL}/sentences?project_id={project_id}", headers=headers_auth)
    sentence_id = resp.json()[0]['sentenceId']

    # Case 2 : PUT Draft
    put_data = [
            {"sentenceId":sentence_id,
             "draft": "കാട്",
             "draftMeta":[
                  [ [5,11], [0,4], "confirmed"]
                ]
            }
    ]
    resp = client.put(f"/v2/translation/project/draft?project_id={project_id}",
        headers=headers_auth, json=put_data)
    # Get project details
    project_resp = client.get(project_url, headers=headers_auth)
    project_update_time = project_resp.json()[0]['updateTime']
    assert not project_create_time == project_update_time
 
    #Case 3: Update suggestions
    resp = client.put(f"/v2/translation/project/suggestions?project_id={project_id}&sentenceIdList={sentence_id}",
        headers=headers_auth)
    assert resp.status_code == 201
     # Get project details
    project_resp = client.get(project_url, headers=headers_auth)
    project_update_time = project_resp.json()[0]['updateTime']
    assert not project_create_time == project_update_time

    # Case 4 : Delete Sentence
    response = client.delete(f"{UNIT_URL}/sentences?project_id={project_id}&sentence_id={sentence_id}",
            headers=headers_auth)
    assert response.status_code == 201
    assert "successfull" in response.json()['message']
     # Get project details
    project_resp = client.get(project_url, headers=headers_auth)
    project_update_time = project_resp.json()[0]['updateTime']
    assert not project_create_time == project_update_time


#Project translation Access rules based permission
def test_agmt_translation_access_permissions():
    """test for access permission to project translation"""
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    #create a project
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/translation/projects", headers=headers_auth, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    resp = client.get("/v2/translation/project/tokens?project_id="+str(project_id)
        ,headers=headers_auth)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    for item in resp.json():
        assert_positive_get_tokens(item)

    #Apply token translations PUT
    all_tokens = resp.json()
    our_token = all_tokens[0]['token']
    occurrences = all_tokens[0]['occurrences']

    post_obj_list = [
      {
        "token": all_tokens[0]['token'],
        "occurrences": [all_tokens[0]["occurrences"][0]],
        "translation": "test translation"
      }
    ]

    #create a AgUser and add as memeber to a project and SA
    #Super Admin
    SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(SA_user_data)
    assert response.json()['message'] == "Login Succesfull"
    test_SA_token = response.json()["token"]

    #PUT Permission in agmt translations
    #"SuperAdmin", "AgAdmin", "projectOwner", "projectMember"
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert response.status_code == 201
    assert response.json()['message'] == 'Token translations saved'

    headers_auth['Authorization'] = "Bearer"+" "+test_SA_token
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert response.status_code == 201
    assert response.json()['message'] == 'Token translations saved'

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser2']['token']
    #PUT with Aguser not a member
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

    response = client.put('/v2/translation/project/token-sentences?project_id='+
        str(project_id)+'&token='+our_token,
        json=occurrences, headers=headers_auth)
    assert response.status_code == 403
    assert response.json()['error'] == "Permission Denied"

    #Add AgUser as memeber to projects
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    response = client.post('/v2/translation/project/user'+'?project_id='+str(project_id)+
        '&user_id='+str(initial_test_users['AgUser2']["test_user_id"]),headers=headers_auth)
    assert response.status_code == 201
    assert response.json()['message'] == "User added to project successfully"

    #After adding as member PUT
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser2']['token']
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers_auth, json=post_obj_list)
    assert response.status_code == 201
    print("resp after put token:",resp.json())

    response = client.put('/v2/translation/project/token-sentences?project_id='+
        str(project_id)+'&token='+our_token,
        json=occurrences, headers=headers_auth)
    assert response.status_code == 200

    #GET Permission in agmt translations
    #"SuperAdmin", "AgAdmin", "projectOwner", "projectMember", "BcsDeveloper"
    token_list = []
    token_list.append(test_SA_token)
    token_list.append(initial_test_users['AgUser2']['token'])
    token_list.append(initial_test_users['AgAdmin']['token'])
    token_list.append(initial_test_users['BcsDev']['token'])
    token_list.append(initial_test_users['AgAdmin']['token'])

    for user_token in token_list:
        headers_auth['Authorization'] = "Bearer"+" "+user_token
        resp = client.get("/v2/translation/project/tokens?project_id="+str(project_id)
            ,headers=headers_auth)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        for item in resp.json():
            assert_positive_get_tokens(item)
            
        data_str = json.dumps(post_obj_list)
        response = client.get(
            UNIT_URL + "/token-translations",
            params={
                "project_id": str(project_id),
                "token": all_tokens[0]['token'],
                "sentence_id": "41001001",
                "offset": ["0", "4"],
                "data": data_str
                },
            headers=headers_auth)
        assert response.status_code == 200
        assert len(response.json()) > 0

        response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
            "&output_format=alignment-json",headers=headers_auth)
        assert response.status_code == 200
        assert len(response.json()) > 0

        response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
            "&with_draft=True",headers=headers_auth)
        assert response.status_code ==200
        assert len(response.json()) > 0

        response = client.get(UNIT_URL+"/progress?project_id="+str(project_id),
        headers=headers_auth)
        assert response.status_code ==200
        assert len(response.json()) > 0

        response = client.get(UNIT_URL+"/versification?project_id="+str(project_id)
        ,headers=headers_auth)
        assert response.status_code ==200
        assert len(response.json()) > 0

    #Not getting Content
    #Aguser is not member of project
    token_list = []
    token_list.append(initial_test_users['VachanUser']['token'])
    token_list.append(initial_test_users['AgUser']['token'])
    token_list.append(initial_test_users['APIUser']['token'])
    token_list.append(initial_test_users['VachanAdmin']['token'])

    for user_token in token_list:
        headers_auth['Authorization'] = "Bearer"+" "+user_token
        resp = client.get("/v2/translation/project/tokens?project_id="+str(project_id)
            ,headers=headers_auth)    
        assert resp.status_code == 403
        assert resp.json()['error'] == "Permission Denied"

        data_str = json.dumps(post_obj_list)
        response = client.get(
            UNIT_URL + "/token-translations",
         params={
                "project_id": str(project_id),
                "token": all_tokens[0]['token'],
                "sentence_id": "41001001",
                "offset": ["0", "4"],
                "data": data_str
                },
             headers=headers_auth)
        assert response.status_code == 403
        assert response.json()['error'] == "Permission Denied"

        response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
            "&output_format=alignment-json",headers=headers_auth)
        assert response.status_code == 403
        assert response.json()['error'] == "Permission Denied"

        response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
            "&with_draft=True",headers=headers_auth)
        assert response.status_code == 403
        assert response.json()['error'] == "Permission Denied"

        response = client.get(UNIT_URL+"/progress?project_id="+str(project_id),
        headers=headers_auth)
        assert response.status_code == 403
        assert response.json()['error'] == "Permission Denied"

        response = client.get(UNIT_URL+"/versification?project_id="+str(project_id)
        ,headers=headers_auth)
        assert response.status_code == 403
        assert response.json()['error'] == "Permission Denied"