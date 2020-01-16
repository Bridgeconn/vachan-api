  # -- coding: utf - 8 --
import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

def test_generateconcordance_SuperAdmin(supply_url):
	url = supply_url + '/v1/concordances/35/2ti/करो'
	resp = requests.get(url)
	j = json.loads(resp.text)
	for x in j:
		print(x.encode("utf-8"))
	assert resp.status_code == 200, resp.text
	print(j)

# def test_generateconcordance_(supply_url):
# 	url = supply_url + '/v1/concordances/35/heb/करो'
# 	resp = requests.get(url)
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert isinstance(j,list), j
# 	# new_j = [x.encode('utf-8') for x in j]
#  	# print(new_j)
#     	 # print(j)
# 	# assert 'all' in j[0], j[0]
	
# def test_generateconcordancesad(supply_url,get_accessTokenad):
# 	url = supply_url + '/v1/concordances/35/heb/करो'
# 	resp = requests.get(url)
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert isinstance(j,list), j
# 	# new_j = [x.encode('utf-8') for x in j]
#  	# print(new_j)
#     	# print(j)
# 	# assert 'all' in j[0], j[0]
	
