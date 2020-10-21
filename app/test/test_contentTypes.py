from . import client

unit_url = "/v2/contents"

def test_get_default():
	'''positive test case, without optional params'''
    response = client.get()
    assert response.status_code == 200
    assert isInstance( response.json(), list)
    for item in response.json():
    	assert "contentId" in item
    	assert isInstance(item['contentId'], int)
    	assert "contentType" in item

def test_get_limit():
	'''positive test case, with optional param, limit'''
    response = client.get(unit_url+"?limit=3")
    assert response.status_code == 200
    assert isInstance( response.json(), list)
    assert len(response.json()) < 3

def test_get_skip():
	'''positive test case, with optional param, skip'''
	response1 = client.get(unit_url+"?skip=0")
    assert response1.status_code == 200
    assert isInstance( response1.json(), list)
    if len(response1.json()) > 1:
		response2 = client.get(unit_url+"?skip=1")
	    assert response2.status_code == 200
	    assert isInstance( response2.json(), list)
	    assert response1.json()[1] == response2.json()[0]

def test_get_notavailable_contentType():
	''' fetch bible contentType before it is added'''
	response = client.get(unit_url+"?contentType=Bible")
    assert response.status_code == 404
    assert "error" in response.json()
    assert response.json()['error'] == "Requested Content Not Available"


def test_get_notavailable_pagination():
	'''fetch a non existant page, with skip and limit values'''
	response = client.get(unit_url+"?skip=1000;limit=10")
    assert response.status_code == 404
    assert "error" in response.json()
    assert response.json()['error'] == "Requested Content Not Available"

def test_get_incorrectvalue_limit1():
	'''limit should be an integer'''
	response = client.get(unit_url+"?limit=abc")
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()['error'] == "Input validation Error"

def test_get_incorrectvalue_limit2():
	'''limit should be a positive integer'''
	response = client.get(unit_url+"?limit=-1")
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()['error'] == "Input validation Error"

def test_get_incorrectvalue_skip1():
	'''skip should be an integer'''
	response = client.get(unit_url+"?skip=abc")
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()['error'] == "Input validation Error"
    
def test_get_incorrectvalue_skip2():
	'''skip should be a positive integer'''
	response = client.get(unit_url+"?skip=-10")
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()['error'] == "Input validation Error"

def test_post_default():
	'''positive test case, checking for correct return object'''
	data = {"contentType":"Bible"}
	headers = {"contentType": "application/json", "accept": "application/json"}
	response = client.post(unit_url, headers=headers, json=data)
	assert response.status_code == 200
	assert response.json()['message'] == "Content type %s created successfully."%data
	assert response.json()["data"]["contentType"] == data
	assert isInstance(response.json()["data"]["contentId"], int)

def test_get_filterbycontentType():
	'''test again for bible contentType fetch after POST call'''
	response = client.get(unit_url+"?contentType=Bible")
    assert response.status_code == 200
    assert isInstance( response1.json(), list)
    assert response.json()[0]['contentType'] == "Bible"
    assert isInstance(response.json()[0]['contentId'], int) 

def test_post_incorrectdatatype1():
	'''the input data object should a json with "contentType" key within it'''
	data = "Bible"
	headers = {"contentType": "application/json", "accept": "application/json"}
	response = client.post(unit_url, headers=headers, json=data)
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()['error'] == "Input validation Error"

def test_post_incorrectdatatype2():
	'''contentType should not be integer, as per the Database datatype constarints'''
	data = {"contentType":75}
	headers = {"contentType": "application/json", "accept": "application/json"}
	response = client.post(unit_url, headers=headers, json=data)
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()['error'] == "Input validation Error"

def test_post_missingvalue_contenttype():
	'''contentType is mandatory in input data object'''
	data = {}
	headers = {"contentType": "application/json", "accept": "application/json"}
	response = client.post(unit_url, headers=headers, json=data)
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()['error'] == "Input validation Error"

def test_post_incorrectvalue_contenttype():
	''' The contentType name should not contain spaces, as this name would be used for creating tables'''
	data = {"contentType":"Bible Contents"}
	headers = {"contentType": "application/json", "accept": "application/json"}
	response = client.post(unit_url, headers=headers, json=data)
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()['error'] == "Input validation Error"

