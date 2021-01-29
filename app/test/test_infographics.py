'''Test cases for infographics related APIs'''
from . import client
from . import check_default_get, check_soft_delete
from . import assert_input_validation_error, assert_not_available_content
from .test_versions import check_post as add_version
from .test_sources import check_post as add_source

UNIT_URL = '/v2/infographics/'


def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "book" in item
    assert "bookId" in item['book']
    assert "bookCode" in item['book']
    assert "title" in item
    assert "infographicLink" in item

def check_post(data: list):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for infographic",
    }
    add_version(version_data)
    source_data = {
        "contentType": "infographic",
        "language": "urd",
        "version": "TTT",
        "year": 2020,
        "revision": 1
    }
    headers = {"contentType": "application/json", "accept": "application/json"}
    source = add_source(source_data)
    source_name = source.json()['data']['sourceName']
    resp = client.post(UNIT_URL+source_name, headers=headers, json=data)
    return resp, source_name

def test_post_default():
    '''Positive test to upload infographics'''
    data = [
    	{'bookCode':'gen', 'title':"creation", "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'gen', 'title':"abraham's family",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'exo', 'title':"Isarel's travel routes",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"the Gods reveals himself in new testament",
        "infographicLink":"http://somewhere.com/something"},
    ]
    response = check_post(data)[0]
    assert response.status_code == 201
    assert response.json()['message'] == "Infographics added successfully"
    for item in response.json()['data']:
        assert_positive_get(item)
    assert len(data) == len(response.json()['data'])

def test_post_duplicate():
    '''Negative test to add two infographics Links with same book and title'''
    data = [
        {'bookCode':'rev', 'title':"the Gods reveals himself in new testament",
        "infographicLink":"http://somewhere.com/something"}
    ]
    resp, source_name = check_post(data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Infographics added successfully"

    headers = {"contentType": "application/json", "accept": "application/json"}
    data[0]['infographicLink'] = 'http://anotherplace/item'
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    data = {'bookCode':'mat', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"http://somewhere.com/something"}
    resp, source_name = check_post(data)
    assert_input_validation_error(resp)

    # data object with missing mandatory fields
    headers = {"contentType": "application/json", "accept": "application/json"}
    data = [
        {'bookCode':'mat',
        "infographicLink":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    data = [
        {'title':"the Geneology of Jesus Christ",
        "infographicLink":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields

    data = [
        {'bookCode':'mat ', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mathew', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"not a url"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)


    data = [
        {'bookCode':'mat', 'title':"the Geneology of Jesus Christ",
        "infographicLink":"noProtocol.com/something"}
    ]
    response = client.post(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    source_name1 = source_name.replace('infographic', 'info')
    data = []
    response = client.post(UNIT_URL+source_name1, headers=headers, json=data)
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '11')
    response = client.post(UNIT_URL+source_name2, headers=headers, json=[])
    assert response.status_code == 404

def test_get_after_data_upload():
    '''Add some infographics data into the table and do all get tests'''
    data = [
        {'bookCode':'gen', 'title':"creation",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'gen', 'title':"Noah's Ark",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'gen', 'title':"abraham's family",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'exo', 'title':"Isarel's travel routes",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'act', 'title':"Paul's travel routes",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"the Gods reveals himself in new testament",
        "infographicLink":"http://somewhere.com/something"}
    ]
    res, source_name = check_post(data)
    assert res.status_code == 201

    check_default_get(UNIT_URL+source_name, assert_positive_get)

    #filter by book
    response = client.get(UNIT_URL+source_name+'?book_code=gen')
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.get(UNIT_URL+source_name+'?book_code=exo')
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with title introductions
    response = client.get(UNIT_URL+source_name+'?title=creation')
    assert response.status_code == 200
    assert len(response.json()) == 1

    # both title and book
    response = client.get(UNIT_URL+source_name+"?book_code=gen&title=Noah's%20Ark")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # not available
    response = client.get(UNIT_URL+source_name+'?book_code=mat')
    assert_not_available_content(response)

    response = client.get(UNIT_URL+source_name+'?book_code=rev&title=vision')
    assert_not_available_content(response)

def test_get_incorrect_data():
    '''Check for input validations in get'''
    source_name = 'urd_TTT'
    response = client.get(UNIT_URL+source_name)
    assert_input_validation_error(response)

    source_name = 'urd_TTT_1_infographic'
    response = client.get(UNIT_URL+source_name+'?book_code=60')
    assert_input_validation_error(response)

    response = client.get(UNIT_URL+source_name+'?book_code=mark')
    assert_input_validation_error(response)

    resp, source_name = check_post([])
    assert resp.status_code == 201
    source_name = source_name.replace('infographic', 'graphics')
    response = client.get(UNIT_URL+source_name)
    assert response.status_code == 404

def test_put_after_upload():
    '''Positive tests for put'''
    data = [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhere.com/something"}
    ]
    response, source_name = check_post(data)
    assert response.status_code == 201

    # positive PUT
    new_data = [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://anotherplace.com/something"},
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhereelse.com/something"}
    ]
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(UNIT_URL+source_name,headers=headers, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Infographics updated successfully'
    for i,item in enumerate(response.json()['data']):
        assert_positive_get(item)
        assert response.json()['data'][i]['infographicLink'] == new_data[i]['infographicLink']
        assert response.json()['data'][i]['book']['bookCode'] == data[i]['bookCode']
        assert response.json()['data'][i]['title'] == data[i]['title']

    # not available PUT
    new_data[0]['bookCode'] = 'mrk'
    response = client.put(UNIT_URL+source_name, headers=headers, json=new_data)
    assert response.status_code == 404

    source_name = source_name.replace('1', '10')
    response = client.put(UNIT_URL+source_name, headers=headers, json=[])
    assert response.status_code == 404

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''

    post_data = [
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"}
    ]
    resp, source_name = check_post(post_data)
    assert resp.status_code == 201

    # single data object instead of list
    headers = {"contentType": "application/json", "accept": "application/json"}
    data =  {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://anotherplace.com/something"}
    response = client.put(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    # data object with missing mandatory fields
    data = [
        {'title':"12 apostles",
        "infographicLink":"http://anotherplace.com/something"}
            ]
    response = client.put(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mat',
        "infographicLink":"http://somewhere.com/something"}    ]
    response = client.put(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields

    data = [
         {'bookCode':'41', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"}   ]
    response = client.put(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"filename.txt"}    ]
    response = client.put(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    data = [
        {'bookCode':'mat ', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"}    ]
    response = client.put(UNIT_URL+source_name, headers=headers, json=data)
    assert_input_validation_error(response)

    source_name1 = source_name.replace('infographic', 'graphics')
    response = client.put(UNIT_URL+source_name1, headers=headers, json=[])
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '10')
    response = client.put(UNIT_URL+source_name2, headers=headers, json=[])
    assert response.status_code == 404

def test_soft_delete():
    '''check soft delete in infographics'''
    data = [
        {'bookCode':'mat', 'title':"12 apostles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"miracles",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'mat', 'title':"Words of Jesus",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"7 churches of Asia Minor",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"Creatures in Heaven",
        "infographicLink":"http://somewhere.com/something"},
        {'bookCode':'rev', 'title':"All the Sevens",
        "infographicLink":"http://somewhere.com/something"}
    ]

    delete_data = [
        {'bookCode':'rev', 'title':"Creatures in Heaven"},
        {'bookCode':'rev', 'title':"All the Sevens"}
    ]
    check_soft_delete(UNIT_URL, check_post, data, delete_data)
    