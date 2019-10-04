import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"


@pytest.fixture
def get_adm_accessToken():
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
def get_trans_accessToken():
	email = 'ag2@yopmail.com'
	password = '1189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token

def test_listorganisationsup(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "No organisation data available", str(j)
	# assert isinstance (j,list), j
	# assert 'organisationId' in j[0], j[0]
	# assert 'organisationName' in j[0], j[0]
	# assert 'organisationAddress' in j[0], j[0]
	# assert 'organisationPhone' in j[0], j[0]
	# assert 'organisationEmail' in j[0], j[0] 
	# assert 'verified' in j[0], j[0]
	# assert 'userId' in j[0], j[0]

def test_listorganisationgad(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance (j,list), j
	assert 'organisationId' in j[0], j[0]
	assert 'organisationName' in j[0], j[0]
	assert 'organisationAddress' in j[0], j[0]
	assert 'organisationPhone' in j[0], j[0]
	assert 'organisationEmail' in j[0], j[0] 
	assert 'verified' in j[0], j[0]
	assert 'userId' in j[0], j[0]
	
	
def test_listorganisationtr(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized", str(j)
