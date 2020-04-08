import pytest
import requests
import json

@pytest.fixture
def url():
	# POST API
	return "https://stagingapi.autographamt.com/v1/auth"

data = [
	("joelcjohnson123@gmail.com",'111111'),  # valid detatils
	("joelcjohnson123@gmail.com", '11111'),  # wrong password
	("joelcjohnson@gmail.com",'111111'),     # email not registered
	("joel@yopmail.com", '111111')           # email not verified
]


# -------------------- Check login page --------------------#
def test_pageload():
	resp = requests.get("https://staging.autographamt.com/signin")
	assert resp.status_code == 200


# -------------------- valid user --------------------#
@pytest.mark.parametrize("email, password", [data[0]])
def test_valid_user(url, email, password):
	resp = requests.post(url, {'email': email, 'password': password})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out.get('accessToken') != None


#  --------------- with incorrect password --------- #
@pytest.mark.parametrize("email, password", [data[1]])
def test_invalid_password(url, email, password):
	resp = requests.post(url, {'email': email, 'password': password})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == 'Incorrect Password'


#  --------------- with unregistered emailId ---------- #
@pytest.mark.parametrize("email, password", [data[2]])
def test_unreg_email(url, email, password):
	resp = requests.post(url, {'email': email, 'password': password})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == 'This email is not registered'


#  --------------- with unverified emailId ---------- #
@pytest.mark.parametrize("email, password", [data[3]])
def test_unver_email(url, email, password):
	resp = requests.post(url, {'email': email, 'password': password})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == 'Email is not Verified'