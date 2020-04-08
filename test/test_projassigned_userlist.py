import pytest
import requests
import json

@pytest.fixture
def url():
	# GET API for all roles
	return "https://stagingapi.autographamt.com/v1/autographamt/projects/assignments/"

data = [
	('joelcjohnson123@gmail.com', '111111')     # super admin role
]

# ------------------------- get access token --------------------------- #
def get_accesstoken(email, password):
	auth_url = 'https://stagingapi.autographamt.com/v1/auth'
	resp = requests.post(auth_url, {'email': email, 'password': password})
	out = json.loads(resp.text)
	token = out['accessToken']
	return token


# -------------------- Check page --------------------#
def test_pageload():
	resp = requests.get("https://staging.autographamt.com")
	assert resp.status_code == 200


# ----------------- List users assigned under a project----------------#
@pytest.mark.parametrize('data',[data])
def test_listusers(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	resp = requests.get(url+str(35),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance (out,list)


# ----------------- List users assigned under a unknow project----------------#
@pytest.mark.parametrize('data',[data])
def test_listusers(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	resp = requests.get(url+str(55),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance (out,list)
	assert out == []

