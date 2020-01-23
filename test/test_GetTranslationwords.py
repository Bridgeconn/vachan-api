  # -- coding: utf - 8 --
import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

def test_getTranslationwords_1(supply_url):
	url = supply_url + '/v1/translationshelps/words/30/करो'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert isinstance(j,list), j
	# assert len(j)>0
	print (j)

def test_getTranslationwords_2(supply_url):
	url = supply_url + '/v1/translationshelps/words/30/करो'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert j['success'] == False, str(j)
	# assert j['message'] == "No Translation or sense available for this token", str(j)
        print (j)

def test_getTranslationwords_3(supply_url):
	url = supply_url + '/v1/translationshelps/words/01/करो'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert j['success'] == False, str(j)
	# assert j['message'] == "Invalid source ID", str(j)
        print (j)