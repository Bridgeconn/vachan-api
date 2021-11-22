'''Tests the translation APIs that do need projects available in DB'''
from . import client
from . import check_default_get
from . import assert_not_available_content

UNIT_URL = '/v2/lookup/stopwords'
headers = {"contentType": "application/json", "accept": "application/json"}

update_obj1 = {
        "stopWord": "कहता",
        "active": False,
        "metaData": {
        "type": "verb"
     }
    }
update_obj2 = {
        "stopWord": "गए",
        "active": False,
    }
update_wrong_obj =  {
        "stopWord": "prayed",
        "active": False,
        "metaData": {
        "type": "verb"
     }
    }

def assert_positive_get_stopwords(item):
    '''Check for the properties in the normal return object'''
    assert "stopWord" in item
    assert "stopwordType" in item
    if item["stopwordType"] == "auto generated":
        assert "confidence" in item
        assert isinstance(item["confidence"], float)
    assert "active" in item

def test_get_default():
    '''positive test case, without optional params'''
    check_default_get(UNIT_URL+'/hi', assert_positive_get_stopwords)

def assert_positive_update_stopwords(out):
    '''Check the properties in the update response'''
    assert "message" in out
    assert "data" in out

def test_get_stop_words():
    '''Positve tests for get stopwords API'''
    default_response = client.get(UNIT_URL+'/hi?', headers=headers)
    assert default_response.status_code == 200
    assert isinstance(default_response.json(), list)
    for item in default_response.json():
        assert_positive_get_stopwords(item)

    response = client.get(UNIT_URL+'/hi?include_system_defined=False', headers=headers)
    assert response.status_code == 200
    sw_types = {sw_dic['stopwordType'] for sw_dic in response.json()}
    assert "system defined" not in sw_types

    response = client.get(UNIT_URL+'/hi?include_user_defined=False', headers=headers)
    assert response.status_code == 200
    sw_types = {sw_dic['stopwordType'] for sw_dic in response.json()}
    assert "user defined" not in sw_types

    response = client.get(UNIT_URL+'/hi?include_auto_generated=False', headers=headers)
    assert response.status_code == 200
    sw_types = {sw_dic['stopwordType'] for sw_dic in response.json()}
    assert "auto generated" not in sw_types

    response = client.get(UNIT_URL+'/hi?only_active=True', headers=headers)
    assert response.status_code == 200
    out = {sw_dic['active'] for sw_dic in response.json()}
    assert False not in out

def test_get_notavailable_code():
    ''' request a not available language_code'''
    response = client.get(UNIT_URL+"/abc")
    assert_not_available_content(response)

def test_update_stopword():
    '''Positve tests for update stopwords API'''
    response = client.put(UNIT_URL+'/hi?',headers=headers, json=update_obj1)
    assert response.status_code == 200
    assert_positive_update_stopwords(response.json())
    assert_positive_get_stopwords(response.json()['data'])
    assert response.json()['message'] == "Stopword info updated successfully"

    response = client.put(UNIT_URL+'/hi?',headers=headers, json=update_obj2)
    assert response.status_code == 200
    assert_positive_update_stopwords(response.json())
    assert_positive_get_stopwords(response.json()['data'])
    assert response.json()['message'] == "Stopword info updated successfully"

    response = client.put(UNIT_URL+'/hi?',headers=headers, json=update_wrong_obj)
    assert response.status_code == 404
