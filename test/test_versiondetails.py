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

def test_getversiondetailssup(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/versiondetails/1/3702'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# print (j)
	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]

def test_versiondetailsup1(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/versiondetails/2/3702'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# print (j)
	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]

def test_versiondetailsup2(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/versiondetails/3/3702'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# print (j)
	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]

def test_versiondetailsup3(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/versiondetails/1/39'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# print (j)
	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]

def test_versiondetailsup4(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/versiondetails/2/39'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# print (j)
	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]


def test_versiondetailsup5(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/versiondetails/3/39'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# print (j)
	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]
 

def test_versiondetailad(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/versiondetails/1/4'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	print (j)
	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]


def test_versiondetailad3(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/versiondetails/2/4'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	print (j)
	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]

def test_versiondetailad4(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/versiondetails/3/4'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	print (j)
	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]

def test_versiondetailsad5(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/versiondetails'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	print (j)
	assert 'sourceId' in j[0], j[0]
	assert 'versionContentDescription' in j[0], j[0]
	assert 'year' in j[0], j[0]
	assert 'license' in j[0], j[0]
	assert 'revision' in j[0], j[0]
	assert 'contentType' in j[0], j[0]
	assert 'languageName' in j[0], j[0]

   
def test_versiondetailtr1(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/versiondetails'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	print (j)
 	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]


def test_versiondetailsup11(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/versiondetails'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	print (j)
 	# assert 'sourceId' in j[0], j[0]
	# assert 'versionContentDescription' in j[0], j[0]
	# assert 'year' in j[0], j[0]
	# assert 'license' in j[0], j[0]
	# assert 'revision' in j[0], j[0]
	# assert 'contentType' in j[0], j[0]
	# assert 'languageName' in j[0], j[0]

  