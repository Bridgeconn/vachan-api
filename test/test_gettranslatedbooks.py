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

def test_firstpage_load():
	url = "https://staging.autographamt.com"
	resp = requests.get(url)
	assert resp.status_code == 200, resp.text

## GET method with access token for list users
def test_getUserProjectssup(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/translatedbooks/30/18'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	print (j)
	# assert 'languageName' in j[0], j[0]
	# assert 'languageId' in j[0], j[0]
    # assert 'languageCode' in j[0], j[0]
	

def test_getUserProjectad(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/translatedbooks/30/18'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	print (j)
	# assert 'languageName' in j[0], j[0]
	# assert 'languageId' in j[0], j[0]
    # assert 'languageCode' in j[0], j[0]
	


def test_getUserProjecttr(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/translatedbooks/30/18'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	print (j)
	# assert 'languageName' in j[0], j[0]
	# assert 'languageId' in j[0], j[0]
    # assert 'languageCode' in j[0], j[0]
	
  
