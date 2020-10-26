import pytest
import requests
import json

@pytest.fixture
def url():
	# GET API
	return "https://stagingapi.autographamt.com/v1/languages"


# ----------------- get all language list------------------#
def test_getLanguageList(url):
	resp = requests.get(url)
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance (out,list)

