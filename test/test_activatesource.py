import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"


#-------super admin role-----------#
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

#-----------normal user-------------#
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

#-------------activate source with su-admin role-------------#
@pytest.mark.skip(reason="need to change the values")
@pytest.mark.parametrize('sourceId',[('47')])
def test_activatesource_1(supply_url,get_supAdmin_accessToken,sourceId):
	url = supply_url + '/v1/autographamt/source/activate'
	data = {'sourceId':sourceId}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Source already active.", str(j)


#-------------deactivate source with su-admin role-------------#
@pytest.mark.parametrize('sourceId',[('47')])
def test_delete_source_2(supply_url,get_supAdmin_accessToken,sourceId):
	url = supply_url + '/v1/autographamt/source/delete'
	data = {'sourceId':sourceId}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	# assert j['success'] == True, str(j)
	# assert j['message'] == "Source deactivated.", str(j)


#-------------re-activate source with su-admin role-------------#
@pytest.mark.parametrize('sourceId',[('47')])
def test_reactivate_source_3(supply_url,get_supAdmin_accessToken,sourceId):
	url = supply_url +'/v1/autographamt/source/activate'
	data = {'sourceId':sourceId}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == True
	assert j['message'] == "Source re-activated."


#-------------activate source with user role-------------#
@pytest.mark.parametrize('sourceId',[('12')])
def test_activatesource_5(supply_url,get_trans_accessToken,sourceId):
	url = supply_url + '/v1/autographamt/source/activate'
	data = {'sourceId':sourceId}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False
	assert j['message'] == "Unauthorized attempt"
