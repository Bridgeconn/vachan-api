import pytest
import requests
import json

@pytest.fixture
def url():
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
