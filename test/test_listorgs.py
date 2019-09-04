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

@pytest.mark.parametrize("email, password",[("savitha.mark@bridgeconn.com",'221189')])
def test_list_valid_user(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert "accessToken" in j, "success="+str(j['success'])+j['message']


@pytest.mark.parametrize("email, password",[('savitha.mark@bridgeconn.com',"letme")])
def test_list_invalid_password(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "Incorrect Password", 'message='+j['message']

@pytest.mark.parametrize("email, password",[('savithaa.mark@bridgeconn.com',"221189")])
def test_list_invalid_email(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	print(j)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "This email is not registered", 'message='+j['message']

# GET method with access token
def test_getlistorg(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	print(j)
	assert resp.status_code == 200, resp.text
	assert isinstance (j,list), j
	assert 'organisationId' in j[0], j[0]
	assert 'organisationName' in j[0], j[0]
	assert 'organisationAddress' in j[0], j[0]
	assert 'organisationPhone' in j[0], j[0]
	assert 'organisationEmail' in j[0], j[0] 
	assert 'verified' in j[0], j[0]
	assert 'userId' in j[0], j[0]
	
# 	## GET method with access token
def test_getlistorgw(supply_url,get_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	print(j)
	assert resp.status_code == 200, resp.text
	assert isinstance (j,list), j
	assert 'organisationId' in j[0], j[0]
	assert 'organisationName' in j[0], j[0]
	assert 'organisationAddress' in j[0], j[0]
	assert 'organisationPhone' in j[0], j[0]
	assert 'organisationEmail' in j[0], j[0] 
	assert 'verified' in j[0], j[0]
	assert 'userId' in j[0], j[0]
	
