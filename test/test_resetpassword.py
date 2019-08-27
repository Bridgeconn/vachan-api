import pytest
import requests
import json

@pytest.fixture
def url():
	return "https://stagingapi.autographamt.com"

def restpass(url,email):
	url = url + "/v1/resetpassword" 
	data = {'email':email}
	resp = requests.post(url, data=data)
	return resp

def test_restpass_load():
	url = "https://staging.autographamt.com/"
	resp = requests.get(url)
	assert resp.status_code == 200, resp.text

@pytest.mark.parametrize("email",[('ag2@yopmail.com')])
def test_restpass_success(url,email):
	resp = restpass(url,email)
	j = json.loads(resp.text)
	assert resp.status_code == 200, request.text
	assert j['success'] == True,str(j['success'])
	assert j['message'] == "Link to reset password has been sent to the registered mail ID",str(j['message'])


@pytest.mark.parametrize("email",[('ag33@yopmail.com')])
def test_restpass_fail(url,email):
	resp = restpass(url,email)
	j = json.loads(resp.text)
	assert resp.status_code == 200, request.text
	assert j['success'] == False,str(j['success'])
	assert j['message'] == "Email has not yet been registered",str(j['message'])

