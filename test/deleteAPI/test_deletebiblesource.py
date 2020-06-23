import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

#----------- admin role --------------#
@pytest.fixture
def get_adm_accessToken():
	email = "alex@yopmail.com"
	password = "1189"
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']
	return token

#----------- su-admin role --------------#
@pytest.fixture
def get_supAdmin_accessToken():
	email = 'savitha.mark@bridgeconn.com'
	password = '221189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']
	return token

#----------- normalrole --------------#
@pytest.fixture
def get_trans_accessToken():
	email = 'ag2@yopmail.com'
	password = '1189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']
	return token

@pytest.mark.parametrize('sourceId',[('58')])
def test_delete_Biblesource_1(supply_url,get_supAdmin_accessToken,sourceId):
	url = supply_url + "/v1/autographamt/source/delete"
	data = {'sourceId':sourceId}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
    # assert j['message'] == "Source is already deactivated."

#----------- delete with normalrole --------------#
@pytest.mark.parametrize('sourceId',[('55')])
def test_delete_Biblesource_2(supply_url,get_adm_accessToken,sourceId):
	url = supply_url + "/v1/autographamt/source/delete"
	data = {'sourceId':sourceId
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	

#----------- delete with norma lrole --------------#
@pytest.mark.parametrize('sourceId',[('55')])
def test_delete_Biblesource_3(supply_url,get_trans_accessToken,sourceId):
	url = supply_url + "/v1/autographamt/source/delete"
	data = {'sourceId':sourceId}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "Unauthorized attempt"