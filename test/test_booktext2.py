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
	return token

@pytest.fixture
def get_trans_accessToken2():
	email = 'ag27@yopmail.com'
	password = '1189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']
	return token
	
def test_booktextsup3(supply_url,get_supAdmin_accessToken):
    url = supply_url +'/v1/sources/4053/json/47'
    resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_supAdmin_accessToken)})
    j = json.loads(resp.text)
    assert resp.status_code == 200, resp.text 
    assert j['success'] == False, str(j)
    assert j['message'] == "Source File not available. Upload source", str(j)

def test_booktextsup4(supply_url,get_supAdmin_accessToken):
    url = supply_url +'/v1/sources/4211/usfm/49'
    resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_supAdmin_accessToken)})
    j = json.loads(resp.text)
    assert resp.status_code == 200, resp.text 
    assert j['success'] == False, str(j)
    assert j['message'] == "Source File not available. Upload source", str(j)

def test_booktexttr(supply_url,get_trans_accessToken2):
    url = supply_url +'/v1/sources/4211/usfm/41'
    resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_trans_accessToken2)})
    j = json.loads(resp.text)
    assert resp.status_code == 200, resp.text 
    assert j['success'] == False, str(j)
    assert j['message'] == "Source File not available. Upload source", str(j)

def test_booktexttr2(supply_url,get_trans_accessToken2):
    url = supply_url +'/v1/sources/4211/usfm/41'
    resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_trans_accessToken2)})
    j = json.loads(resp.text)
    assert resp.status_code == 200, resp.text 
    assert j['success'] == False, str(j)
    assert j['message'] == "Source File not available. Upload source", str(j)


def test_booktextad1(supply_url,get_adm_accessToken):
    url = supply_url +'/v1/sources/4211/ /41'
    resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_adm_accessToken)})
    j = json.loads(resp.text)
    assert resp.status_code == 200, resp.text 
    assert j['success'] == False, str(j)
    assert j['message'] == "Source File not available. Upload source", str(j)


# def test_booktextad2(supply_url,get_adm_accessToken):
#     url = supply_url +'/v1/sources/3732/json/29'
#     resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_adm_accessToken)})
#     j = json.loads(resp.text)
#     assert resp.status_code == 200, resp.text 
#     assert j['success'] == False, str(j)
#     assert j['message'] == "Book not available", str(j)

# def test_booktextad4(supply_url,get_adm_accessToken):
#     url = supply_url +'/v1/sources/7027/usfm/29'
#     resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_adm_accessToken)})
#     j = json.loads(resp.text)
#     assert resp.status_code == 200, resp.text 
#     assert j['success'] == False, str(j)
#     assert j['message'] == "Book not available", str(j)








	 