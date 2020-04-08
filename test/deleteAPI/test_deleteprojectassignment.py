import pytest
import requests
import json

@pytest.fixture
def url():
	# POST API 
	return "https://stagingapi.autographamt.com/v1/autographamt/projects/assignments"


def userdetails():
	data = [
			(9, 65),     # delete assigned user 
			(505, 65)    # delete unknow user
	]
	return data


def jsondump(data1):
	jsondump = {'userId': data1[0],
				'projectId': data1[1]
	}
	return(jsondump)


# --------------------- delete new user --------------------#
def test_projectassignment_newuser(url):
	usr = userdetails()
	jsondata = jsondump(usr[0])
	resp = requests.delete(url,data=json.dumps(jsondata))
	out = json.loads(resp.text)
	assert resp.status_code == 200
	# assert out['success'] == True
	# assert out['message'] == "User removed from Project"


# --------------------- delete unknown user -----------------#
def test_projectassignment_existingusr(url):
	usr = userdetails()
	jsondata = jsondump(usr[1])
	resp = requests.delete(url,data=json.dumps(jsondata))
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == "User Role Does Not exist"
