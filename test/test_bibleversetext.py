  # -- coding: utf - 8 --
import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"



def test_getbibleverses(supply_url):
	url = supply_url + '/v1/bibles/35/books/PRO/chapters/7/verses/17'
	resp = requests.get(url)
	j = json.dumps(resp.text)
	assert resp.status_code == 200, resp.text
	assert 'bibleBookCode'in j
	assert 'sourceId' in j
	assert 'reference' in j
	assert 'verseNumber' in j
	assert 'chapterNumber' in j
	
def test_getbibleverseup2(supply_url):
	url = supply_url + '/v1/bibles/89/books/pro/chapters/2/verses/18'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Source doesn't exist", str(j)
 

def test_getbibleversead(supply_url):
	url = supply_url + '/v1/bibles/35/books/55/chapters/3/verses/1'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid book code", str(j)
 

def test_getbibleversestr(supply_url):
	url = supply_url + '/v1/bibles/35/books/3jn/chapters/2/verses/4'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "No verse found", str(j)

  
	



	
	 
