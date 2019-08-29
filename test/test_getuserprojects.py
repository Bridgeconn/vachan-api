import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

@pytest.fixture
def get_accessToken():
	email = "alex@yopmail.com"
	password = "1189"
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token

@pytest.fixture
def get_accessTokenw():
	email = "ag2@yopmail.com"
	password = "1189"
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token


@pytest.fixture
def get_supAdmin_accessToken():
	email = 'savitha.mark@bridgeconn.com'
	password = '221189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token


def check_login(url,email,password):
	url = url + "/v1/auth" 
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	return resp

def test_firstpage_load():
	url = "https://staging.autographamt.com"
	resp = requests.get(url)
	assert resp.status_code == 200, resp.text

@pytest.mark.parametrize("email, password",[("alex@yopmail.com",'1189')])
def test_list_valid_user(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert "accessToken" in j, "success="+str(j['success'])+j['message']

@pytest.mark.parametrize("email, password",[("ag2@yopmail.com",'1189')])
def test_list_valid_userk(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert "accessToken" in j, "success="+str(j['success'])+j['message']

@pytest.mark.parametrize("email, password",[('ag27@yopmail.com',"letme")])
def test_list_invalid_password(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "Incorrect Password", 'message='+j['message']

@pytest.mark.parametrize("email, password",[('kavitharaju@gmail.com',"letme"),('kavitharaju@bridgeconn.com',"letme")])
def test_list_invalid_email(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "This email is not registered", 'message='+j['message']

@pytest.mark.parametrize("email, password",[('kavitha.raju@bridgeconn.com',"letmepass")])
def test_list_notverified_email(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "Email is not Verified", 'message='+j['message']

## GET method with access token for list users
def test_getUserProjects(supply_url,get_accessToken):
	url = supply_url + '/v1/autographamt/users/projects'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	assert 'projectId' in j[0], j[0]
	assert 'projectName' in j[0], j[0]
    # assert 'organisationName' in j[0], j[0]
    # assert 'books' in j[0], j[0]
    # assert 'targetID' in j[0], j[0]
    # assert 'version' in j[0], j[0]
    # assert 'organisationName' in j[0], j[0]
    # assert 'books' in j[0], j[0]
    # assert 'sourceId' in j[0], j[0]
    # assert 'targetId' in j[0], j[0]
    # assert 'version' in j[0], j[0]

def test_getusersw(supply_url,get_accessTokenw):
	url = supply_url + '/v1/autographamt/users/projects'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_accessTokenw)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	assert 'projectId' in j[0], j[0]
	assert 'projectName' in j[0], j[0]
