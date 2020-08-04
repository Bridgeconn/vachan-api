import pytest
import requests
import json

@pytest.fixture
def url():
	# POST API
	return "https://stagingapi.autographamt.com/v1/registrations"

data = [
	("Joel","Johnson","joelcjohnson123@gmail.com",'111111'),  # valid detatils which is already exists
	("Joel","Johnson","joelcj@yopmail.com", '111111')         # new details
]

# -------------------- Check Signup page --------------------#
def test_pageload():
	resp = requests.get("https://staging.autographamt.com/signup")
	assert resp.status_code == 200


# ----------------------- existing user --------------------#
@pytest.mark.parametrize("firstName, lastName, email, password", [data[0]])
def test_existing_user(url, firstName, lastName, email, password):
	resp = requests.post(url, {'firstName':firstName, 'lastName':lastName, 'email':email, 'password':password})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == 'This email has already been Registered, '


# ----------------------- new user --------------------#
@pytest.mark.skip(reason="need to change the values")
@pytest.mark.parametrize("firstName, lastName, email, password", [data[1]])
def test_new_user(url, firstName, lastName, email, password):
	resp = requests.post(url, {'firstName':firstName, 'lastName':lastName, 'email':email, 'password':password})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == True
	assert out['message'] == 'Verification Email has been sent to your email id'

