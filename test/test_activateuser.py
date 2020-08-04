import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"


@pytest.fixture
def get_supAdmin_accessToken():
	email = 'joelcjohnson123@gmail.com'
	password = '111111'
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

#-------------activate exist user with su-admin role-------------#
@pytest.mark.parametrize('userEmail',[('joelcjohnson123@gmail.com')])
def test_activatesource_sup(supply_url,get_supAdmin_accessToken,userEmail):
	url = supply_url + '/v1/autographamt/user/activate'
	data = {'userEmail':userEmail}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "User account already active.", str(j)

@pytest.mark.parametrize('userEmail',[('shawn@yopmail.com')])
def test_delete_user_3(supply_url,get_supAdmin_accessToken,userEmail):
	url = supply_url + '/v1/autographamt/user/delete'
	data = {'userEmail':userEmail}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == False, str(j)
	assert j['message'] == "User has translation assignments.", str(j)


@pytest.mark.parametrize('userEmail',[('ag7@yopmail.com')])
def test_delete_user_8(supply_url,get_supAdmin_accessToken,userEmail):
	url = supply_url + '/v1/autographamt/user/delete'
	data = {'userEmail':userEmail}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == False, str(j)
	assert j['message'] == "User not present.", str(j)

@pytest.mark.parametrize('userEmail',[('ag7@yopmail.com')])
def test_activatesource_2(supply_url,get_trans_accessToken,userEmail):
	url = supply_url + '/v1/autographamt/user/activate'
	data = {'userEmail':userEmail}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized! Only a super admin can actiavte user accounts.", str(j)

@pytest.mark.parametrize('userEmail',[('susanna@yopmail.com')])
def test_delete_user_8(supply_url,get_supAdmin_accessToken,userEmail):
	url = supply_url + '/v1/autographamt/user/delete'
	data = {'userEmail':userEmail}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	print(j)
	assert j['success'] == True, str(j)
	assert j['message'] == "Deactivated user.", str(j)

@pytest.mark.parametrize('userEmail',[('susanna@yopmail.com')])
def test_activatesource_2(supply_url,get_supAdmin_accessToken,userEmail):
	url = supply_url + '/v1/autographamt/user/activate'
	data = {'userEmail':userEmail}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "User re-activated", str(j)