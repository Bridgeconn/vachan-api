 # -- coding: utf - 8 --

import pytest
import requests
import json

@pytest.fixture
def url():
	# GET API 
	return "https://stagingapi.autographamt.com/v1/autographamt/projects/translations/अंकुर/45"



# --------------------- checking token translation --------------------#
def test_projectTranslation(url):
	resp = requests.get(url)
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == "No Translation or sense available for this token"
