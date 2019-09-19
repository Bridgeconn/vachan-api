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

def check_login(url,email,password):
	url = url + "/v1/auth" 
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	return resp
# POST method with access token

@pytest.mark.parametrize('languageCode,versionContentCode,versionContentDescription,year,revision,license',[("181","2",'versionContentDescription',"2019","2",'CC BY SA')])
def test_Createbiblesourcesup(supply_url,get_supAdmin_accessToken,languageCode,versionContentCode,versionContentDescription,year,revision,license):
	url = supply_url + '/v1/sources/bibles'
	data = {'languageCode':languageCode,
			'versionContentCode':versionContentCode,
            'versionContentDescription':versionContentDescription,
            'year':year,
            'revision': revision,
            'license' : license
            }
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert j['success'] == False, str(j)
	# assert j['message'] == "Source already exists", str(j)

@pytest.mark.parametrize('languageCode,versionContentCode,versionContentDescription,year,revision,license',[('mal','IRV','irv_3',"2019","2",'CC BY SA')])
def test_Createbiblesourcesup2(supply_url,get_supAdmin_accessToken,languageCode,versionContentCode,versionContentDescription,year,revision,license):
	url = supply_url + '/v1/sources/bibles'
	data = {'languageCode':languageCode,
			'versionContentCode':versionContentCode,
            'versionContentDescription':versionContentDescription,
            'year':year,
            'revision': revision,
            'license' : license
            }
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Source already exists", str(j)


@pytest.mark.parametrize('languageCode,versionContentCode,versionContentDescription,year,revision,license',[("6719","2",'versionContentDescription',"2019","2",'CC BY SA')])
def test_Createbiblesourcead(supply_url,get_supAdmin_accessToken,languageCode,versionContentCode,versionContentDescription,year,revision,license):
	url = supply_url + '/v1/sources/bibles'
	data = {'languageCode':languageCode,
			'versionContentCode':versionContentCode,
            'versionContentDescription':versionContentDescription,
            'year':year,
            'revision': revision,
            'license' : license
            }
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text