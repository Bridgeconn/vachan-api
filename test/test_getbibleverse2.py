  # -- coding: utf - 8 --
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

def check_login(url,email,password):
	url = url + "/v1/auth" 
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	return resp

def test_getbiblechapterssup(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/bibles/35/chapters/pro.7/verses'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
  	assert isinstance(j,list), j
	assert 'sourceId' in j[0], j[0]
	assert 'chapterId' in j[0], j[0]
	assert 'verse' in j[0], j[0]


def test_getbibleverse2sup2(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/bibles/35/chapters/pro/verses'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Chapter id format.", str(j)
  	# assert isinstance(j,list), j
	# assert 'sourceId' in j[0], j[0]
	# assert 'chapter' in j[0], j[0]

def test_getbibleverse2sad(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/bibles/31/chapters/55/verses'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Chapter id format.", str(j)

def test_getbibleverse2sad2(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/bibles/98/chapters/55/verses'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Chapter id format.", str(j)


def test_getbibleverse2ad3(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/bibles/35/chapters/tt/verses'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Chapter id format.", str(j)
  

def test_getbiblechaptersstr(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/bibles/35/chapters/aa/verses'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Chapter id format.", str(j)
  

    



	
	 