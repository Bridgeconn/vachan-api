import pytest
import requests
import json

@pytest.fixture
def url():
	return "https://stagingapi.autographamt.com"

def forgotpassword(temporaryPassword,password):
	url = "https://stagingapi.autographamt.com" + "/v1/forgotpassword"
	data = {'temporaryPassword':temporaryPassword,
            'password': password
            }
	resp = requests.post(url, data=data)
	return resp
	
@pytest.mark.parametrize("temporaryPassword,password",[("363588","111111")])
def test_setnewpass_success(temporaryPassword,password):
	resp = forgotpassword(temporaryPassword,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, request.text
	assert j['success'] == True,str(j['success'])
	assert j['message'] == "Password has been reset. Login with the new password.",str(j['message'])

@pytest.mark.parametrize("temporaryPassword,password",[("8646040","221189")])
def test_setnewpass_fail(temporaryPassword,password):
	resp = forgotpassword(temporaryPassword,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, request.text
	assert j['success'] == False,str(j['success'])
	assert j['message'] == "Invalid temporary password.",str(j['message'])