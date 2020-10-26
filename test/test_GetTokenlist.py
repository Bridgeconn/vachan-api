#-*-coding:utf-8-*-
import pytest
import requests
import json

@pytest.fixture
# GET API
def url():
	return "https://stagingapi.autographamt.com/v1/tokenlist/35/2ti"


# ----------------- get token list------------------#
def test_GetTokenList(url):
	resp = requests.get(url)
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance (out,list)

