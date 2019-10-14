import pytest
import requests
import json
import test_listprojects

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"


@pytest.fixture
def get_accessTokenadm():
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
def get_accessTokentrans():
	email = 'kavitharaju18@gmail.com'
	password = '111111'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']
	return token

@pytest.mark.parametrize('sourceId,targetLanguageID,organisationId',[(56,3702,26)])
def test_createprojecttr(supply_url,get_accessTokentrans,sourceId,targetLanguageID,organisationId):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
		'sourceId':sourceId,
    	'targetLanguageId':targetLanguageID,
    	'organisationId':organisationId
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessTokentrans)})
	j = json.loads(resp.text)
	print(j)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Project created", str(j)
	### add code to delete the project

@pytest.mark.parametrize('sourceId,targetLanguageID,organisationId',[(56,4923,26)])
def test_createprojectsup1(supply_url,get_supAdmin_accessToken,sourceId,targetLanguageID,organisationId):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
		'sourceId':sourceId,
    	'targetLanguageId':targetLanguageID,
    	'organisationId':organisationId
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.dumps(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Project created", str(j)
	### add code to delete the project

@pytest.mark.parametrize('sourceId,targetLanguageID,organisationId',[(56,3699,13)])
def test_createprojectad(supply_url,get_supAdmin_accessToken,sourceId,targetLanguageID,organisationId):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
			'sourceId':sourceId,
    		'targetLanguageId':targetLanguageID,
    		'organisationId':organisationId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Project created", str(j)
	### add code to delete the project
