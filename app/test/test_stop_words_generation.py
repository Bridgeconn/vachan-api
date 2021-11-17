'''Tests the translation APIs that do need projects available in DB'''

from . import client
from . import check_default_get
from . import assert_not_available_content

UNIT_URL = '/v2/lookup/stopwords'
headers = {"contentType": "application/json", "accept": "application/json"}

def assert_positive_get_stopwords(item):
    '''Check for the properties in the normal return object'''
    assert "stopword" in item
    assert "stopwordType" in item
    assert "confidence" in item
    assert "active" in item

def test_get_default():
    '''positive test case, without optional params'''
    check_default_get(UNIT_URL+'/hi', assert_positive_get_stopwords)    

def test_get_stop_words():
    '''Positve tests for get stopwords API'''
    default_response = client.get(UNIT_URL+'/hi?', headers=headers) 
    assert default_response.status_code == 200
    assert isinstance(default_response.json(), list)
    for item in default_response.json():
        assert_positive_get_stopwords(item)
        if item["stopwordType"] in ["system defined", "user defined"]:
            assert item["confidence"] is None
        if item["stopwordType"] == "auto generated":
            assert isinstance(item["confidence"], float) 

    response = client.get(UNIT_URL+'/hi?include_system_defined=False', headers=headers) 
    assert response.status_code == 200
    sw_types = set([sw_dic['stopwordType'] for sw_dic in response.json()])
    assert "system defined" not in sw_types

    response = client.get(UNIT_URL+'/hi?include_user_defined=False', headers=headers) 
    assert response.status_code == 200
    sw_types = set([sw_dic['stopwordType'] for sw_dic in response.json()])
    assert "user defined" not in sw_types

    response = client.get(UNIT_URL+'/hi?include_auto_generated=False', headers=headers) 
    assert response.status_code == 200
    sw_types = set([sw_dic['stopwordType'] for sw_dic in response.json()])
    assert "auto generated" not in sw_types

    response = client.get(UNIT_URL+'/hi?only_active=True', headers=headers) 
    assert response.status_code == 200
    out = set([sw_dic['active'] for sw_dic in response.json()])
    assert False not in out        

def test_get_notavailable_code():
    ''' request a not available language_code'''
    response = client.get(UNIT_URL+"/abc")
    assert_not_available_content(response)            