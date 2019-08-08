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

@pytest.mark.parametrize("password",[('1189'),('221189')])
def test_list_no_email(supply_url,password):
	resp = check_login (supply_url,email)
	j = json.loads(resp.txt)
	assert resp.status_code == 400, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "enter the password", 'message='+j['message']
