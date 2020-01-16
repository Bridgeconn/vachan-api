#-*-coding:utf-8-*-
import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

# def test_GetTokenList_SuperAdmin(supply_url):
# 	url = supply_url + '/v1/tokenlist/35/heb'
# 	resp = requests.get(url)
# 	j = json.loads(resp.text)
# 	for x in j:
# 		print(x.encode("utf-8"))
# 	assert resp.status_code == 200, resp.text
# 	print(j)



# def test_GetTokenList_SuperAdmin2(supply_url):
# 	url = supply_url + '/v1/tokenlist/35/heb'
# 	resp = requests.get(url)
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == False, str(j)
# 	assert j['message'] == "Phrases method error", str(j)

def test_GetTokenList(supply_url):
	url = supply_url + '/v1/tokenlist/35/2ti'
	resp = requests.get(url)
	j = json.loads(resp.text)
	for x in j:
		print(x.encode("utf-8"))
	assert resp.status_code == 200, resp.text

# def test_GetTokenList_2(supply_url):
# 	url = supply_url + '/v1/tokenlist/35/2ti'
# 	resp = requests.get(url)
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == False, str(j)
# 	assert j['message'] == "Phrases method error", str(j)
# 	# assert isinstance(j,list), j
# 	# assert len(j)>0
	

# def test_GetTokenList_Translator(supply_url):
# 	url = supply_url + '/v1/tokenlist/35/2jn'
# 	resp = requests.get(url)
# 	j = json.loads(resp.text)
# 	for x in j:
# 		print(x.encode("utf-8"))
# 	assert resp.status_code == 200, resp.text
	
# def test_GetTokenList_Translator2(supply_url):
# 	url = supply_url + '/v1/tokenlist/35/2jn'
# 	resp = requests.get(url)
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert j['success'] == False, str(j)
# 	assert j['message'] == "Phrases method error", str(j)
  
