'''Tests the translation APIs that do need projects available in DB'''
import re
import csv

from . import client
from . import assert_input_validation_error, assert_not_available_content
from .test_agmt_translation import assert_positive_get_tokens, assert_positive_get_sentence
from .conftest import initial_test_users

UNIT_URL = '/v2/translation'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"
            }

sentences = [
    "Once upon a time, there was a test case.",
    "The test case tested for all the anticipated usages, that the developer could think of.",
    "But there were a few senarios which escaped his thoughts and were left out.",
    "Thus, even though the test was always run and ensured to pass every time,",
    "the few cases that were forgotten made it not effective.",
    "This is the sad story of a poor test which worked so hard and yet couldn't be good enough.☹️."
]
sentence_list = [{"sentenceId":i, "sentence":s} for i,s in enumerate(sentences)]

sample_sent = "इब्राहीम के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस प्रकार है"
post_obj = {"sentence_list":[{
                "sentenceId":1, 
                "sentence":sample_sent}],
            "stopwords":{
                "prepositions":["इस"],
                "postpositions":["के", "की", "है"]
            }}
def test_tokenize():
    '''Positve tests for generic tokenization API'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    default_response = client.put(UNIT_URL+'/tokens?source_language=en', headers=headers_auth,
        json={"sentence_list":sentence_list})
    assert default_response.status_code == 200
    assert len(default_response.json()) >10 
    for item in default_response.json():
        assert_positive_get_tokens(item)

    #without auth
    response = client.put(UNIT_URL+'/tokens?source_language=en&include_phrases=True',
        headers=headers, json={"sentence_list":sentence_list})
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.put(UNIT_URL+'/tokens?source_language=en&include_phrases=True',
        headers=headers_auth, json={"sentence_list":sentence_list})
    assert response.status_code == 200
    assert default_response.json() == response.json()  

    response = client.put(UNIT_URL+'/tokens?source_language=en',
        headers=headers, json={"sentence_list":sentence_list[:3]})
    #without auth
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.put(UNIT_URL+'/tokens?source_language=en',
        headers=headers_auth, json={"sentence_list":sentence_list[:3]}) 
    assert response.status_code == 200
    for item in response.json():
        assert_positive_get_tokens(item)
    assert len(default_response.json()) > len(response.json())  

    # include_phrases flag
    #without auth
    response = client.put(UNIT_URL+"/tokens?source_language=en"+
        "&include_phrases=true", headers=headers,
        json={"sentence_list":sentence_list})
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.put(UNIT_URL+"/tokens?source_language=en"+
        "&include_phrases=true", headers=headers_auth,
        json={"sentence_list":sentence_list})
    assert response.json() == default_response.json()

    response = client.put(UNIT_URL+"/tokens?source_language=en"+
        "&include_phrases=false", headers=headers_auth,
        json={"sentence_list":sentence_list})
    assert response.status_code == 200
    assert len(response.json()) <= len(default_response.json())
    for item in response.json():
        assert_positive_get_tokens(item)
        assert " " not in item['token']

    # include stopwords flag
    sample_stopwords = ["the", "is", "a"]
    #without auth
    response = client.put(UNIT_URL+"/tokens?source_language=en"+
        "&include_stopwords=false", headers=headers,
        json={"sentence_list":sentence_list})
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.put(UNIT_URL+"/tokens?source_language=en"+
        "&include_stopwords=false", headers=headers_auth,
        json={"sentence_list":sentence_list})
    assert response.json() == default_response.json()
    for item in response.json():
        assert_positive_get_tokens(item)
        assert item['token'] not in sample_stopwords

    response = client.put(UNIT_URL+"/tokens?source_language=en"+
        "&include_stopwords=true", headers=headers_auth,
        json={"sentence_list":sentence_list})
    assert response.status_code == 200
    for item in response.json():
        assert_positive_get_tokens(item)

    response = client.put(UNIT_URL+"/tokens?source_language=en"+
        "&include_stopwords=true&include_phrases=false", headers=headers_auth,
        json={"sentence_list":sentence_list})
    assert response.status_code == 200
    all_words = [item['token'] for item in response.json()]
    for swd in sample_stopwords:
        assert swd in all_words



def test_tokenize_with_diff_flags():
    '''Postive tests for tokenizing a single input sentence with varying parameters'''
    response = client.put(UNIT_URL+"/tokens?source_language=hi"+
        "&include_stopwords=true&include_phrases=false&use_translation_memory=false",
        headers=headers_auth, json=post_obj)
    assert response.status_code == 200
    all_words = [item['token'] for item in response.json()]
    for word in sample_sent.split(): # covers all words in source
        assert word in all_words
    assert len(all_words) == len(set(all_words)) #unique
    for word in all_words: # no phrases
        assert " " not in word

    response = client.put(UNIT_URL+"/tokens?source_language=hi"+
        "&include_stopwords=true&include_phrases=true&use_translation_memory=false",
        headers=headers_auth, json=post_obj)
    assert response.status_code == 200
    all_tokens = [item['token'] for item in response.json()]
    assert "इस प्रकार है" in all_tokens
    assert "इब्राहीम के" in all_tokens

    response = client.put(UNIT_URL+"/tokens?source_language=hi"+
        "&include_stopwords=false&include_phrases=true&use_translation_memory=false",
        headers=headers_auth, json=post_obj)
    assert response.status_code == 200
    all_tokens = [item['token'] for item in response.json()]
    # no independant stopwords are present
    for swd in post_obj['stopwords']['prepositions'] + post_obj['stopwords']['postpositions']:
        assert swd not in all_tokens
    assert "इस प्रकार है" in all_tokens # stopwords coming within phrases are included
    assert "इब्राहीम के" in all_tokens

    # make a translation
    trans_obj = post_obj
    trans_obj['token_translations'] = [
        { "token": "यीशु मसीह",
          "occurrences": [
            { "sentenceId": 1,
              "offset": [31,40]}
          ],
          "translation": "Jesus Christ"}
      ]

    response = client.put(UNIT_URL+"/token-translate?source_language=hi"+
        "&target_language=en&use_data_for_learning=true",
        headers=headers_auth, json=trans_obj)
    assert response.status_code ==200

    # after a translation testing for use_translation_memory flag
    response = client.put(UNIT_URL+"/tokens?source_language=hi"+
        "&include_stopwords=true&include_phrases=true&use_translation_memory=true",
        headers=headers_auth, json=post_obj)
    assert response.status_code == 200
    all_tokens = [item['token'] for item in response.json()]
    assert "यीशु मसीह" in all_tokens
    assert "की" in all_tokens

    response = client.put(UNIT_URL+"/tokens?source_language=hi"+
        "&use_translation_memory=true",
        headers=headers_auth, json=post_obj)
    assert response.status_code == 200
    all_tokens = [item['token'] for item in response.json()]
    assert "यीशु मसीह" in all_tokens
    assert "की" not in all_tokens

    response = client.put(UNIT_URL+"/tokens?source_language=hi"+
        "&use_translation_memory=false",
        headers=headers_auth, json=post_obj)
    assert response.status_code == 200
    all_tokens = [item['token'] for item in response.json()]
    assert "यीशु मसीह" not in all_tokens
    assert "यीशु" in all_tokens

def test_token_translate():
    '''Positive tests to apply token translationa nd obtain drafts'''

    #tokenize
    resp = client.put(UNIT_URL+"/tokens?source_language=hi&use_translation_memory=false"+
        "&include_stopwords=true",
        headers=headers_auth, json=post_obj)
    assert resp.status_code ==200
    all_tokens = resp.json()
    for tok in all_tokens:
        assert_positive_get_tokens(tok)
        assert tok != "यीशु मसीह"

    # translate one token
    trans_obj = post_obj
    trans_obj['token_translations'] = [
        { "token": all_tokens[0]['token'],
          "occurrences": [all_tokens[0]['occurrences'][0]],
          "translation": "test"}
      ]

    response = client.put(UNIT_URL+"/token-translate?source_language=hi"+
        "&target_language=en&use_data_for_learning=false",
        headers=headers_auth, json=trans_obj)
    assert response.status_code ==200
    return_sent = response.json()['data'][0]
    assert_positive_get_sentence(return_sent)
    assert return_sent['draft'].startswith("test")
    assert return_sent['draftMeta'][0][2] == "confirmed"
    assert return_sent['draftMeta'][1][2] == "untranslated"
    assert len(return_sent['draftMeta']) == 2

    # translate all tokens
    trans_obj = {"sentence_list": [return_sent], 'token_translations':[]}
    for tok in all_tokens:
        obj = {"token": tok['token'], "occurrences":tok["occurrences"], "translation":"test"}
        trans_obj['token_translations'].append(obj)
    response = client.put(UNIT_URL+"/token-translate?source_language=hi"+
        "&target_language=en&use_data_for_learning=false",
        headers=headers_auth, json=trans_obj)
    assert response.status_code ==200
    return_sent = response.json()['data'][0]
    assert_positive_get_sentence(return_sent)
    words_in_draft = re.findall(r'\w+',return_sent['draft'])
    for word in words_in_draft:
        assert word == 'test'
    for meta in return_sent['draftMeta']:
        if meta[0][1] - meta[0][0] > 1: # all non space and non-punct parts of input
            assert meta[2] == "confirmed"

    # make a translation for a token not in token list
    # it combines & re-translates 2 already translated tokens
    # and use data for learning
    trans_obj = {"sentence_list": [return_sent]}
    trans_obj['token_translations'] = [
        { "token": "यीशु मसीह",
          "occurrences": [
            { "sentenceId": 1,
              "offset": [31,40]}
          ],
          "translation": "Jesus Christ"}
      ]
    response = client.put(UNIT_URL+"/token-translate?source_language=hi"+
        "&target_language=en",
        headers=headers_auth, json=trans_obj)
    assert response.status_code ==200
    new_return_sent = response.json()['data'][0]
    assert "Jesus Christ" in new_return_sent['draft']
    # combined two segments to one
    assert len(new_return_sent['draftMeta']) == len(return_sent['draftMeta']) -1

def test_draft_generation():
    '''tests conversion of sentence list to differnt draft formats'''
    verse_start = 41001001
    for i,sentence in enumerate(sentence_list):
        sentence['sentenceId'] = verse_start+i
    #without auth
    response = client.put(UNIT_URL+'/draft?doc_type=usfm', headers=headers, json=sentence_list)
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.put(UNIT_URL+'/draft?doc_type=usfm', headers=headers_auth, json=sentence_list)
    assert response.status_code == 200
    assert "\\id MAT" in response.json()[0]
    assert sentence_list[0]['sentence'] in response.json()[0]

    response = client.put(UNIT_URL+'/draft?doc_type=csv', headers=headers_auth, json=sentence_list)
    assert response.status_code == 200
    assert sentence_list[0]['sentence'] in response.json()
    lines = response.json().split('\n')
    parse_csv = True
    try:
        csv.reader(lines)
    except csv.Error:
        parse_csv = False
    assert parse_csv

    response = client.put(UNIT_URL+'/draft?doc_type=text', headers=headers_auth, json=sentence_list)
    assert response.status_code == 200
    input_text = " ".join([sent['sentence'] for sent in sentence_list])
    assert input_text.strip() == response.json().strip()

    # to be implemented: alignment-json
