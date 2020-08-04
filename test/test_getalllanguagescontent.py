import pytest
import requests
import json

@pytest.fixture
# GET API
def url():
	return "https://stagingapi.autographamt.com/v1/languages/"


# -----------------get all languages for content id--------------#
def test_GetalllanguageswithcontentID_1(url):
	resp = requests.get(url+str(1))
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance(out,list)


# -----------------get all languages for unknown content id--------------#
def test_GetalllanguageswithcontentID_2(url):
	resp = requests.get(url+str(26))
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == "No languages available for this content", str(j)


  
