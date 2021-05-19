'''tests the APIs related to translation suggestion module'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from .test_agmt_translation import assert_positive_get_tokens, assert_positive_get_sentence
from .test_generic_translation import sentence_list, sample_sent

UNIT_URL = '/v2/translation'
headers = {"contentType": "application/json", "accept": "application/json"}


tokens_trans = [
    {"token":"test", "translations":["ടെസ്റ്റ്"]},
    {"token":"test case", "translations":["ടെസ്റ്റ് കേസ്"]},
    {"token":"deveopler", "translations":["ടെവെലപ്പര്‍"]},
    {"token":"run", "translations":["റണ്‍"]},
    {"token":"pass", "translations":["പാസ്സ്"]},
    {"token":"tested", "translations":["ടെസ്റ്റഡ്", "ടെസ്റ്റ് ചെയ്തു"],
        "tokenMetaData":{"tense": "past"}}
]

align_data = [
    {   "sourceTokenList": ["This", "is", "a test case"],
        "targetTokenList": ["ഇത്", "ഒരു ടെസ്റ്റ് കേസ്", "ആണ്"],
        "alignedTokens":[
            {"sourceTokenIndex":0, "targetTokenIndex":0},
            {"sourceTokenIndex":1, "targetTokenIndex":2},
            {"sourceTokenIndex":2, "targetTokenIndex":1}]
    },
    {   "sourceTokenList": ["Developer", "is not", "happy"],
        "targetTokenList": ["ടെവെലപ്പര്‍", "സന്തോഷവാന്‍", "അല്ല"],
        "alignedTokens":[
            {"sourceTokenIndex":0, "targetTokenIndex":0},
            {"sourceTokenIndex":1, "targetTokenIndex":2},
            {"sourceTokenIndex":2, "targetTokenIndex":1}]
    },
    {   "sourceTokenList": ["Happy", "user", "is here"],
        "targetTokenList": ["സന്തോഷവാന്‍ ആയ", "ഉപയോക്താവ്" , "ഇവിടുണ്ട്"],
        "alignedTokens":[
            {"sourceTokenIndex":0, "targetTokenIndex":0},
            {"sourceTokenIndex":1, "targetTokenIndex":2},
            {"sourceTokenIndex":2, "targetTokenIndex":1}]
    }

]

def assert_positive_get_suggetion(item):
    '''check for properties in a suggestion response'''
    assert "translations" in item
    assert isinstance(item['translations'], dict)
    for sense in item['translations']:
        assert isinstance(item['translations'][sense], (int, float))
    if "metaData" in item and item['metaData'] is not None:
        assert isinstance(item['metaData'], dict)


def test_learn_n_suggest():
    '''Positive tests for adding knowledge and getting suggestions'''

    # add dictionary
    response = client.post(UNIT_URL+'/learn/gloss?source_language=en&target_language=ml',
        headers=headers, json=tokens_trans)
    assert response.status_code == 201
    assert response.json()['message'] == "Added to glossary"

    # check if suggestions are given in token list
    token_response = client.put(UNIT_URL+'/tokens?source_language=en&target_language=ml',
        headers=headers, json={"sentence_list":sentence_list}) 
    assert token_response.status_code == 200
    assert len(token_response.json()) >10
    found_testcase = False
    found_tested = False 
    for item in token_response.json():
        if item['token'] == "tested":
            assert "ടെസ്റ്റഡ്" in item['translations']
            assert "ടെസ്റ്റ് ചെയ്തു" in item['translations']
            assert item["metaData"]["tense"] == "past"
            found_tested = True
        assert_positive_get_tokens(item)
        if item['token'] == "test case":
            assert "ടെസ്റ്റ് കേസ്" in item['translations']
            assert item['translations']["ടെസ്റ്റ് കേസ്"] == 0
            found_testcase = True
    assert found_tested
    assert found_testcase

    # add alignmnet
    response = client.post(UNIT_URL+'/learn/alignment?source_language=en&target_language=ml',
        headers=headers, json=align_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Alignments used for learning"
    found_lower_developer = False
    for item in response.json()['data']:
        if item['token'] == 'developer':
            found_lower_developer = True
    assert found_lower_developer

    # try tokenizing again
    token_response = client.put(UNIT_URL+'/tokens?source_language=en&target_language=ml',
        headers=headers, json={"sentence_list":sentence_list}) 
    assert token_response.status_code == 200
    found_atestcase  = False
    found_lower_developer = False
    for item in token_response.json():
        assert_positive_get_tokens(item)
        if item['token'] == 'a test case':
            assert "ഒരു ടെസ്റ്റ് കേസ്" in item['translations']
            found_atestcase = True
        if item['token'] == 'developer':
            assert item['translations']['ടെവെലപ്പര്‍'] == 1
            found_lower_developer = True
    assert found_atestcase
    assert found_lower_developer

    # get gloss

    # only a dict entry not in draft or alignment
    response = client.get(UNIT_URL+'/gloss?source_language=en&target_language=ml&token=test')
    assert response.status_code ==200
    assert isinstance(response.json(), dict)
    assert len(response.json()['translations']) > 0
    assert_positive_get_suggetion(response.json())
    found_test = False
    for item in response.json()['translations']:
        if item == "ടെസ്റ്റ്":
            found_test = True
    assert found_test

    # learnt from alignment
    response = client.get(UNIT_URL+
        '/gloss?source_language=en&target_language=ml&token=a%20test%20case')
    assert response.status_code ==200
    assert_positive_get_suggetion(response.json())
    found_atestcase = False
    for item in response.json()['translations']:
        if item == "ഒരു ടെസ്റ്റ് കേസ്":
            found_atestcase = True
    assert found_atestcase

    # with different contexts
    sense1 = "സന്തോഷവാന്‍"
    sense2 = "സന്തോഷവാന്‍ ആയ"

    #no context
    response = client.get(UNIT_URL+'/gloss?source_language=en&target_language=ml&token=happy')
    assert response.status_code ==200
    assert_positive_get_suggetion(response.json())
    found_sense1 = False
    found_sense2 = False
    for item in response.json()['translations']:
        if item == sense1:
            found_sense1 = True
            score1 = response.json()['translations'][item]
        if item == sense2:
            found_sense2 = True
            score2 = response.json()['translations'][item]
    assert found_sense1
    assert found_sense2
    assert score1 == score2


    # context 1
    response = client.get(UNIT_URL+'/gloss?source_language=en&target_language=ml&token=happy'+
        '&context=the%20happy%20user%20went%20home')
    assert response.status_code ==200
    assert_positive_get_suggetion(response.json())
    found_sense1 = False
    found_sense2 = False
    print(response.json())
    for item in response.json()['translations']:
        if item == sense1:
            found_sense1 = True
            score1 = response.json()['translations'][item]
        if item == sense2:
            found_sense2 = True
            score2 = response.json()['translations'][item]
    assert found_sense1
    assert found_sense2
    assert score1 < score2

    # context 2
    response = client.get(UNIT_URL+'/gloss?source_language=en&target_language=ml&token=happy'+
        '&context=now%20user%20is%20not%20happy')
    assert response.status_code ==200
    assert_positive_get_suggetion(response.json())
    found_sense1 = False
    found_sense2 = False
    for item in response.json()['translations']:
        if item == sense1:
            found_sense1 = True
            score1 = response.json()['translations'][item]
        if item == sense2:
            found_sense2 = True
            score2 = response.json()['translations'][item]
    assert found_sense1
    assert found_sense2
    assert score1 > score2

    # auto translate
    sentence_list[0]['sentence'] = "This his wish "+sentence_list[0]['sentence']
    response = client.put(UNIT_URL+'/suggestions?source_language=en&target_language=ml',
        headers=headers, json={"sentence_list":sentence_list})
    draft = client.put(UNIT_URL+'/draft?doc_type=text', headers=headers, json=response.json())
    draft = draft.json()
    print(draft)
    assert "ഒരു ടെസ്റ്റ് കേസ്." in draft
    assert "ടെസ്റ്റ് കേസ് ടെസ്റ്റ് ചെയ്തു" in draft
    assert "ടെവെലപ്പര്‍" in draft
    assert "This ആണ് the sad story of a poor ടെസ്റ്റ് " in draft
    