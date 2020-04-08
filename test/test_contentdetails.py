import pytest
import requests
import json

@pytest.fixture
def url():
	return "https://stagingapi.autographamt.com/v1/contentdetails"


# ------------------list content id and conent type-----------------#
def test_Contentdetails(url):
	resp = requests.get(url)
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance(out,list)

  