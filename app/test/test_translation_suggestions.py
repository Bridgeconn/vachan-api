'''tests the APIs related to translation suggestion module'''
from . import client
from . import assert_input_validation_error
from .test_agmt_translation import assert_positive_get_tokens, assert_positive_get_sentence
from .test_generic_translation import sentence_list, sample_sent
from .conftest import initial_test_users
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user

UNIT_URL = '/v2/translation'
NLP_UNIT_URL = '/v2/nlp'
RESTORE_URL = '/v2/restore'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"
            }

tokens_trans = [
    {"token":"test", "translations":["ടെസ്റ്റ്"]},
    {"token":"the", "translations":[""]},
    {"token":"test case", "translations":["ടെസ്റ്റ് കേസ്"]},
    {"token":"developer", "translations":["ടെവെലപ്പര്‍"]},
    {"token":"run", "translations":["റണ്‍"]},
    {"token":"pass", "translations":["പാസ്സ്"]},
    {"token":"tested", "translations":["ടെസ്റ്റഡ്"],
        "metaData":{"tense": "past"}}
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
            {"sourceTokenIndex":1, "targetTokenIndex":1},
            {"sourceTokenIndex":2, "targetTokenIndex":2}]
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
    #without auth
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.post(NLP_UNIT_URL+'/learn/gloss?source_language=en&target_language=ml',
        headers=headers, json=tokens_trans)
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.post(NLP_UNIT_URL+'/learn/gloss?source_language=en&target_language=ml',
        headers=headers_auth, json=tokens_trans)
    assert response.status_code == 201
    assert response.json()['message'] == "Added to glossary"

    # check if suggestions are given in token list
    #without auth
    token_response = client.put(UNIT_URL+'/tokens?source_language=en&target_language=ml',
        headers=headers, json={"sentence_list":sentence_list})
    assert token_response.json()['error'] == "Authentication Error"
    assert token_response.status_code == 401
    #with auth another registered user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    token_response = client.put(UNIT_URL+'/tokens?source_language=en&target_language=ml',
        headers=headers_auth, json={"sentence_list":sentence_list})
    assert token_response.status_code == 200
    assert len(token_response.json()) >10
    found_testcase = False
    found_tested = False
    for item in token_response.json():
        if item['token'] == "tested":
            assert "ടെസ്റ്റഡ്" in item['translations']
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
    response = client.post(NLP_UNIT_URL+'/learn/alignment?source_language=en&target_language=ml',
        headers=headers, json=align_data)
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.post(NLP_UNIT_URL+'/learn/alignment?source_language=en&target_language=ml',
        headers=headers_auth, json=align_data)
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
    assert token_response.json()['error'] == "Authentication Error"
    assert token_response.status_code == 401
    #with auth
    token_response = client.put(UNIT_URL+'/tokens?source_language=en&target_language=ml',
        headers=headers_auth, json={"sentence_list":sentence_list})
    assert token_response.status_code == 200
    found_atestcase  = False
    found_lower_developer = False
    for item in token_response.json():
        assert_positive_get_tokens(item)
        if item['token'] == 'a test case':
            assert "ഒരു ടെസ്റ്റ് കേസ്" in item['translations']
            found_atestcase = True
        if item['token'] == 'developer':
            assert item['translations']['ടെവെലപ്പര്‍'] >= 1
            found_lower_developer = True
    assert found_atestcase
    assert found_lower_developer

    # get gloss

    # only a dict entry not in draft or alignment
    response = client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=test',
    headers=headers)
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=test',
    headers=headers_auth)
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
    response = client.get(NLP_UNIT_URL+
        '/gloss?source_language=en&target_language=ml&token=a%20test%20case',headers=headers)
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.get(NLP_UNIT_URL+
        '/gloss?source_language=en&target_language=ml&token=a%20test%20case',headers=headers_auth)
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
    response = client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=happy',
    headers=headers)
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=happy',
    headers=headers_auth)
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
    response = client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=happy'+
        '&context=the%20happy%20user%20went%20home',headers=headers_auth)
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
    assert score1 < score2

    # context 2
    response = client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=happy'+
        '&context=now%20user%20is%20not%20happy',headers=headers_auth)
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
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401
    #with auth
    response = client.put(UNIT_URL+'/suggestions?source_language=en&target_language=ml',
        headers=headers_auth, json={"sentence_list":sentence_list})

    # ensures that source is tokenized in draftmeta, even when there is no suggestion
    assert len(response.json()[0]["draftMeta"]) > 7 
    assert len([meta for meta in response.json()[0]["draftMeta"] if meta[2]=="untranslated"]) > 4
    
    draft = client.put(UNIT_URL+'/draft?doc_type=text', headers=headers_auth, json=response.json())
    draft = draft.json()
    assert "ഒരു ടെസ്റ്റ് കേസ്." in draft
    assert "ടെസ്റ്റ് കേസ് ടെസ്റ്റ് ചെയ്തു" in draft or "ടെസ്റ്റ് കേസ് ടെസ്റ്റഡ്" in draft
    assert "ടെവെലപ്പര്‍" in draft
    assert "ഇത് ആണ് ടെസ്റ്റ്" in draft

def test_bug_fix():
    '''testing bug fix for issue #412'''
    tokens_abraham = [
      {
        "token": "अब्राहम से",
        "translations": [
          "Abraham"
        ],
        "metaData": {
          "for": "अब्राहम से"
        }
      },
      {
        "token": "अब्राहम की",
        "translations": [
          "Abraham's"
        ],
        "metaData": {
          "for": "अब्राहम की"
        }
      }
    ]
    response = client.post(NLP_UNIT_URL+'/learn/gloss?source_language=hi&target_language=en',
        headers=headers_auth, json=tokens_abraham)
    assert response.status_code == 201
    assert response.json()['message'] == "Added to glossary"    
    
    response = client.get(NLP_UNIT_URL+'/gloss?source_language=hi&target_language=en&token=अब्राहम से',
        headers=headers_auth)
    assert response.status_code ==200
    assert response.json()["token"] == "अब्राहम से"
    assert list(response.json()["translations"].keys())[0] == "Abraham".lower()
    assert response.json()["metaData"]["for"] == "अब्राहम से"

    response = client.get(NLP_UNIT_URL+'/gloss?source_language=hi&target_language=en&token=अब्राहम की',
        headers=headers_auth)
    assert response.status_code ==200
    assert response.json()["token"] == "अब्राहम की"
    assert list(response.json()["translations"].keys())[0] == "Abraham's".lower()
    assert response.json()["metaData"]["for"] == "अब्राहम की"

def test_metadata_to_same_gloss():
    '''testing metadata is added to the same token-translation pair'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.post(NLP_UNIT_URL+'/learn/gloss?source_language=en&target_language=ml',
        headers=headers_auth, json=tokens_trans)
    assert response.status_code == 201
    assert response.json()['message'] == "Added to glossary"

    response = \
        client.get(NLP_UNIT_URL+'/gloss-entries?source_language=en&target_language=ml&token=tested',
        headers=headers_auth)
    assert response.status_code ==200
    # Ensuring metadata is added to the correct token-translation pair - positive test
    assert response.json()[0]["token"] == "tested"
    assert response.json()[0]["translation"] == "ടെസ്റ്റഡ്"
    assert response.json()[0]["metaData"]["tense"] == "past"

    #Adding metadata in incorrect format
    tokens_test = [
    {"token":"test", "translations":["ടെസ്റ്റ്"],"metaData":"translations"}
    ]
    response = client.post(NLP_UNIT_URL+'/learn/gloss?source_language=en&target_language=ml',
        headers=headers_auth, json=tokens_test)
    assert response.status_code == 422
    assert response.json()['error'] == "Input Validation Error"

    #Adding a sentences and ensuring frequency is incremented for same token-translation pair
    response = \
        client.get(NLP_UNIT_URL+'/gloss-entries?source_language=en&target_language=ml&token=developer',
        headers=headers_auth)
    freq_before = response.json()[0]['frequency']
    align_data1 = [
        {
            "sourceTokenList": ["This","is","a","developer"],
            "targetTokenList": ["ഇത്", "ഒരു", "ടെവെലപ്പര്‍", "ആണ്"],
            "alignedTokens": [
            {"sourceTokenIndex": 0,"targetTokenIndex": 0},
            {"sourceTokenIndex": 1,"targetTokenIndex": 3},
            {"sourceTokenIndex": 2,"targetTokenIndex": 1},
            {"sourceTokenIndex": 3,"targetTokenIndex": 2}
            ]
        },
        {
            "sourceTokenList": ["Developer","is","happy"],
            "targetTokenList": ["ടെവെലപ്പര്‍","സന്തോഷവാന്‍", "ആണ്"],
            "alignedTokens": [
            {"sourceTokenIndex": 0,"targetTokenIndex": 0},
            {"sourceTokenIndex": 1,"targetTokenIndex": 2},
            {"sourceTokenIndex": 2,"targetTokenIndex": 1}
            ]
            }
    ]
    response = client.post(NLP_UNIT_URL+'/learn/alignment?source_language=en&target_language=ml',
        headers=headers_auth, json=align_data1)
    assert response.status_code == 201
    assert response.json()['message'] == "Alignments used for learning"
    response = \
        client.get(NLP_UNIT_URL+'/gloss-entries?source_language=en&target_language=ml&token=developer',
        headers=headers_auth)
    freq_after = response.json()[0]['frequency']
    assert freq_after == freq_before + 2

def test_update_glossary():
    '''Test the updation of translation and metadata fields of glossary'''

    # Adding glossary
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.post(NLP_UNIT_URL+'/learn/gloss?source_language=en&target_language=ml',
        headers=headers_auth, json=tokens_trans)
    assert response.status_code == 201
    assert response.json()['message'] == "Added to glossary"
    response = \
        client.get(NLP_UNIT_URL+'/gloss-entries?source_language=en&target_language=ml&token=tested',
        headers=headers_auth)
    assert response.status_code ==200

    # Ensuring metadata is added to the correct token-translation pair - positive test
    assert response.json()[0]["token"] == "tested"
    assert response.json()[0]["translation"] == "ടെസ്റ്റഡ്"
    assert response.json()[0]["metaData"]["tense"] == "past"
    token_id = response.json()[0]["tokenId"]
    data = {
        "tokenId": token_id,
        "token": "tested",
        "translation": "പരീക്ഷിക്കുന്നു",
        "metaData": {"tense": "present" }
        }
    # update without auth - negative test
    response = client.put(NLP_UNIT_URL+'/gloss',headers=headers, json=data)
    assert response.json()['error'] == "Authentication Error"
    assert response.status_code == 401

    #with auth - updating both translation and metadata - positive test
    response = client.put(NLP_UNIT_URL+'/gloss',headers=headers_auth, json=data)
    assert response.status_code ==200
    assert response.json()['message'] == 'Glossary Updated'
    assert response.json()['data']['token'] == "tested"
    assert response.json()['data']['translation'] == "പരീക്ഷിക്കുന്നു"
    assert response.json()['data']['metaData']['tense'] == "present"

    #updating translation only - positive test
    data =  {
        "tokenId": token_id,
        "token": "tested",
        "translation": "പരീക്ഷിക്കുന്നു"
        }
    response = client.put(NLP_UNIT_URL+'/gloss',headers=headers_auth, json=data)
    assert response.json()['data']['translation'] == "പരീക്ഷിക്കുന്നു"
    assert response.json()['data']['metaData'] == {}

    #updating  on invalid token - negative test
    data =  {
        "tokenId": 9999,
        "token": "tested",
        "translation": "പരീക്ഷിക്കുന്നു",
         "metaData": {"tense": "present"}
        }
    response = client.put(NLP_UNIT_URL+'/gloss',headers=headers_auth, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"

    #updating  metadata in incorrect format - negative test
    data =  {
        "tokenId": token_id,
        "token": "tested",
        "translation": "പരീക്ഷിക്കുന്നു",
         "metaData": "tense"
        }
    response = client.put(NLP_UNIT_URL+'/gloss',headers=headers_auth, json=data)
    assert response.status_code == 422
    assert response.json()['error'] == "Input Validation Error"

def test_delete_glossary():
    '''Test the removal of a suggestion/glossary'''

    #Adding a suggestion for translation
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.post(NLP_UNIT_URL+'/learn/gloss?source_language=en&target_language=ml',
        headers=headers_auth, json=tokens_trans)
    assert response.status_code == 201
    assert response.json()['message'] == "Added to glossary"

    # Check glossary is added
    response = client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=test',
    headers=headers_auth)
    assert response.status_code ==200
    assert isinstance(response.json(), dict)
    assert len(response.json()['translations']) > 0
    assert_positive_get_suggetion(response.json())
    found_test = False
    for item in response.json()['translations']:
        if item == "ടെസ്റ്റ്":
            found_test = True
    assert found_test

    #deleting glossary with no auth - Negative Test
    resp = client.delete(NLP_UNIT_URL+
        '/gloss?source_lang=en&target_lang=ml&token=test&translation=ടെസ്റ്റ്',
             headers=headers)
    assert resp.status_code == 401
    assert resp.json()['details'] == "Access token not provided or user not recognized."

    #Deleting glossary with different auth of registerdUser - Positive Test
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.delete(NLP_UNIT_URL+
        '/gloss?source_lang=en&target_lang=ml&token=test&translation=ടെസ്റ്റ്',
        headers=headers_auth)
    assert response.status_code == 201
    assert "successfull" in response.json()['message']

    # Ensure deleted glossary is not present
    get_response =client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=test',
                headers=headers_auth)
    assert get_response.status_code == 200
    assert isinstance(get_response.json(), dict)
    assert len(get_response.json()['translations']) == 0

    #Create and Delete glossary with superadmin - Positive test
    # Login as Super Admin
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth['Authorization'] = "Bearer"+" "+test_user_token
    response = client.post(NLP_UNIT_URL+'/learn/gloss?source_language=en&target_language=ml',
        headers=headers_auth, json=tokens_trans)
    response = client.delete(NLP_UNIT_URL+
        '/gloss?source_lang=en&target_lang=ml&token=test&translation=ടെസ്റ്റ്',
        headers=headers_auth)
    assert response.status_code == 201
    assert "successfull" in response.json()['message']

    # Ensure deleted sentence is not present
    get_response =client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=test',
                headers=headers_auth)
    assert get_response.status_code == 200
    assert isinstance(get_response.json(), dict)
    assert len(get_response.json()['translations']) == 0

    #Delete with not available source language
    response = client.delete(NLP_UNIT_URL+
        '/gloss?source_lang=x-ttt&target_lang=ml&token=test&translation=ടെസ്റ്റ്',
        headers=headers_auth)
    assert response.status_code == 404
    assert "Source language not available" in response.json()['details']

     #Delete not available target language
    response = client.delete(NLP_UNIT_URL+
        '/gloss?source_lang=en&target_lang=x-ttt&token=test&translation=ടെസ്റ്റ്',
        headers=headers_auth)
    assert response.status_code == 404
    assert "Target language not available" in response.json()['details']
    logout_user(test_user_token)


def test_restore_glossary():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Adding a suggestion for translation
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.post(NLP_UNIT_URL+'/learn/gloss?source_language=en&target_language=ml',
        headers=headers_auth, json=tokens_trans)
    # Deleting
    delete_resp = client.delete(NLP_UNIT_URL+
        '/gloss?source_lang=en&target_lang=ml&token=test&translation=ടെസ്റ്റ്',
        headers=headers_auth)

    # Ensure deleted glossary is not present
    get_response =client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=test',
                headers=headers_auth)
    assert get_response.status_code == 200
    assert isinstance(get_response.json(), dict)
    assert len(get_response.json()['translations']) == 0

    deleteditem_id = delete_resp.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring data
    #Restore glossary without authentication - Negative Test
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore glossary with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev-Negative Test
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev']:
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users[user]['token']
        response = client.put(RESTORE_URL, headers=headers_auth, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Restore glossary with Super Admin - Positive Test
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

    # Check glossary is restored
    response = client.get(NLP_UNIT_URL+'/gloss?source_language=en&target_language=ml&token=test',
    headers=headers_auth)
    assert response.status_code ==200
    assert isinstance(response.json(), dict)
    assert len(response.json()['translations']) > 0
    assert_positive_get_suggetion(response.json())
    found_test = False
    for item in response.json()['translations']:
        if item == "ടെസ്റ്റ്":
            found_test = True
    assert found_test

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
