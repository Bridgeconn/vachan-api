import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"


@pytest.mark.parametrize('userID,projectID,Books',[(30,52,["rev"])])
def test_projectassignment_newtanslator(supply_url,userID, projectID,Books):
	url = supply_url + '/v1/autographamt/projects/assignments'
	data = {'userId': userID,
			'projectId': projectID,
			'books': Books
			}
	resp = requests.post(url,data=json.dumps(data))
	j = json.loads(resp.text)
	print(j)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "User Role Assigned", str(j)
	### add code to delete assignment


@pytest.mark.parametrize('userID,projectID,Books',[(30,52,["mat"])])
def test_projectassignment_existingTranslator(supply_url,userID, projectID,Books):
	url = supply_url + '/v1/autographamt/projects/assignments'
	data = {'userId': userID,
			'projectId': projectID,
			'books': Books
			}
	resp = requests.post(url,data=json.dumps(data))
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "User Role Updated", str(j)





