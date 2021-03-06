import pytest
import requests
import json

@pytest.fixture
def url():
	# GET API
	return "https://stagingapi.autographamt.com/v1/autographamt/projects"

data = [
	('alex@yopmail.com', '1189'),                # admin role
	('joelcjohnson123@gmail.com', '111111'),     # super admin role
	('ag2@yopmail.com', '1189')                  # user role
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


# ----------------- List projects for admin role----------------#
@pytest.mark.parametrize('data',[data])
def test_projectlist_admin(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance (out,list)


# ----------------- List projects for superadmin role----------------#
@pytest.mark.parametrize('data',[data])
def test_projectlist_su(url, data):
	access_token = get_accesstoken(data[1][0], data[1][1])
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance (out,list)


# ----------------- List projects for normal role----------------#
@pytest.mark.parametrize('data',[data])
def test_projectlist(url, data):
	access_token = get_accesstoken(data[2][0], data[2][1])
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == 'Not authorized'

