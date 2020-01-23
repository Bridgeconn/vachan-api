import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

# def test_getbiblebookchapters_1(supply_url):
# 	url = supply_url + '/v1/bibles/35/books-chapters"'
# 	resp = requests.get(url)
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	assert isinstance(j,list), j
#     assert len(j)>0
#     print(j)

def test_getbiblebookchapters_2(supply_url):
	url = supply_url + '/v1/bibles/2/books-chapters"'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	# assert j['success'] == False, str(j)
	# assert j['message'] == "No Books uploaded yet", str(j)
	print(j)

def test_getbiblebookchapters_3(supply_url):
	url = supply_url + '/v1/bibles/10/books-chapters"'
	resp = requests.get(url)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert j['success'] == False, str(j)
	assert j['message'] == "Invalid Source Id", str(j)