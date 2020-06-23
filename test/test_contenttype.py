import pytest
import requests
import json

@pytest.fixture
def url():
	return "https://stagingapi.autographamt.com/v1/contenttypes"


def test_Contenttype_1(url):
	resp = requests.get(url)
	out = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(out, list)
  
  
