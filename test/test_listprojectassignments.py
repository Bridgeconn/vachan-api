import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"


@pytest.fixture
def get_admin_accessToken():
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

@pytest.fixture
def get_translator_accessToken():
	email = 'ag2@yopmail.com'
	password = '1189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']
	return token

def test_Listprojectasignment_SuperAdmin(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/projects/assignments/35'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert 'assignmentId' in j[0], j[0]
	assert 'books' in j[0], j[0]
	assert 'user' in j[0], j[0]
	assert 'projectId' in j[0], j[0]
	print (j)

# def test_Listprojectasignment_SuperAdmin2(supply_url,get_supAdmin_accessToken):
# 	url = supply_url + '/v1/autographamt/projects/assignments/35'
# 	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == False, str(j)
# 	assert j['message'] == "Not authorized", str(j)

def test__Listprojectasignment_Admin(supply_url,get_admin_accessToken):
	url = supply_url + '/v1/autographamt/projects/assignments/35'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_admin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print(j)
	assert 'assignmentId' in j[0], j[0]
	assert 'books' in j[0], j[0]
	assert 'user' in j[0], j[0]
	assert 'projectId' in j[0], j[0]


# def test__Listprojectasignment_Admin2(supply_url,get_admin_accessToken):
# 	url = supply_url + '/v1/autographamt/projects/assignments/35'
# 	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_admin_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == False, str(j)
# 	assert j['message'] == "Not authorized", str(j)

def test__Listprojectasignment_Translator(supply_url,get_translator_accessToken):
	url = supply_url + '/v1/autographamt/projects/assignments/35'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_translator_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print(j)
	assert 'assignmentId' in j[0], j[0]
	assert 'books' in j[0], j[0]
	assert 'user' in j[0], j[0]
	assert 'projectId' in j[0], j[0]


# def test__Listprojectasignment_Translator2(supply_url,get_translator_accessToken):
# 	url = supply_url + '/v1/autographamt/projects/assignments/35'
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == False, str(j)
# 	assert j['message'] == "Not authorized", str(j)

