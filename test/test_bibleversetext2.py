  # -- coding: utf - 8 --
import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"


def test_getbibleversetexts(supply_url):
	url = supply_url + '/v1/bibles/35/verses/pro.7.1'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert 'sourceId' in j
	assert 'chapterNumber' in j
	assert 'verseContent' in j

def test_getbibleversetextsup2(supply_url):
	url = supply_url + '/v1/bibles/35/verses/pro.7'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Verse id format.", str(j)

def test_getbibleversetextsad(supply_url):
	url = supply_url + '/v1/bibles/07/verses/pro.7.8'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Source doesn\'t exist", str(j)

  

def test_getbibleversetextstr(supply_url):
	url = supply_url + '/v1/bibles/35/verses/uu'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Verse id format.", str(j)
  



	
	 