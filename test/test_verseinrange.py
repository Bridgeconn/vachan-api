#-*-coding:utf-8-*-
import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"


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

def test_verseinrangesup(supply_url,get_supAdmin_accessToken):
	url = supply_url +'/v1/sources/39/json/43/1'
	resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	# for x in j:
	# 	print(x.encode("utf-8"))
	assert resp.status_code == 200, resp.text


def test_verseinrangesup2(supply_url,get_supAdmin_accessToken):
    url = supply_url +'/v1/sources/39/json/9/5'
    resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_supAdmin_accessToken)})
    j = json.loads(resp.text)
    assert resp.status_code == 200, resp.text 
    
	
def test_verseinrangesup3(supply_url,get_supAdmin_accessToken):
    url = supply_url +'/v1/sources/9/usfm/43/1'
    resp = requests.get(url,headers={'Authorization': 'bearer{}'.format(get_supAdmin_accessToken)})
    j = json.loads(resp.text)
    assert resp.status_code == 200, resp.text 
    assert j['success'] == False, str(j)
    assert j['message'] == "Source File not available. Create source", str(j)



	
	 