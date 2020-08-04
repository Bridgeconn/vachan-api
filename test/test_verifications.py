import pytest
import requests
import json

@pytest.fixture
def url():
	# GET API
	return "https://stagingapi.autographamt.com/v1/verifications/"


data = [
	('34399b9399ce46a4a5aa4453088d0a6b '),  # valid code
	('34399b9312ce46a4a2aa4453082d0a6b ')   # invalid code
]

# -------------------- Check page --------------------#
def test_pageload():
	resp = requests.get("https://staging.autographamt.com/signup")
	assert resp.status_code == 200

# ----------------------- validating verification code --------------------#
@pytest.mark.parametrize('data', [data[1]])
def test_validcode(url, data):
	resp = requests.get(url+data)
	out = resp.text
	assert resp.status_code == 200


# NEED TO CHECK AGAIN