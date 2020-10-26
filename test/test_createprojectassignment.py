import pytest
import requests
import json

@pytest.fixture
def url():
	# POST API 
	return "https://stagingapi.autographamt.com/v1/autographamt/projects/assignments"


def userdetails():
	data = [
			(9,'65',["mat"]),   # new assign 
			(9,'65',["mat"])    # existing user with as
	]
	return data


def jsondump(data1):
	jsondump = {'userId': data1[0],
				'projectId': data1[1],
				'books': data1[2]
	}
	return(jsondump)


# --------------------- assign new user --------------------#
def test_projectassignment_newuser(url):
	usr = userdetails()
	jsondata = jsondump(usr[0])
	resp = requests.post(url,data=json.dumps(jsondata))
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == True
	assert out['message'] == "User Role Assigned"


# --------------------- assign existing user -----------------#
def test_projectassignment_existingusr(url):
	usr = userdetails()
	jsondata = jsondump(usr[1])
	resp = requests.post(url,data=json.dumps(jsondata))
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == True
	assert out['message'] == "User Role Updated"





