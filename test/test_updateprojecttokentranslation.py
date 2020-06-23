import pytest
import requests
import json

@pytest.fixture
def url():
	# POST API
	return "https://stagingapi.autographamt.com/v1/autographamt/projects/translations"


data = [
	('joelcjohnson123@gmail.com', '111111') 
]

def projectdetails():
	data = [
			(59,'अपना','test1',['senses']),     # add new token translation with all values		
			(59,'अंकुर','test1',['senses']),     # add existing token translation with same values
			(59,'अंकुर','test111',['senses']),      # update token trasnlation
	]
	return data

def jsondump(data1):
	jsondump = {'projectId': data1[0],
				'token': data1[1],
                'translation': data1[2],
                'senses': data1[3]
	}
	return(jsondump)


# ------------------------- get access token --------------------------- #
def get_accesstoken(email, password):
	auth_url = 'https://stagingapi.autographamt.com/v1/auth'
	resp = requests.post(auth_url, {'email': email, 'password': password})
	out = json.loads(resp.text)
	token = out['accessToken']
	return token


# ----------------- add new token translation with all values----------------#
@pytest.mark.skip(reason="need to change the values")
@pytest.mark.parametrize('data',[data])
def test_updatetokentrans(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	project = projectdetails()
	jsondata = jsondump(project[0])
	resp = requests.post(url,data=json.dumps(jsondata), headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == True
	assert out['message'] == "Translation has been inserted"


# ----------------- add same token translation with all values----------------#
@pytest.mark.parametrize('data',[data])
def test_updatetokentrans1(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	project = projectdetails()
	jsondata = jsondump(project[1])
	resp = requests.post(url,data=json.dumps(jsondata), headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == False
	assert out['message'] == "No New change. This data has already been saved"


# --------------------- update token trasnlation with different values--------------------- #
@pytest.mark.parametrize('data',[data])
@pytest.mark.skip(reason="need to change the values")
def test_updatedifftoken(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	project = projectdetails()
	jsondata = jsondump(project[2])
	resp = requests.post(url,data=json.dumps(jsondata), headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert resp.status_code == 200
	assert out['success'] == True
	assert out['message'] == "Translation has been updated"

