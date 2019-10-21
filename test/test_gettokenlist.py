#-*-coding:utf-8-*-
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

def test_gettokeenlistsup(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/tokenlist/35/heb'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	for x in j:
		print(x.encode("utf-8"))
	assert resp.status_code == 200, resp.text
	assert resp.status_code == 200, resp.text
	
	

def test_gettokeenlistad(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/tokenlist/35/2ti'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	for x in j:
		print(x.encode("utf-8"))
	assert resp.status_code == 200, resp.text
	assert resp.status_code == 200, resp.text
	
	

def test_gettokeenlisttr(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/tokenlist/35/2jn'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	for x in j:
		print(x.encode("utf-8"))
	assert resp.status_code == 200, resp.text
	assert resp.status_code == 200, resp.text
	
	
	
	
  
