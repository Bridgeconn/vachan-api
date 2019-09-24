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
	
# @pytest.fixture
# def get_trans_accessToken3():
# 	email = 'kavitharaju18@gmail.com'
# 	password = '111111'
# 	url = "https://stagingapi.autographamt.com/v1/auth"
# 	data = {'email':email,
# 			'password':password}
# 	resp = requests.post(url, data=data)
# 	respobj = json.loads(resp.text)
# 	token = respobj['accessToken']
# 	return token

def test_Contenttypesup(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/contenttypes'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	assert 'contentType' in j[0], j[0]
	assert 'contentId' in j[0], j[0]
 
	

def test_Contenttypead(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/contenttypes'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	assert 'contentType' in j[0], j[0]
	assert 'contentId' in j[0], j[0]
   


def test_Contenttypetr(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/contenttypes'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	assert 'contentType' in j[0], j[0]
	assert 'contentId' in j[0], j[0]
	 
# def test_Contenttypetr2(supply_url,get_trans_accessToken3):
# 	url = supply_url + '/v1/contenttypes'
# 	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken3)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == False, str(j)
# 	assert j['message'] == "There are no contents available", str(j)
  
  
