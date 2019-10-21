  # -- coding: utf - 8 --
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

# def test_getbibleversetextssup(supply_url,get_supAdmin_accessToken):
# 	url = supply_url + '/v1/bibles/35/verses/pro.7.1'
# 	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	print(j)
# 	# assert j['success'] == False, str(j)
# 	# assert j['message'] == "Invalid book code", str(j)
#   	# assert isinstance(j,list), j
# 	# assert 'sourceId' in j[0], j[0]
# 	# assert 'chapterId' in j[0], j[0]
# 	# assert 'verse' in j[0], j[0]
# 	# print(j)

def test_getbibleversetextsup2(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/bibles/35/verses/pro.7'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Verse id format.", str(j)
  	# assert isinstance(j,list), j
	# assert 'sourceId' in j[0], j[0]
	# assert 'chapter' in j[0], j[0]

def test_getbibleversetextsad(supply_url,get_adm_accessToken):
	url = supply_url + '/v1/bibles/07/verses/pro.7.8'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Source doesn\'t exist", str(j)
    # assert isinstance(j,list),j
	# assert 'sourceId' in j[0], j[0]
	# assert 'books' in j[0], j[0]

# def test_ggetbibleversetextsad2(supply_url,get_adm_accessToken):
# 	url = supply_url + '/v1/bibles/35/chapters/verses'
# 	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == False, str(j)
# 	assert j['message'] == "No verse found", str(j)
#     # assert isinstance(j,list),j
# 	# assert 'sourceId' in j[0], j[0]
# 	# assert 'books' in j[0], j[0]


# def test_getbibleversetextad3(supply_url,get_adm_accessToken):
# 	url = supply_url + '/v1/bibles/35/chapters/verses/pr.2.2'
# 	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == False, str(j)
# 	assert j['message'] == "Invalid Verse id format.", str(j)
#     # assert isinstance(j,list),j
# 	# assert 'sourceId' in j[0], j[0]
# 	# assert 'books' in j[0], j[0]
   

def test_getbibleversetextstr(supply_url,get_trans_accessToken):
	url = supply_url + '/v1/bibles/35/verses/uu'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Verse id format.", str(j)
  



	
	 