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

# @pytest.mark.parametrize("email, password",[("kavitharaju18@gmail.com",'111111')])
# def test_list_valid_user(supply_url,email,password):
# 	resp = check_login(supply_url,email,password)
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert "accessToken" in j, "success="+str(j['success'])+j['message']

@pytest.mark.parametrize("email, password",[("alex@yopmail.com",'1189')])
def test_list_valid_user(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert "accessToken" in j, "success="+str(j['success'])+j['message']



@pytest.mark.parametrize("email, password",[('kavitharaju18@gmail.com',"letme")])
def test_list_invalid_password(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "Incorrect Password", 'message='+j['message']

@pytest.mark.parametrize("email, password",[('kavitharaju@gmail.com',"letme"),('kavitharaju@bridgeconn.com',"letme")])
def test_list_invalid_email(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "This email is not registered", 'message='+j['message']

@pytest.mark.parametrize("email, password",[('kavitha.raju@bridgeconn.com',"letmepass")])
def test_list_notverified_email(supply_url,email,password):
	resp = check_login(supply_url,email,password)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, "success="+str(j['success'])
	assert j['message'] == "Email is not Verified", 'message='+j['message']
# create project
@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs2','Delhi','000','kavitharaju18@gmail.com')])
def test_createprojt(supply_url,get_trans_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
		'sourceId' = sourceId,
    	'targetLanguageId' = targetLanguageId
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print (j)
	assert j['success'] == False, str(j)
	assert j['message'] == "UnAuthorized", str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs4','Delhi','000','alex@yopmail.com')])
def test_createprojad(supply_url,get_adm_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations/projects'
data = {
		'sourceId' =sourceId,
    	'targetLanguageId' = targetLanguageId
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print (j)
	assert j['success'] == True, str(j)
	assert j['message'] == "Project created", str(j)

@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('bcs4','Delhi','000','alex@yopmail.com')])
def test_createprojsup(supply_url,get_supAdmin_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations/projects'
data = {
		'sourceId' =sourceId,
    	'targetLanguageId' = targetLanguageId
		}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	print (j)
	assert j['success'] == True, str(j)
	assert j['message'] == "Project created", str(j)
