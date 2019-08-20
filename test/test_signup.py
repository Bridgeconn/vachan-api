import pytest
import requests
import json

def sign_up(url, FirstName, LastName,EmailAddress,Password):
	url = url + "/v1/auth"  
	data = {'Firstname':FirstName,
            'Lastname':LastName,
            'Email':EmailAddress,
		'Password':Password}
	resp = requests.post(url,data=data)
	return resp

def test_signup_load():
	url = "https://staging.autographamt.com/signup"
	resp = requests.get(url)
	assert resp.status_code == 200, resp.text

@pytest.mark.parametrize("FirstName,LastName,EmailAddress, Password",[('ag','ag','ag17@yopmail.com',"1189")])
def test_sugnup_user(url,FirstName,LastName,EmailAddress,Password):
	resp = sign_up(url,FirstName,LastName,EmailAddress,Password)
	j = json.loads(resp.text)
	assert resp.status_code == 201, resp.text
	assert "accessToken" in j, "success="+str(j['success'])+j['message']
