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


def check_login(url,email,password):
	url = url + "/v1/auth" 
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	return resp

def test_firstpage_load():
	url = "https://staging.autographamt.com"
	resp = requests.get(url)
	assert resp.status_code == 200, resp.text

## GET method with access token


def test_getprojassigna(supply_url,get_accessTokenadm):
	url = supply_url + '/v1/autographamt/projects/assignments/35'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_accessTokenadm)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print (j)
	assert 'assignmentId' in j[0], j[0]
	assert 'books' in j[0], j[0]
	assert 'user' in j[0], j[0]
	assert 'projectId' in j[0], j[0]


def test_getprojassignw(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/projects/assignments/35'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print(j)
	assert 'assignmentId' in j[0], j[0]
	assert 'books' in j[0], j[0]
	assert 'user' in j[0], j[0]
	assert 'projectId' in j[0], j[0]

def test_getprojassignt(supply_url,get_accessTokentr):
	url = supply_url + '/v1/autographamt/projects/assignments/35'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_accessTokentr)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print(j)
	assert 'assignmentId' in j[0], j[0]
	assert 'books' in j[0], j[0]
	assert 'user' in j[0], j[0]
	assert 'projectId' in j[0], j[0]

