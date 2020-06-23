  # -- coding: utf - 8 --
import pytest
import requests
import json

@pytest.fixture
# GET API
def url():
	return "https://stagingapi.autographamt.com/v1/concordances/35/2ti/करो"


# ---------------------list concordance-------------------#
def test_generateconcordance(url):
	resp = requests.get(url)
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance (out, dict)



	
