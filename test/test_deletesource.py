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


@pytest.mark.parametrize('sourceId',[('47')])
def test_reactivate_source_activate(supply_url,get_supAdmin_accessToken,sourceId):
	url = supply_url +'/v1/autographamt/source/activate'
	data = {'sourceId':sourceId
	}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	# print(j)
	assert j['success'] == True, str(j)
	assert j['message'] == "Source re-activated.", str(j)


@pytest.mark.parametrize('sourceId',[('47')])
def test_delete_source_1(supply_url,get_supAdmin_accessToken,sourceId):
	url = supply_url + '/v1/autographamt/source/delete'
	data = {"sourceId":sourceId
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == True, str(j)
	assert j['message'] == "Source deactivated.", str(j)

@pytest.mark.parametrize('sourceId',[('36')])
def test_delete_source_2(supply_url,get_trans_accessToken,sourceId):
	url = supply_url + '/v1/autographamt/source/delete'
	data = {"sourceId":sourceId
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == False, str(j)
	assert j['message'] == "Unauthorized attempt", str(j)

@pytest.mark.parametrize('sourceId',[('36')])
def test_delete_source_3(supply_url,get_trans_accessToken,sourceId):
	url = supply_url + '/v1/autographamt/source/delete'
	data = {"sourceId":sourceId
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == False, str(j)
	assert j['message'] == "Unauthorized attempt", str(j)


@pytest.mark.parametrize('sourceId',[('0')])
def test_delete_source_4(supply_url,get_supAdmin_accessToken,sourceId):
	url = supply_url + '/v1/autographamt/source/delete'
	data = {"sourceId":sourceId
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == False, str(j)
	assert j['message'] == "Source not present.", str(j)

