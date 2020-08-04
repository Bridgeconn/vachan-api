import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

@pytest.fixture
def get_accessTokenadm():
	email = "alex@yopmail.com"
	password = "1189"
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']
	return token

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

def test_projectassignmentsna(supply_url,get_accessTokenadm):
	url = supply_url + '/v1/autographamt/projects'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_accessTokenadm)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	assert 'organisationName' in j[0], j[0]
	assert 'sourceId' in j[0], j[0]
	assert 'projectName' in j[0], j[0]
	assert 'targetId' in j[0], j[0]

def test_projectassignmentsna1(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/projects'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	

	

def test_projectassignmentst(supply_url,get_accessTokentr):
	url = supply_url + '/v1/autographamt/projects'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_accessTokentr)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
    # assert j['success'] == False, str(j)
	# assert j['message'] == "Not authorized", str(j)
	