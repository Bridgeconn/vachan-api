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

@pytest.mark.parametrize('userId,projectId',[("32","35")])
def test_delete_Projectassignment_1(supply_url,get_supAdmin_accessToken,userId,projectId):
	url = supply_url + "/v1/autographamt/projects/assignments"
	data = {'userId':userId,
            'projectId': projectId
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "User Role Does Not exist"


@pytest.mark.parametrize('userId,projectId',[("32","3")])
def test_delete_Projectassignment_2(supply_url,get_supAdmin_accessToken,userId,projectId):
	url = supply_url + "/v1/autographamt/projects/assignments"
	data = {'userId':userId,
            'projectId': projectId
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "User Role Does Not exist"


@pytest.mark.parametrize('userId,projectId',[("32","35")])
def test_delete_Projectassignment_3(supply_url,get_supAdmin_accessToken,userId,projectId):
	url = supply_url + "/v1/autographamt/projects/assignments"
	data = {'userId':userId,
            'projectId': projectId
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "User Role Does Not exist"

# @pytest.mark.parametrize('userEmail',[('shawn@yopmail.com')])
# def test_activatesource_1(supply_url,get_supAdmin_accessToken,userEmail):
# 	url = supply_url + '/v1/autographamt/user/activate'
# 	data = {
# 			'userEmail':userEmail
# 			}
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == True, str(j)
# 	assert j['message'] == "User re-activated", str(j)

# @pytest.mark.parametrize('userId,projectId',[("12","12")])
# def test_delete_Projectassignment_5(supply_url,get_supAdmin_accessToken,userId,projectId):
# 	url = supply_url + "/v1/autographamt/projects/assignments"
# 	data = {'userId':userId,
#             'projectId': projectId
# 	}
# 	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200
# 	assert j['message'] == "User removed from Project"

# @pytest.mark.parametrize('userEmail',[('shawn@yopmail.com')])
# def test_activatesource_2(supply_url,get_supAdmin_accessToken,userEmail):
# 	url = supply_url + '/v1/autographamt/user/activate'
# 	data = {
# 			'userEmail':userEmail
# 			}
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == True, str(j)
# 	assert j['message'] == "User re-activated", str(j)

@pytest.mark.parametrize('userID,projectID,Books',[(30,52,["mat"])])
def test_projectassignment_existingTranslator1(supply_url,userID, projectID,Books):
	url = supply_url + '/v1/autographamt/projects/assignments'
	data = {'userId': userID,
			'projectId': projectID,
			'books': Books
			}
	resp = requests.post(url,data=json.dumps(data))
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "User Role Assigned", str(j)



@pytest.mark.parametrize('userId,projectId',[("30","52")])
def test_delete_Projectassignment_6(supply_url,userId,projectId):
	url = supply_url + "/v1/autographamt/projects/assignments"
	data = {'userId':userId,
            'projectId': projectId
	}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "User removed from Project"