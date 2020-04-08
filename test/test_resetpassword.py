import pytest
import requests
import json

@pytest.fixture
def url():
	# POST API
	return "https://stagingapi.autographamt.com/v1/resetpassword"

data = [
	("joelcjohnson123@gmail.com"),  # valid email id
	("joelcjn@yopmail.com")           # invalid email id
]

# -------------------- Check page --------------------#
def test_pageload():
	resp = requests.get("https://staging.autographamt.com")
	assert resp.status_code == 200


# ----------------------- valid email id --------------------#
@pytest.mark.parametrize("email", [data[0]])
def test_valid_id(url, email):
	resp = requests.post(url, {'email':email})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == True
	assert out['message'] == 'Link to reset password has been sent to the registered mail ID'


# ----------------------- invalid email id --------------------#
@pytest.mark.parametrize("email", [data[1]])
def test_invalid_id(url, email):
	resp = requests.post(url, {'email':email})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == 'Email has not yet been registered'

