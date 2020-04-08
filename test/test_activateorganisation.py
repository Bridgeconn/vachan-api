import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

#---------------- admin role----------------#
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

#---------------- su-admin role----------------#
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


#---------------check existing organisation-------------#
@pytest.mark.skip(reason="need to change the values")
@pytest.mark.parametrize('organisationId',[('35')])
def test_activateorganisation_sup(supply_url,get_supAdmin_accessToken,organisationId):
	url = supply_url + '/v1/autographamt/organisation/activate'
	data = {
			'organisationId':organisationId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False
	assert j['message'] == "Organisation already active"
	

#---------------check existing organisation by user role-------------#
@pytest.mark.parametrize('organisationId',[('35')])
def test_activateorganisation_2(supply_url,get_adm_accessToken,organisationId):
	url = supply_url + '/v1/autographamt/organisation/activate'
	data = {
			'organisationId':organisationId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False
	assert j['message'] == "UnAuthorized! Only a super admin can activate organizations."

