import pytest
import requests
import json

@pytest.fixture
def url():
	# POST API 
	return "https://stagingapi.autographamt.com/v1/autographamt/organisations/projects"


data = [
	('joelcjohnson123@gmail.com', '111111'),     # super admin role
	('ag2@yopmail.com', '1189')                  # user role  
]

def projectdetails():
	data1 = [
			(56,3929,26),   # create new project
			(56,3702,26),   # create existing project
			(56,3702,'')    # create project with empty values
	]
	return data1

def jsondump(data1):
	jsondump = {'sourceId': data1[0],
				'targetLanguageId': data1[1],
				'organisationId': data1[2]
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


# ----------------- create new project with su-admin role----------------#
@pytest.mark.skip(reason="need to change the values")
@pytest.mark.parametrize('data',[data])
def test_create_newproject(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	proj = projectdetails()
	jsondata = jsondump(proj[0])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == True
	assert out['message'] == 'Project created'


# ----------------- create existing project with su-admin role----------------#
@pytest.mark.parametrize('data',[data])
def test_create_existproject(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	proj = projectdetails()
	jsondata = jsondump(proj[1])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == 'Project already created'


# ----------------- create project with empty values----------------#
@pytest.mark.parametrize('data',[data])
def test_create_project_empty(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	proj = projectdetails()
	jsondata = jsondump(proj[2])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == 'Server Error'


# ----------------- create project with user role----------------#
@pytest.mark.parametrize('data',[data])
def test_create_project_usr(url, data):
	access_token = get_accesstoken(data[1][0], data[1][1])
	proj = projectdetails()
	jsondata = jsondump(proj[1])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == 'UnAuthorized'

