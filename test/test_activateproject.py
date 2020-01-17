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

# @pytest.mark.parametrize('projectId',[('67')])
# def test_delete_project_4(supply_url,get_supAdmin_accessToken,projectId):
# 	url = supply_url + '/v1/autographamt/project/activate'
# 	data = {"projectId":projectId
# 	}
# 	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200
# 	print(j)
# 	# assert j['success'] == True, str(j)
# 	# assert j['message'] == "Project  removed", str(j)

@pytest.mark.parametrize('projectId',[("35")])
def test_delete_Project_3(supply_url,get_supAdmin_accessToken,projectId):
	url = supply_url + "/v1/autographamt/project/delete"
	data = {
            'projectId': projectId
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "Deactivated project."

@pytest.mark.parametrize('projectId',[('35')])
def test_activateproject_sup(supply_url,get_supAdmin_accessToken,projectId):
	url = supply_url + '/v1/autographamt/project/activate'
	data = {
			'projectId':projectId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Project re-activated", str(j)

@pytest.mark.parametrize('projectId',[('0')])
def test_activateproject_sup1(supply_url,get_supAdmin_accessToken,projectId):
	url = supply_url + '/v1/autographamt/project/activate'
	data = {
			'projectId':projectId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Project not present.", str(j)

@pytest.mark.parametrize('projectId',[('35')])
def test_activateproject_sup2(supply_url,get_supAdmin_accessToken,projectId):
	url = supply_url + '/v1/autographamt/project/activate'
	data = {
			'projectId':projectId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Project already active.", str(j)

# @pytest.mark.parametrize('projectId',[('35')])
# def test_activateproject_sup3(supply_url,get_supAdmin_accessToken,projectId):
# 	url = supply_url + '/v1/autographamt/project/activate'
# 	data = {
# 			'projectId':projectId
# 			}
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == False, str(j)
# 	assert j['message'] == "Project already active.", str(j)


@pytest.mark.parametrize('projectId',[('12')])
def test_activateproject_1(supply_url,get_trans_accessToken,projectId):
	url = supply_url + '/v1/autographamt/project/activate'
	data = {
			'projectId':projectId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized! Only the organisation admin or super admin can delete projects.", str(j)


@pytest.mark.parametrize('projectId',[('53')])
def test_activateproject_2(supply_url,get_adm_accessToken,projectId):
	url = supply_url + '/v1/autographamt/project/activate'
	data = {
			'projectId':projectId
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Project not present in the organisation.", str(j)