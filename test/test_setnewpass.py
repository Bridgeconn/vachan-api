import pytest
import requests
import json

@pytest.fixture
def url():
	return "https://stagingapi.autographamt.com"

def setnewpass(temporaryPassword,password):
	url = "https://stagingapi.autographamt.com" + "/v1/forgotpassword"
	data = {'temporaryPassword':temporaryPassword,
            'password': password
            }
	resp = requests.post(url, data=data)
	return resp

def test_setnewpass_load():
	url = "https://staging.autographamt.com/forgotpassword"
	resp = requests.get(url)
	assert resp.status_code == 200, resp.text

@pytest.mark.parametrize("temporaryPassword,password",[("363588","111111")])
def test_setnewpass_success(temporaryPassword,password):
	resp = setnewpass(temporaryPassword,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, request.text
	assert j['success'] == True,str(j['success'])
	assert j['message'] == "Password has been reset. Login with the new password.",str(j['message'])

@pytest.mark.parametrize("temporaryPassword,password",[("8646040","221189")])
def test_setnewpass_fail(temporaryPassword,password):
	resp = setnewpass(temporaryPassword,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, request.text
	assert j['success'] == False,str(j['success'])
	assert j['message'] == "Invalid temporary password.",str(j['message'])