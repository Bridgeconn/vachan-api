'''Test cases for Glossary related APIs'''
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_auth_basic import login,SUPER_USER,SUPER_PASSWORD,logout_user
from .conftest import initial_test_users

src_lang = "en"
trg_lang = "aa"

POST_URL = '/v2/nlp/learn/gloss'
GET_LIST_URL = "/v2/nlp/gloss-entries"
GET_COUNT_URL = '/v2/nlp/gloss-entries/count'

gloss_data = [
    {"token":"love", "translations":["love"]},
    {"token":"happy", "translations":["happy"]},
    {"token":"joy", "translations":["happy"]},
    {"token":"smile", "translations":["happy", "face"]},
    {"token":"love", "translations":["love-2"]},
]

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "token" in item
    assert "translation" in item
    for key in item:
        assert key in ['tmID', 'token', 'translation', 'frequency', 'metaData']

def check_post(src, trg, data, headers):
    '''common steps for positive post test cases'''
    response = client.post(POST_URL+\
        f"?resource_language={src}&target_language={trg}", headers=headers, json=data)
    assert response.status_code == 201
    assert "added" in response.json()['message'].lower()

def test_get_gloss_entries():
    '''Happy path testing for glossary list/translation meory list'''
    headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser']['token']
            }
    # upload data before GET call
    check_post(src_lang, trg_lang, gloss_data, headers_auth)

    GET_URL = GET_LIST_URL+f"?resource_language={src_lang}&target_language={trg_lang}"

    check_default_get(GET_URL, headers_auth, assert_positive_get)

    # with all registered users
    for user in ['APIUser', 'APIUser2', "BcsDev", "AgAdmin", "AgUser", "VachanUser", "VachanAdmin"]:
        headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
                }

        resp = client.get(GET_URL, headers=headers_auth)
        assert resp.status_code == 200
        for item in resp.json():
            assert_positive_get(item)
        assert len(resp.json()) >= 5

    # with filter for token
    headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser']['token']
            }
    resp = client.get(GET_URL+"&token=love", headers=headers_auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    for item in resp.json():
        assert item['token'] == "love"

def test_get_gloss_count():
    '''Test cases to count all glossary records and count unique tokens in translation memory'''
    headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                'Authorization': "Bearer"+" "+initial_test_users['APIUser']['token']
            }
    # upload data before GET call
    check_post(src_lang, trg_lang, gloss_data, headers_auth)

    GET_URL = GET_COUNT_URL+f"?resource_language={src_lang}&target_language={trg_lang}"

    # Without authentication - Negative Test
    headers = {"contentType": "application/json", "accept": "application/json"}
    resp = client.get(GET_URL, headers=headers)
    assert resp.status_code == 401
    assert resp.json()['error'] == 'Authentication Error'

    # With all registered users - Positive Test
    for user in ['APIUser', 'APIUser2', "BcsDev", "AgAdmin", "AgUser", "VachanUser", "VachanAdmin"]:
        headers_auth = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
                }

        # Without filter of token - Positive Test
        response = client.get(GET_URL,headers=headers_auth)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert len(response.json()) == 2
        assert "tokenTranslationCount" in response.json()
        assert "tokenCount" in response.json()
        assert response.json()['tokenTranslationCount'] == 6
        assert response.json()['tokenCount'] == 4

    # With filter for token - Positive Test
    resp = client.get(GET_URL+"&token=love", headers=headers_auth)
    assert resp.status_code == 200
    assert resp.json()['tokenTranslationCount'] == 2
    # Validate tokenCount
    assert resp.json()['tokenCount'] == 1

    # With notavailable token - Negative Test
    resp = client.get(GET_URL+"&token=ttt", headers=headers_auth)
    assert resp.status_code == 200
    assert resp.json()['tokenTranslationCount'] == 0
    assert resp.json()['tokenCount'] == 0

    # With notavailable resource language - Negative Test
    GET_URL = GET_COUNT_URL+f"?resource_language=x-ttt&target_language={trg_lang}"
    resp = client.get(GET_URL,headers=headers_auth)
    assert resp.status_code == 404
    assert resp.json()['error'] == 'Requested Content Not Available'

    # With notavailable target language - Negative Test
    GET_URL = GET_COUNT_URL+f"?resource_language={src_lang}&target_language=x-ttt"
    resp = client.get(GET_URL,headers=headers_auth)
    assert resp.status_code == 404
    assert resp.json()['error'] == 'Requested Content Not Available'
