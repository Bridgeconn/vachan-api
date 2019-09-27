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
	email = 'ag2@yopmail.com'
	password = '1189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

@pytest.mark.parametrize('sourceId,targetLanguageID',[("40","181")])
def test_createprojecttr(supply_url,get_accessTokentrans,sourceId,targetLanguageID):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
		'sourceId':sourceId,
    	'targetLanguageId':targetLanguageID
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessTokentrans)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Not authorized", str(j)

@pytest.mark.parametrize('sourceId,targetLanguageID',[("35","18")])
def test_createprojectsup1(supply_url,get_supAdmin_accessToken,sourceId,targetLanguageID):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
		'sourceId':sourceId,
    	'targetLanguageId':targetLanguageID
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.dumps(resp.text)
	assert resp.status_code == 500, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Project created", str(j)

@pytest.mark.parametrize('sourceId,targetLanguageID',[("4","39")])
def test_createprojectsup2(supply_url,get_supAdmin_accessToken,sourceId,targetLanguageID):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
		'sourceId':sourceId,
    	'targetLanguageId':targetLanguageID
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.dumps(resp.text)
	assert resp.status_code == 500, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Project created", str(j)

@pytest.mark.parametrize('sourceId,targetLanguageID',[("35","39")])
def test_createprojectad(supply_url,get_supAdmin_accessToken,sourceId,targetLanguageID):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
			'sourceId':sourceId,
    		'targetLanguageId':targetLanguageID
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Project created", str(j)

@pytest.mark.parametrize('sourceId,targetLanguageID',[("3702","181")])
def test_createprojectad2(supply_url,get_supAdmin_accessToken,sourceId,targetLanguageID):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
			'sourceId':sourceId,
    		'targetLanguageId':targetLanguageID
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text

@pytest.mark.parametrize('sourceId,targetLanguageID',[("35","974")])
def test_createprojectsup3(supply_url,get_supAdmin_accessToken,sourceId,targetLanguageID):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
		'sourceId':sourceId,
    	'targetLanguageId': targetLanguageID
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "No projects created yet", str(j)

@pytest.mark.parametrize('sourceId,targetLanguageID',[("181","2302")])
def test_createprojectsup4(supply_url,get_supAdmin_accessToken,sourceId,targetLanguageID):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
		'sourceId':sourceId,
    	'targetLanguageId': targetLanguageID
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "No projects created yet", str(j)
