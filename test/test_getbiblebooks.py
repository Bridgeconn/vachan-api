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
	return token

# @pytest.fixture
# def get_trans_accessToken2():
# 	email = 'ag27@yopmail.com'
# 	password = '1189'
# 	url = "https://stagingapi.autographamt.com/v1/auth"
# 	data = {'email':email,
# 			'password':password}
# 	resp = requests.post(url, data=data)
# 	respobj = json.loads(resp.text)
# 	token = respobj['accessToken']
# 	return token


def test_getbiblebookssup(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/bibles/35/books'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
  	assert isinstance(j,list), j
	assert 'sourceId' in j[0], j[0]
	assert 'books' in j[0], j[0]
	
def test_getbiblelbookssad(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/bibles/35/books'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list),j
	assert 'books' in j[0], j[0]
	
	# assert j['success'] == False, str(j)
	# assert j['message'] == "No Books uploaded yet", str(j)
   
def test_getbiblebooksstr1(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/bibles/31/books'
	resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list),j
	assert 'books' in j[0], j[0]

def test_getbiblebooksstr(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/bibles/21/books'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Source Id", str(j)

	
# def test_getbiblebooksstr2(supply_url,get_trans_accessToken2):
# 	url = supply_url + '/v1/bibles/40/books'
# 	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken2)})
# 	j = json.loads(resp.text)
# 	print(j)
# 	assert resp.status_code == 200, resp.text
# 	# assert j['success'] == False, str(j)
# 	# assert j['message'] == "No Books uploaded yet", str(j)

   

	
	 