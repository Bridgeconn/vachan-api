import pytest
import requests
import json

@pytest.fixture
def url():
	# GET API
	return "https://stagingapi.autographamt.com/v1/autographamt/users/projects"


data = [
	('joelcjohnson123@gmail.com', '111111'),   # user which has projects assigned
	('none@gmail.com', 'none')                 # user which has empty projects
]


# ------------------------- get access token --------------------------- #
def get_accesstoken(email, password):
	auth_url = 'https://stagingapi.autographamt.com/v1/auth'
	resp = requests.post(auth_url, {'email': email, 'password': password})
	out = json.loads(resp.text)
	token = out['accessToken']
	return token


# ----------------- List user projects----------------#
@pytest.mark.parametrize('data',[data])
def test_organisationList_admin(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance (out,list)



# ----------------- if no projects available----------------#
@pytest.mark.skip(reason="need to add the values")
@pytest.mark.parametrize('data',[data])
def test_organisationList_admin(url, data):
	access_token = get_accesstoken(data[1][0], data[1][1])
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == "No projects assigned"

