import pytest
import requests
import json

@pytest.fixture
def url():
	# POST API for all roles
	return "https://stagingapi.autographamt.com/v1/autographamt/organisations"


data = [
	('joelcjohnson123@gmail.com', '111111')   
]

def orglist():
	data1 = [
			('bcvs2','asj','21212','abcg2@gmail.com'),   # new organisation details
			('bcs232','asj','21212','abcg2@gmail.com'),  # already exists organisation
			('bascs2332','','21212',''),                    # new organisation empty values
			('bascs232','','','')                          # existing organisation with empty values
	]
	return data1

def jsondump(data1):
	jsondump = {'organisationName': data1[0],
				'organisationAddress': data1[1],
				'organisationPhone': data1[2],
				'organisationEmail': data1[3]
	}
	return(jsondump)


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


# ----------------- create new Organisation ----------------#
@pytest.mark.skip(reason="need to change the values")
@pytest.mark.parametrize('data',[data])
def test_createorganisations(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	org = orglist()
	jsondata = jsondump(org[0])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert out['success'] == True
	assert out['message'] == "Organisation request sent"


# ----------------- create existing Organisation ----------------#
@pytest.mark.parametrize('data',[data])
def test_createorganisationsex(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	org = orglist()
	jsondata = jsondump(org[1])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert out['success'] == False
	assert out['message'] == 'Organisation already created'


# ----------------- create new Organisation with empty values----------------#
@pytest.mark.parametrize('data',[data])
def test_createorganisationsempty(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	org = orglist()
	jsondata = jsondump(org[2])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	print(out)
	assert out['success'] == False
	assert out['message'] == 'Organisation already created'


# # ----------------- create existing Organisation with empty values----------------#
# @pytest.mark.parametrize('data',[data])
# def test_createorganisationsempty1(url, data):
# 	access_token = get_accesstoken(data[0][0], data[0][1])
# 	org = orglist()
# 	jsondata = jsondump(org[3])
# 	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
# 	out = json.loads(resp.text)
# 	assert out['success'] == False
# 	assert out['message'] == 'Organisation already created'

