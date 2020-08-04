import pytest
import requests
import json

@pytest.fixture
def url():
	# GET API
	return "https://stagingapi.autographamt.com/v1/sources/bibles"


data = [
	('joelcjohnson123@gmail.com', '111111'),     # super admin role
	('ag2@yopmail.com', '1189')                  # normal role
]


def sourcelist():
	data1 = [
			("kad","new india version","niv","2020",1,"CC BY SA"),   # new source details
			("kad","new india version","niv","2020",1,"CC BY SA")    # existing source details
	]
	return data1

def jsondump(data1):
	jsondump = {'languageCode':data1[0],
				'versionContentCode':data1[1],
            	'versionContentDescription':data1[2],
           	 	'year':data1[3],
           	 	'revision': data1[4],
           	 	'license' : data1[5]
	}
	return(jsondump)


# ------------------------- get access token --------------------------- #
def get_accesstoken(email, password):
	auth_url = 'https://stagingapi.autographamt.com/v1/auth'
	resp = requests.post(auth_url, {'email': email, 'password': password})
	out = json.loads(resp.text)
	token = out['accessToken']
	return token


# ----------------- create new source ----------------#
@pytest.mark.skip(reason="need to change the values")
@pytest.mark.parametrize('data',[data])
def test_createsourcenew(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	sources = sourcelist()
	jsondata = jsondump(sources[0])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert out['success'] == True
	assert out['message'] == "Source Created successfully"


# ----------------- create existing source ----------------#
@pytest.mark.skip(reason="need to change the values")
@pytest.mark.parametrize('data',[data])
def test_createsources1(url, data):
	access_token = get_accesstoken(data[0][0], data[0][1])
	sources = sourcelist()
	jsondata = jsondump(sources[1])
	resp = requests.post(url,data=json.dumps(jsondata),headers={'Authorization': 'bearer {}'.format(access_token)})
	out = json.loads(resp.text)
	assert out['success'] == False
	assert out['message'] == "Source already exists"

