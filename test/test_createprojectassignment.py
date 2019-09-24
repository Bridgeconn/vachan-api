import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

# @pytest.fixture
# def get_accessTokenadm():
# 	email = "alex@yopmail.com"
# 	password = "1189"
# 	url = "https://stagingapi.autographamt.com/v1/auth"
# 	data = {'email':email,
# 			'password':password}
# 	resp = requests.post(url, data=data)
# 	respobj = json.loads(resp.text)
# 	token = respobj['accessToken']

# 	return token

@pytest.fixture
def get_accessTokentr():
	email = "ag2@yopmail.com"
	password = "1189"
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token

@pytest.fixture
def get_supAdmin_accessToken():
	email = 'savitha.mark@bridgeconn.com'
	password = '221189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token


# @pytest.mark.parametrize('userID,projectID,Books',[("14","35",'act')])
# def test_projectassignmentAd(supply_url,get_accessTokenadm,userID, projectID,Books):
# 	url = supply_url + '/v1/autographamt/projects/assignments'
# 	data = {
# 			'userId': userID,
# 			'projectId': projectID,
# 			'Books': Books
# 			}
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessTokenadm)})
# 	j = json.loads(resp.text)
# 	print(j)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == True, str(j)
# 	assert j['message'] == "User Role Updated", str(j)

@pytest.mark.parametrize('userID,projectID,Books',[("30","37",'rev')])
def test_projectassignmentsup(supply_url,get_supAdmin_accessToken,userID, projectID,Books):
	url = supply_url + '/v1/autographamt/projects/assignments'
	data = {'userId': userID,
			'projectId': projectID,
			'books': Books
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "User Role Updated", str(j)


@pytest.mark.parametrize('userID,projectID,Books',[("30","37",'rev')])
def test_projectassignmenttr(supply_url,get_accessTokentr,userID, projectID,Books):
	url = supply_url + '/v1/autographamt/projects/assignments'
	data = {'userId': userID,
			'projectId': projectID,
			'books': Books
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessTokentr)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "User Role Updated", str(j)





