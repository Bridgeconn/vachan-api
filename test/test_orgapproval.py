import pytest
import requests
import json

@pytest.fixture
def url():
	# POST API
	return "https://stagingapi.autographamt.com/v1/autographamt/approvals/organisations"


data = [
	('alex@yopmail.com', '1189'),                # admin role
	('joelcjohnson123@gmail.com', '111111'),     # super admin role
	('ag2@yopmail.com', '1189')                  # normal role
]


def orglist():
	data1 = [
			(26, True)   # new organisation details
	]
	return data1

def jsondump(data1):
	jsondump = {'organisationId': data1[0],
				'verified': data1[1]
	}
	return(jsondump)


# ------------------------- get access token --------------------------- #
def get_accesstoken(email, password):
	auth_url = 'https://stagingapi.autographamt.com/v1/auth'
	resp = requests.post(auth_url, {'email': email, 'password': password})
	out = json.loads(resp.text)
	token = out['accessToken']
	return token


# ------------------ organisation approval with admin role---------------# 
@pytest.mark.parametrize('data',[data])
def test_organisationapprov(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	org = orglist()
	jsondata = jsondump(org[0])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert out['success'] == False
	assert out['message'] == "Unauthorized"


# ------------------ organisation approval with super-admin role---------------# 
@pytest.mark.parametrize('data',[data])
def test_organisationapprov1(url, data):
	access_token = get_accesstoken(data[1][0], data[1][1])
	org = orglist()
	jsondata = jsondump(org[0])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert out['success'] == True
	assert out['message'] == "Role Updated"


# ------------------ organisation approval with normal role---------------# 
@pytest.mark.parametrize('data',[data])
def test_organisationapprov2(url, data):
	access_token = get_accesstoken(data[2][0], data[2][1])
	org = orglist()
	jsondata = jsondump(org[0])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert out['success'] == False
	assert out['message'] == "Unauthorized"