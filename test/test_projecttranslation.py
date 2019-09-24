 # -- coding: utf - 8 --
import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

@pytest.fixture
def get_accessTokenad():
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
def get_accessToketr():
	email = "ag2@yopmail.com"
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


def test_Projecttranslationad(supply_url,get_accessTokenad):
	url = supply_url + '/v1/autographamt/projects/translations/करो/35'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_accessTokenad)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# assert 'translation' in j[0], j[0]
	# assert 'senses' in j[0], j[0]
	assert j['success'] == False, str(j)
	assert j['message'] == "No Translation or sense available for this token", str(j)


def test_Projecttranslationtr(supply_url,get_accessToketr):
	url = supply_url + '/v1/autographamt/projects/translations/करो/35'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_accessToketr)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# assert 'translation' in j[0], j[0]
	# assert 'senses' in j[0], j[0]
	assert j['success'] == False, str(j)
	assert j['message'] == "No Translation or sense available for this token", str(j)

def test_Projecttranslationsup(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/projects/translations/करो/35'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# assert 'translation' in j[0], j[0]
	# assert 'senses' in j[0], j[0]
	assert j['success'] == False, str(j)
	assert j['message'] == "No Translation or sense available for this token", str(j)