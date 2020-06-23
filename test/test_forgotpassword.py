import pytest
import requests
import json

@pytest.fixture
def url():
<<<<<<< HEAD
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
=======
	# POST API
	return "https://stagingapi.autographamt.com/v1/forgotpassword"

data = [
	(23233,'111111'),  # incorrect temp password
	(651110, '111111')   # correct temp password
]


# -------------------- Check page --------------------#
def test_pageload():
	resp = requests.get("https://staging.autographamt.com/signin")
	assert resp.status_code == 200


# ----------------------- checking with incorrect temp password --------------------#
@pytest.mark.parametrize("temporaryPassword, password", [data[0]])
def test_incorrect(url, temporaryPassword, password):
	resp = requests.post(url, {'temporaryPassword':temporaryPassword, 'password':password})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == 'Invalid temporary password.'


# ----------------------- checking with correct temp password --------------------#
@pytest.mark.skip(reason="need to change the values")
@pytest.mark.parametrize("temporaryPassword, password", [data[1]])
def test_correct(url, temporaryPassword, password):
	resp = requests.post(url, {'temporaryPassword':temporaryPassword, 'password':password})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == True
	assert out['message'] == 'Password has been reset. Login with the new password.'
>>>>>>> origin/master
