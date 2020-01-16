import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

def test_GetalllanguageswithcontentID_1(supply_url):
	url = supply_url + '/v1/languages/1'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	assert 'languageCode' in j[0], j[0]
	assert 'languageId' in j[0], j[0]
	print(j)
    # assert 'languageName'in j[0], j[0]
	
def test_GetalllanguageswithcontentID_2(supply_url):
	url = supply_url + '/v1/languages/6'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "No languages available for this content", str(j)


  
