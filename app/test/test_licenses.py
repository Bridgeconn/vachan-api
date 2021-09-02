'''Test cases for licenses related APIs'''
from . import client, check_default_get
from . import assert_input_validation_error, assert_not_available_content

UNIT_URL = '/v2/licenses'
headers = {"contentType": "application/json", "accept": "application/json"}

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "license" in item
    assert "name" in item
    assert "code" in item
    assert "permissions" in item
    assert isinstance(item['permissions'], list)
    assert "active" in item

def test_get():
    '''positive test case, without optional params'''
    check_default_get(UNIT_URL, assert_positive_get)

    # '''positive test case, with one optional params, code'''
    response = client.get(UNIT_URL+'?license_code=ISC')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'ISC'

    # '''positive test case, with one optional params, code in lower case'''
    response = client.get(UNIT_URL+'?license_code=isc')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'ISC'

    # '''positive test case, with one optional params, name'''
    response = client.get(UNIT_URL+'?license_name=Creative%20Commons%20License')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['code'] == 'CC-BY-SA'

    # '''positive test case, with two optional params'''
    response = client.get(UNIT_URL+'?license_code=ISC&active=true')
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) == 1
    assert_positive_get(response.json()[0])
    assert response.json()[0]['active']
    assert response.json()[0]['code'] == 'ISC'

    # ''' request a not available license, with code'''
    response = client.get(UNIT_URL+"?license_code=aaj")
    assert_not_available_content(response)

    # '''filter with permissions'''
    response = client.get(UNIT_URL+'?permission=Commercial_use')
    assert response.status_code == 200
    assert len(response.json()) == 2

    # ''' request a not available license, with license name'''
    response = client.get(UNIT_URL+"?license_name=not-a-license")
    assert_not_available_content(response)

    # '''license code should not have spaces'''
    response = client.get(UNIT_URL+"?license_code=ISC%20II")
    assert_input_validation_error(response)

    # '''permissions should take only predefined values'''
    response = client.get(UNIT_URL+"?permission=abcd")
    assert_input_validation_error(response)

def test_post():
    '''positive test case, checking for correct return object'''
    data = {
      "license": "A very very long license text",
      "name": "Test License version 1",
      "code": "LIC-1",
      "permissions": ["Private_use"]
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "License uploaded successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "LIC-1"

    # '''positive test case, checking for case conversion of code'''
    data["code"]= "lic-2"
    data['name']= "Test License version 2"

    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "License uploaded successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["code"] == "LIC-2"

    # '''positive test case, checking without permissions'''
    data = {
        "code": "lic-3",
        "name": "Test License version 3",
        "license": "a long long long text"
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "License uploaded successfully"
    assert_positive_get(response.json()['data'])
    assert response.json()["data"]["permissions"] == ["Private_use"]

    # '''without mandatory fields'''
    data = {
        "code": "lic-4",
        "name": "Test License version 4",
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    data = {
        "code": "lic-4",
        "license": "Test License version 4",
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    data = {
        "license": "long long text",
        "name": "Test License version 4",
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    # '''code should have letters numbers  . _ or - only'''
    data = {
      "license": "new-lang",
      "code": "AB@",
      "name": "new name"
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    data = {
      "license": "new-lang",
      "code": "AB 1",
      "name": "new name"
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

    # '''permissions should be from the pre-defined list'''
    data = {
      "license": "new- license text",
      "code": "MMM",
      "name": "new name",
      "permissions": ["regular"]
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert_input_validation_error(response)

def test_put():
    '''Add a new license and then alter it'''
    data = {
      "license": "A very very long license text",
      "code": "LIC-1",
      "name": "Test License version 1",
      "permissions": ["Private_use"]
    }
    response = client.post(UNIT_URL, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "License uploaded successfully"

    update_data = {"code":"LIC-1", "permissions":["Private_use", "Patent_use"]}
    response = client.put(UNIT_URL, json=update_data, headers=headers)
    assert response.status_code == 201
    assert response.json()['message'] == "License edited successfully"
    assert response.json()['data']['permissions'] == ["Private_use", "Patent_use"]

    update_data = {"code":"LIC-1", "name":"New name for test license"}
    response = client.put(UNIT_URL, json=update_data, headers=headers)
    assert response.status_code == 201
    assert response.json()['message'] == "License edited successfully"
    assert response.json()['data']['name'] == "New name for test license"

    update_data = {"code":"LIC-1", "license":"A different text"}
    response = client.put(UNIT_URL, json=update_data, headers=headers)
    assert response.status_code == 201
    assert response.json()['message'] == "License edited successfully"
    assert response.json()['data']['license'] == "A different text"

    # unavailable code
    update_data['code'] = "LIC-2"
    response = client.put(UNIT_URL, json=update_data, headers=headers)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"

    #without code
    update_data = {"name": "some name", "active":False}
    response = client.put(UNIT_URL, json=update_data, headers=headers)
    assert_input_validation_error(response)

    #deactivate or soft-delete
    resp1 = client.get(UNIT_URL)
    assert resp1.status_code == 200
    assert len(resp1.json()) >= 3

    update_data = {"code": "LIC-1", "active":False}
    response = client.put(UNIT_URL, json=update_data, headers=headers)
    assert response.status_code == 201

    resp2 = client.get(UNIT_URL)
    assert resp1.status_code == 200
    assert len(resp1.json()) - len(resp2.json()) == 1