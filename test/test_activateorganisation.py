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

@pytest.mark.parametrize('organisationId',[('35')])
def test_activateorganisation_sup(supply_url,get_supAdmin_accessToken,organisationId):
	url = supply_url + '/v1/autographamt/organisation/activate'
	data = {
			'organisationId':organisationId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Organisation already active", str(j)


@pytest.mark.parametrize('organisationId',[('35')])
def test_activateorganisation_1(supply_url,get_trans_accessToken,organisationId):
	url = supply_url + '/v1/autographamt/organisation/activate'
	data = {
			'organisationId':organisationId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized! Only a super admin can activate organizations.", str(j)



@pytest.mark.parametrize('organisationId',[('35')])
def test_activateorganisation_2(supply_url,get_adm_accessToken,organisationId):
	url = supply_url + '/v1/autographamt/organisation/activate'
	data = {
			'organisationId':organisationId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized! Only a super admin can activate organizations.", str(j)

@pytest.mark.parametrize('organisationId',[('1')])
def test_activateorganisation_3(supply_url,get_adm_accessToken,organisationId):
	url = supply_url + '/v1/autographamt/organisation/activate'
	data = {
			'organisationId':organisationId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized! Only a super admin can activate organizations.", str(j)