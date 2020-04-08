import pytest
import requests
import json

@pytest.fixture
def url():
	# GET API
	return "https://stagingapi.autographamt.com/v1/sources/books/"


data = [
	('joelcjohnson123@gmail.com', '111111'),     # super admin role
]


# ------------------------- get access token --------------------------- #
def get_accesstoken(email, password):
	auth_url = 'https://stagingapi.autographamt.com/v1/auth'
	resp = requests.post(auth_url, {'email': email, 'password': password})
	out = json.loads(resp.text)
	token = out['accessToken']
	return token


# ----------------- List available books----------------#
@pytest.mark.parametrize('data',[data])
def test_availablebooks(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	resp = requests.get(url+str(45),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200 
	assert isinstance (out,list)


# ----------------- List books with unknow source id----------------#
@pytest.mark.parametrize('data',[data])
def test_availablebooks1(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	resp = requests.get(url+str(425),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200 
	assert out['success'] == False
	assert out['message'] == "No data available"
