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


@pytest.mark.parametrize('userEmail',[('ag21@yopmail.com')])
def test_delete_user_1(supply_url,get_supAdmin_accessToken,userEmail):
	url = supply_url + '/v1/autographamt/user/delete'
	data = {"userEmail":userEmail
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "User has translation assignments."


@pytest.mark.parametrize('userEmail',[('ag21@yopmail.com')])
def test_delete_user_2(supply_url,get_adm_accessToken,userEmail):
	url = supply_url + '/v1/autographamt/user/delete'
	data = {"userEmail":userEmail
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "UnAuthorized! Only a super admin can delete users."

@pytest.mark.parametrize('userEmail',[('ag21@yopmail.com')])
def test_delete_user_3(supply_url,get_trans_accessToken,userEmail):
	url = supply_url + '/v1/autographamt/user/delete'
	data = {"userEmail":userEmail
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "UnAuthorized! Only a super admin can delete users."

@pytest.mark.parametrize('userEmail',[('susanna@yopmail.com')])
def test_delete_user_4(supply_url,get_supAdmin_accessToken,userEmail):
	url = supply_url + '/v1/autographamt/user/delete'
	data = {"userEmail":userEmail
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	print(j)
	assert j['success'] == True, str(j)
	assert j['message'] == "Deactivated user.", str(j)