import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

@pytest.fixture
def get_accessToken():
	email = "kavitharaju18@gmail.com"
	password = "111111"
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

@pytest.mark.parametrize("email, password",[("kavitharaju18@gmail.com",'111111')])
def test_list_valid_user(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert "accessToken" in j, "success="+str(j['success'])+j['message']


@pytest.mark.parametrize("email, password",[('kavitharaju18@gmail.com',"letme")])
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

## GET method with access token
def test_getusers(supply_url,get_accessToken):
	url = supply_url + '/v1/autographamt/users'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	assert 'roleId' in j[0], j[0]
	assert 'firstName' in j[0], j[0]

## POST method with access token

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs2','Delhi','000','kavitharaju18@gmail.com')])
def test_createOrg(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Organisation request sent", str(j)
