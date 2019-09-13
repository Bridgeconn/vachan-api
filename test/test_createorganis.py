import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

@pytest.fixture
def get_accessToken():
	email = "kavitharaju18@gmail.com"
	password = "111111"
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


def check_login(url,email,password):
	url = url + "/v1/auth" 
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	return resp

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs2','Delhi','000','kavitharaju18@gmail.com')])
def test_createOrg(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Organisation request sent", str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs3','Delhi','000','ag28@yopmail.com')])
def test_createOrg(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Organisation request sent", str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs3','Delhi','000','ag41@yopmail.com')])
def test_createOrg(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Organisation request sent", str(j)


@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('','','','ag32@yopmail.com')])
def test_createOrge(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('','','000','')])
def test_createOrgp(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('','','000','ag32@yopmail.com')])
def test_createOrgpe(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('','Delhi','','')])
def test_createOrga(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('','Delhi','000','')])
def test_createOrgap(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('','Delhi','000','ag32@yopmail.com')])
def test_createOrgape(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs3','','','')])
def test_createOrgn(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs3','','','ag32@yopmail.com')])
def test_createOrgne(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs3','','000','')])
def test_createOrgnp(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs3','','000','ag32@yopmail.com')])
def test_createOrgnpe(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs3','Delhi','','')])
def test_createOrgnp(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs3','Delhi',"",'ag32@yopmail.com')])
def test_createOrgnae(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs3','Delhi','000','')])
def test_createOrgndp(supply_url,get_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)

