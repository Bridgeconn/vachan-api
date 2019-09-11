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


def check_login(url,email,password):
	url = url + "/v1/auth" 
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	return resp

def test_firstpage_load():
	url = "https://staging.autographamt.com"
	resp = requests.get(url)
	assert resp.status_code == 200, resp.text

# create project
@pytest.mark.parametrize('sourceId,targetLanguageID',[('31','2761')])
def test_createprojt(supply_url,get_trans_accessToken,soueceID,targetLanguageID):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
		'sourceId': 31,
    	'targetLanguageId': 2761
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print (j)
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized", str(j)

@pytest.mark.parametrize ('sourceId,targetLanguageID',[('31','2761')])
def test_createprojad (supply_url,get_adm_accessToken,soueceID,targetLanguageID):
	url = supply_url + '/v1/autographamt/organisations/projects'
data = {
		'sourceId': 31,
    	'targetLanguageId': 2761
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print (j)
	assert j['success'] == True, str(j)
	assert j['message'] == "Project created", str(j)

@pytest.mark.parametrize('sourceId,targetLanguageID',[('31','2761')])
def test_createprojsup(supply_url,get_supAdmin_accessToken,soueceID,targetLanguageID):
	url = supply_url + '/v1/autographamt/organisations/projects'
data = {
		'sourceId': 31,
    	'targetLanguageId': 2761
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print (j)
	assert j['success'] == True, str(j)
	assert j['message'] == "Project created", str(j)

