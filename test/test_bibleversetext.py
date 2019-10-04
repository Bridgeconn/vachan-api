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

def test_getbibleversessup(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/bibles/35/books/PRO/chapters/7/verses/17'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.dumps(resp.text)
	assert resp.status_code == 200, resp.text
  	# assert isinstance(j,list), j
    # assert 'bibleBookCode'in j[0], j[0]
	# assert 'sourceId' in j[0],j[0]
	# assert 'reference' in j[0],j[0]
    # assert 'verseNumber' in j[0],j[0]
	# assert 'chapterNumber' in j[0],j[0]
    
def test_getbibleverseup2(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/bibles/89/books/pro/chapters/pro.2/verses/18'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Source doesn't exist", str(j)
 

def test_getbibleversead(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/bibles/35/books/55/chapters/pro.3/verses/1'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid book code", str(j)
 

def test_getbibleversead2(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/bibles/98/books/55/chapters/pro.8/verses/3'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid book code", str(j)
 
def test_getbibleversead3(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/bibles/35/books/54/chapters/pro.10/verses'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid book code", str(j)
 
   
def test_getbibleversestr(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/bibles/30/books/65/chapters/pro.26/verses/4'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid book code", str(j)
  
    



	
	 
