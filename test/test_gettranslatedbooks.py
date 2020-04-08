import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

def test_getTranslatedbookssup(supply_url):
	url = supply_url + '/v1/translatedbooks/35/18'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j

  
