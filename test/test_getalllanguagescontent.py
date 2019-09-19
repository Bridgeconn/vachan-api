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

def check_login(url,email,password):
	url = url + "/v1/auth" 
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	return resp

def test_getAlllanguagescontentsup(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/languages/1'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	#print(j)
	assert 'languageCode' in j[0], j[0]
	assert 'languageId' in j[0], j[0]
    # assert 'languageName'in j[0], j[0]
	

def test_getAlllanguagescontentad(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/languages/2'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	#print(j)
	assert isinstance(j,list), j
	assert 'languageCode' in j[0], j[0]
	assert 'languageId' in j[0], j[0]
    # assert 'languageName'in j[0], j[0]
	
def test_getAlllanguagescontenttr(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/languages/1'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	#print(j)
	assert isinstance(j,list), j
	assert 'languageCode' in j[0], j[0]
	assert 'languageId' in j[0], j[0]
    # assert 'languageName'in j[0], j[0]
	
def test_getAlllanguagescontenttr2(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/languages/6'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	#print(j)
	# assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# assert 'languageCode' in j[0], j[0]
	# assert 'languageId' in j[0], j[0]
    # assert 'languageName'in j[0], j[0]
	assert j['success'] == False, str(j)
	assert j['message'] == "No languages available for this content", str(j)
  
