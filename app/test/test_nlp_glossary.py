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
        assert key in ['token', 'translation', 'frequency', 'metaData']

def check_post(src, trg, data, headers):
    '''common steps for positive post test cases'''
    response = client.post(POST_URL+\
        f"?source_language={src}&target_language={trg}", headers=headers, json=data)
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

    GET_URL = GET_LIST_URL+f"?source_language={src_lang}&target_language={trg_lang}"

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
