 # -- coding: utf - 8 --
import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

def test_Projecttranslation_1(supply_url):
	url = supply_url + '/v1/autographamt/projects/translations/करो/35'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# assert 'translation' in j[0], j[0]
	# assert 'senses' in j[0], j[0]
	assert j['success'] == False, str(j)
	assert j['message'] == "No Translation or sense available for this token", str(j)


def test_Projecttranslation_2(supply_url):
	url = supply_url + '/v1/autographamt/projects/translations/करो/35'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# assert 'translation' in j[0], j[0]
	# assert 'senses' in j[0], j[0]
	assert j['success'] == False, str(j)
	assert j['message'] == "No Translation or sense available for this token", str(j)

def test_Projecttranslation_3(supply_url):
	url = supply_url + '/v1/autographamt/projects/translations/करो/35'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.texts
	assert j['success'] == False, str(j)
	assert j['message'] == "No Translation or sense available for this token", str(j)

# def test_Projecttranslation_4(supply_url):
# 	url = supply_url + '/v1/autographamt/projects/translations/करो/35'
# 	resp = requests.get(url)
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert isinstance(j,list), j
# 	assert len(j)>0
# 	print (j)
def test_Projecttranslation_5(supply_url):
	url = supply_url + '/v1/autographamt/projects/translations/करो/35'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	assert 'translation' in j[0], j[0]
	assert 'senses' in j[0], j[0]