import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

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

@pytest.mark.parametrize("email, password",[('savitha.mark@bridgeconn.com',"221189"),('ag2@yopmail.com',"1189")])
def test_list_valid_user(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert "accessToken" in j, "success="+str(j['success'])+j['message']

@pytest.mark.parametrize("email, password",[('',"")])
def test_list_valid_usernep(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])

@pytest.mark.parametrize("email, password",[('alex@yopmail.com',"ljkkj"),('savitha.mark@bridgeconn.com',"letme")])
def test_list_invalid_password(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "Incorrect Password", 'message='+j['message']

@pytest.mark.parametrize("email, password",[('ahrg@yop.mail.com',"letme"),('savita@gmail.com',"rgrwg")])
def test_list_invalid_email(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "This email is not registered", 'message='+j['message']

@pytest.mark.parametrize("email, password",[('ag4@yopmail.com',"1189"),('kavitha.raju@bridgeconn.com',"letmepass")])
def test_list_notverified_email(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "Email is not Verified", 'message='+j['message']

@pytest.mark.parametrize("email,password",[('',"1189"),(' ',"221189")])
def test_list_no_password(supply_url,email,password):
	resp = check_login (supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])

@pytest.mark.parametrize("email,password",[('savitha.mark@bridgeconn.com'," "),('ag3@yopmail.com'," ")])
def test_list_no_password(supply_url,email,password):
	resp = check_login (supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])