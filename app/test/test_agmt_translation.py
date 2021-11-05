'''tests for the translation workflow within AgMT projects'''

import re
from math import ceil, floor
from . import client
from . import assert_input_validation_error, assert_not_available_content
from .test_agmt_projects import bible_books, check_post as add_project


UNIT_URL = '/v2/autographa/project'
headers = {"contentType": "application/json", "accept": "application/json"}

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
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # before adding books
    get_response1 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id))
    assert_not_available_content(get_response1)

    put_data = {
        "projectId": project_id,
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/autographa/projects", headers=headers, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # after adding books
    get_response2 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id))
    assert get_response2.status_code == 200
    assert isinstance(get_response2.json(), list)
    for item in get_response2.json():
        assert_positive_get_tokens(item)

    # with book filter
    get_response3 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+"&books=mat")
    assert get_response3.status_code == 200
    assert len(get_response3.json()) < len(get_response2.json())

    get_response4 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+"&books=mrk")
    assert get_response4.status_code == 200
    all_tokens = [item['token'] for item in get_response3.json() + get_response4.json()]
    assert len(get_response2.json()) == len(set(all_tokens))

    # with range filter
    get_response5 = client.get(UNIT_URL+'/tokens?project_id='+str(project_id)+
        "&sentence_id_range=0&sentence_id_range=10")
    print(get_response5.json())
    assert_not_available_content(get_response5)

    get_response6 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_range=41000000&sentence_id_range=41999999")
    assert get_response6.status_code ==200
    assert get_response6.json() == get_response3.json()

    # with list filter
    get_response7 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_list=41000000")
    assert_not_available_content(get_response7)

    get_response7 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_list=41001001")
    assert get_response7.status_code == 200
    assert 0 < len(get_response7.json()) < 25

    # translation_memory flag
    get_response8 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&use_translation_memory=true")
    assert get_response8.json() == get_response2.json()

    get_response9 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&use_translation_memory=false")
    assert get_response9.status_code == 200
    assert len(get_response9.json()) > 0

    # include_phrases flag
    get_response10 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_phrases=true")
    assert get_response10.json() == get_response2.json()

    get_response11 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_phrases=false")
    assert get_response11.status_code == 200
    assert len(get_response11.json()) <= len(get_response10.json())
    for item in get_response11.json():
        assert " " not in item['token']

    # include_stopwords flag
    get_response12 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=false")
    assert get_response12.json() == get_response2.json()
    for item in get_response12.json():
        assert item['token'] not in sample_stopwords

    get_response13 = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=True&include_phrases=false")
    all_tokens = [item['token'] for item in get_response13.json()]
    assert sample_stopwords[0] in all_tokens


def test_tokenization_invalid():
    '''Negative tests for tokenization'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # non existant project
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id+1))
    assert response.status_code == 404
    assert response.json()['details'] == "Project with id, %s, not found"%(project_id+1)

    #invalid book
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+"&books=mmm")
    assert response.status_code == 404
    assert response.json()['details'] == 'Book, mmm, not in database'

    # only one value for range
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_range=41000000")
    assert_input_validation_error(response)

    # incorrect value for range
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_range=gen&sentence_id_range=num")
    assert_input_validation_error(response)

    # incorrect value for id
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&sentence_id_list=first")
    assert_input_validation_error(response)

    # incorrect value for flags
    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=Few")
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_phrases=10")
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&use_translation_memory=always")
    assert_input_validation_error(response)

def test_save_translation():
    '''Positive tests for PUT tokens method'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/autographa/projects", headers=headers, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    resp = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=true")
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
        headers=headers, json=post_obj_list)
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
        headers=headers, json=post_obj_list)
    assert response.status_code == 201
    assert response.json()['message'] == 'Token translations saved'
    for sent in response.json()['data']:
        assert "test translation" in sent['draft']

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
        headers=headers, json=post_obj_list)
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
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/autographa/projects", headers=headers, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    resp = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=true")
    assert resp.status_code == 200
    all_tokens = resp.json()

    # incorrect project id
    obj = {
        "token": all_tokens[0]['token'],
        "occurrences": all_tokens[0]["occurrences"],
        "translation": "sample translation"
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id+1),
        headers=headers, json=[obj])
    assert response.status_code == 404
    assert response.json()['details'] == 'Project with id, %s, not present'%(project_id+1)

    # without token
    obj = {
        "occurrences": all_tokens[0]["occurrences"],
        "translation": "sample translation"
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id+1),
        headers=headers, json=[obj])
    assert_input_validation_error(response)

    # without occurences
    obj = {
        "token": all_tokens[0]['token'],
        "translation": "sample translation"
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id+1),
        headers=headers, json=[obj])
    assert_input_validation_error(response)

    # without translation
    obj = {
        "token": all_tokens[0]['token'],
        "occurrences": all_tokens[0]["occurrences"]
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id+1),
        headers=headers, json=[obj])
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
        headers=headers, json=[obj])
    assert response.status_code ==404
    assert response.json()['details'] == "Sentence id, 0, not found for the selected project"

    # wrong token-occurence pair
    obj = {
        "token": all_tokens[0]['token'],
        "occurrences": all_tokens[1]['occurrences'],
        "translation": "sample translation"
    }
    response = client.put(UNIT_URL+"/tokens?project_id="+str(project_id),
        headers=headers, json=[obj])
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
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/autographa/projects", headers=headers, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    resp = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=true")
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
        headers=headers, json=post_obj_list)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Token translations saved"

    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id))
    assert response.status_code ==200
    assert isinstance(response.json(), list)
    assert "\\v 1 test test test" in response.json()[0]

    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
        "&books=mat")
    assert len(response.json()) == 1
    assert "\\id MAT" in response.json()[0]

    # To be added: proper tests for alignment json drafts
    response = client.get(UNIT_URL+'/draft?project_id='+str(project_id)+
        "&output_format=alignment-json")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_get_token_sentences():
    '''Check if draft-meta is properly segemneted according to specifed token occurence'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    put_data = {
        "projectId": project_id,
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/autographa/projects", headers=headers, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    resp = client.get("/v2/autographa/project/tokens?project_id="+str(project_id))
    tokens = resp.json()
    our_token = tokens[0]['token']
    occurrences = tokens[0]['occurrences']

    #before translating
    response = client.put('/v2/autographa/project/token-sentences?project_id='+
        str(project_id)+'&token='+our_token, headers=headers,
        json=occurrences)
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
        headers=headers, json=post_obj_list)
    assert response.status_code == 201
    assert response.json()['message'] == 'Token translations saved'

    # after translation
    response2 = client.put('/v2/autographa/project/token-sentences?project_id='+
        str(project_id)+'&token='+our_token, headers=headers,
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

def test_get_sentence():
    '''Positive test for agmt sentence/draft fetch API'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # before adding books
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id))
    assert_not_available_content(response)

    put_data = {
        "projectId": project_id,
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/autographa/projects", headers=headers, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # before translation
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&with_draft=True")
    assert response.status_code ==200
    assert len(response.json()) > 1
    for item in response.json():
        assert_positive_get_sentence(item)
        assert item['sentence'] == item['draft']


    # translate all tokens at once
    resp = client.get(UNIT_URL+"/tokens?project_id="+str(project_id)+
        "&include_stopwords=true")
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
        headers=headers, json=post_obj_list)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Token translations saved"

    # after token translation
    response = client.get(UNIT_URL+"/sentences?project_id="+str(project_id)+
        "&with_draft=True")
    assert response.status_code ==200
    for item in response.json():
        assert_positive_get_sentence(item)
        words = re.findall(r'\w+',item['draft'])
        for wrd in words:
            assert wrd == "test"

def test_progress_n_suggestion():
    '''tests for project progress API of AgMT'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # before adding books
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id))
    assert response.status_code ==200
    assert response.json()['confirmed'] == 0
    assert response.json()['untranslated'] == 0
    assert response.json()['suggestion'] == 0

    put_data = {
        "projectId": project_id,
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/autographa/projects", headers=headers, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    # before translation
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id))
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
        "&include_stopwords=true")
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
        headers=headers, json=post_obj_list)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Token translations saved"

    # after token translation
    response = client.get(UNIT_URL+"/progress?project_id="+str(project_id))
    assert response.status_code ==200
    assert ceil(response.json()['confirmed']) == 1
    assert floor(response.json()['untranslated']) == 0

def test_get_versification():
    '''Positive test for agmt sentence/draft fetch API'''
    resp = add_project(project_data)
    assert resp.json()['message'] == "Project created successfully"
    project_id = resp.json()['data']['projectId']

    # before adding books
    response = client.get(UNIT_URL+"/versification?project_id="+str(project_id))
    for key in response.json():
        assert len(response.json()[key]) == 0

    put_data = {
        "projectId": project_id,
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
    }
    resp = client.put("/v2/autographa/projects", headers=headers, json=put_data)
    assert resp.json()['message'] == "Project updated successfully"

    response = client.get(UNIT_URL+"/versification?project_id="+str(project_id))
    found_mat = False
    found_mrk = False
    for book in response.json()['maxVerses']:
        if book == "mat":
            found_mat = True
        if book == "mrk":
            found_mrk = True
    assert found_mat and found_mrk
