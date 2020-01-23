import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"


@pytest.fixture
def get_admin_accessToken():
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
def get_translator_accessToken():
	email = 'ag2@yopmail.com'
	password = '1189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token

def test_listorganisation_superadmin(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance (j,list), j
	# assert 'organisationId' in j[0], j[0]
	# assert 'organisationName' in j[0], j[0]
	# assert 'organisationAddress' in j[0], j[0]
	# assert 'organisationPhone' in j[0], j[0]
	# assert 'organisationEmail' in j[0], j[0] 
	# assert 'verified' in j[0], j[0]
	# assert 'userId' in j[0], j[0]
	# # assert isinstance(j,list),type(j)
	# # for org in j:
	# # 	if org["organisationName"] ==  'test_org':
	# # 		pytest.organisation_id = org["organisationId"]
	# # print (j)
	assert j['success'] == False, str(j)
	assert j['message'] == "No organisation data available", str(j)

def test_listorganisation_SuperAdmin2(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance (j,list), j
	assert 'organisationId' in j[0], j[0]
	assert 'organisationName' in j[0], j[0]
	assert 'organisationAddress' in j[0], j[0]
	assert 'organisationPhone' in j[0], j[0]
	assert 'organisationEmail' in j[0], j[0] 
	assert 'verified' in j[0], j[0]
	assert 'userId' in j[0], j[0]
	print(j)
def test_listorganisation_SuperAdmin3(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized", str(j)

def test_listorganisation_SuperAdmin4(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Server side error", str(j)


def test_listorganisation_admin(supply_url,get_admin_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_admin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance (j,list), j
	assert 'organisationId' in j[0], j[0]
	assert 'organisationName' in j[0], j[0]
	assert 'organisationAddress' in j[0], j[0]
	assert 'organisationPhone' in j[0], j[0]
	assert 'organisationEmail' in j[0], j[0] 
	assert 'verified' in j[0], j[0]
	assert 'userId' in j[0], j[0]
	print(j)

def test_listorganisation_admin2(supply_url,get_admin_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_admin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text	
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized", str(j)


def test_listorganisation_admin3(supply_url,get_admin_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_admin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text	
	assert j['success'] == False, str(j)
	assert j['message'] == "No organisation data available", str(j)


def test_listorganisation_translator(supply_url,get_translator_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_translator_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance (j,list), j
	assert 'organisationId' in j[0], j[0]
	assert 'organisationName' in j[0], j[0]
	assert 'organisationAddress' in j[0], j[0]
	assert 'organisationPhone' in j[0], j[0]
	assert 'organisationEmail' in j[0], j[0] 
	assert 'verified' in j[0], j[0]
	assert 'userId' in j[0], j[0]
	print(j)
	
	

# def test_listorganisationsuperadmin(supply_url,get_supAdmin_accessToken):
# 	url = supply_url + '/v1/autographamt/organisations'
# 	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert isinstance(j,list),type(j)
# 	for org in j:
# 		if org["organisationName"] ==  'test_org':
# 			pytest.organisation_id = org["organisationId"]
# 	print (j)

def test_listorganisation_translator2(supply_url,get_translator_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_translator_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized", str(j)

def test_listorganisation_translator3(supply_url,get_translator_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_translator_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Server side error", str(j)

def test_listorganisation_translator3(supply_url,get_translator_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_translator_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "No organisation data available", str(j)