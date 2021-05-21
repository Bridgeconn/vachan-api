'''Test cases for bible videos related APIs'''
import json
import re
from . import client
from . import check_default_get
from . import assert_input_validation_error, assert_not_available_content
from .test_sources import check_post as add_source
from .test_versions import check_post as add_version

UNIT_URL = '/v2/bibles/'
headers = {"contentType": "application/json", "accept": "application/json"}

gospel_books_data = [
        {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id mrk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
]

audio_data = [
  {
    "name": "matthew recording",
    "url": "https://www.somewhere.com/file_mat",
    "books": [
      "mat"
    ],
    "format": "mp3"
  },
  {
    "name": "John recording",
    "url": "https://www.somewhere.com/file_jhn",
    "books": [
      "jhn"
    ],
    "format": "string"
  },
  {
    "name": "letters of John",
    "url": "https://www.somewhere.com/file_jhn_letters",
    "books": [
      "1jn", "2jn", "3jn"
    ],
    "format": "mp3"
  },
  {
    "name": "last books",
    "url": "https://www.somewhere.com/file_rev",
    "books": [
      "rev"
    ],
    "format": "mp3"
  }
]

def assert_positive_get_for_books(item):
    '''Check for the properties in the normal return object'''
    assert "book" in item
    assert  isinstance(item['book'], dict)
    assert "bookId" in item['book']
    assert "bookCode" in item['book']
    assert "bookName" in item['book']
    assert "active" in item

def assert_positive_get_for_verse(item):
    '''Check for the properties in the normal return object'''
    assert "verseText" in item
    assert "reference" in item
    assert "book" in item['reference']
    assert  isinstance(item['reference']['book'], str)
    assert "chapter" in item['reference']
    assert "verseNumber" in item['reference']

def assert_positive_get_for_audio(item):
    '''Check for the properties in the normal return object'''
    assert "name" in item
    assert "url" in item
    assert "format" in item
    assert "active" in item

def check_post(data: list, datatype='books'):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for bibles",
    }
    add_version(version_data)
    source_data = {
        "contentType": "bible",
        "language": "gu",
        "version": "TTT",
        "year": 3030,
        "revision": 1
    }
    source = add_source(source_data)
    table_name = source.json()['data']['sourceName']
    if datatype == 'audio':
        resp = client.post(UNIT_URL+table_name+'/audios', headers=headers, json=data)
    else:
        resp = client.post(UNIT_URL+table_name+'/books', headers=headers, json=data)
    return resp, table_name

def test_post_default():
    '''Positive test to upload bible videos'''

    resp = check_post(gospel_books_data)[0]
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"
    for i,item in enumerate(resp.json()['data']):
        assert_positive_get_for_books(item)
        book_code = re.match(r'\\id (\w\w\w)', gospel_books_data[i]['USFM']).group(1)
        assert item['book']['bookCode'] == book_code.lower()
    assert len(gospel_books_data) == len(resp.json()['data'])

def test_post_duplicate():
    '''test posting the same book twice'''
    data = gospel_books_data[:1]
    resp, table = check_post(data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"

    data2 = gospel_books_data[:1]
    resp2 = client.post(UNIT_URL+table+'/books', headers=headers, json=data2)
    assert resp2.status_code == 409
    assert resp2.json()['error'] == "Already Exists"

    # # same book repeated in one set
    # data3 = [gospel_books_data[3], gospel_books_data[3]]
    # resp3 = client.post(UNIT_URL+table+'/books', headers=headers, json=data3)
    # assert resp3.status_code == 409
    # assert resp3.json()['error'] == "Already Exists"

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    one_row = gospel_books_data[0]
    resp, source_name = check_post(one_row)
    assert_input_validation_error(resp)

    # data object with missing mandatory fields
    data = [
        {'usfm': '\\id gen\\c 1\\p\\v 1 test content'}
    ]
    response = client.post(UNIT_URL+source_name+"/books", headers=headers, json=data)
    assert_input_validation_error(response)

    data = [{'JSON':gospel_books_data[0]['USFM']}]
    response = client.post(UNIT_URL+source_name+"/books", headers=headers, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields
    data = [
            {'USFM': '<id gen><c 1><p><v 1 test content>'}
    ]
    response = client.post(UNIT_URL+source_name+"/books", headers=headers, json=data)
    assert response.status_code ==415
    assert "USFM is not of the required format" in response.json()['details']

    source_name1 = source_name.replace('bible', 'video')
    data = []
    response = client.post(UNIT_URL+source_name1+'/books', headers=headers, json=data)
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '7')
    response = client.post(UNIT_URL+source_name2+'/books', headers=headers, json=[])
    assert response.status_code == 404

def test_post_audio():
    '''Test the API for audio bible info upload'''
    resp, source_name = check_post(audio_data, 'audio')
    assert resp.status_code == 201
    assert len(resp.json()['data']) == 6
    assert resp.json()['message'] == "Bible audios details uploaded successfully"
    for item in resp.json()['data']:
        assert_positive_get_for_audio(item)

    #attempt duplicate
    resp2 = client.post(UNIT_URL+source_name+'/audios', json=audio_data[:1], headers=headers)
    assert resp2.status_code == 409
    assert resp2.json()['error'] == "Already Exists"

    #incorrect data
    resp3 = client.post(UNIT_URL+source_name+'/audios', json=audio_data[0], headers=headers)
    assert_input_validation_error(resp3)

    wrong_data = [audio_data[0].copy()]
    wrong_data[0]['url'] = 'not a valid url'
    resp4 = client.post(UNIT_URL+source_name+'/audios', json=wrong_data[0], headers=headers)
    assert_input_validation_error(resp4)

    wrong_data = [audio_data[0].copy()]
    wrong_data[0]['books'] = ["not a valid book"]
    resp5 = client.post(UNIT_URL+source_name+'/audios', json=wrong_data[0], headers=headers)
    assert_input_validation_error(resp5)

    wrong_data = [audio_data[0].copy()]
    wrong_data[0]['books'] = 'gen'
    resp6 = client.post(UNIT_URL+source_name+'/audios', json=wrong_data[0], headers=headers)
    assert_input_validation_error(resp6)

def test_put_books():
    '''adds some books and change them using put APIs'''
    resp, src = check_post(gospel_books_data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"

    #update without specifying the book code
    update_data = [{
        "USFM": "\\id mat\n\\c 1\n\\p\n\\v 1 new content for matthew"}]
    response1 = client.put(UNIT_URL+src+"/books", json=update_data, headers=headers)
    assert response1.status_code == 201
    assert response1.json()['message'] == "Bible books updated successfully"
    assert len(response1.json()['data']) == 1
    assert_positive_get_for_books(response1.json()['data'][0])
    assert response1.json()['data'][0]["USFM"] == update_data[0]["USFM"]
    assert response1.json()['data'][0]["book"]["bookCode"] == "mat"

    #only with JSON
    update_data[0]["USFM"] = None
    response2 = client.put(UNIT_URL+src+"/books", json=update_data, headers=headers)
    assert_input_validation_error(response2)


    #to change status
    update_data = [
        {"active": False, "bookCode":"jhn"}
    ]
    response4 = client.put(UNIT_URL+src+"/books", json=update_data, headers=headers)
    assert response4.status_code == 201
    assert response4.json()['message'] == "Bible books updated successfully"
    assert len(response4.json()['data']) == 1
    assert_positive_get_for_books(response4.json()['data'][0])
    assert not response4.json()['data'][0]["active"]
    assert response4.json()['data'][0]["book"]["bookCode"] == "jhn"

    #not available book
    update_data = [
        {"active": False, "bookCode":"rev"}
    ]
    response5 = client.put(UNIT_URL+src+"/books", json=update_data, headers=headers)
    assert response5.status_code == 404
    assert response5.json()['error'] == "Requested Content Not Available"


def test_put_audios():
    '''Add some audios and change them afterwards using PUT'''
    resp, source = check_post(audio_data, 'audio')
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible audios details uploaded successfully"

    update_data = [
    {
        "books": ['mat'],
        "url":"https://www.someotherplace.com/mat_file"
    }]
    response = client.put(UNIT_URL+source+'/audios', json=update_data, headers=headers)
    assert response.status_code == 201
    assert response.json()['message'] == "Bible audios details updated successfully"
    assert response.json()['data'][0]['url'] == 'https://www.someotherplace.com/mat_file'

    #missing books info
    update_data = [
    {
        "format": 'mp3',
        "url":"https://www.someotherplace.com/mat_file"
    }]
    response1 = client.put(UNIT_URL+source+'/audios', json=update_data, headers=headers)
    assert_input_validation_error(response1)

    # invalid data
    update_data = [{
        "books": ['mat'],
        "active":"noooo"
    }]
    response2 = client.put(UNIT_URL+source+'/audios', json=update_data, headers=headers)
    assert_input_validation_error(response2)

    update_data = [{
        "books": ['mat'],
        "url":"invalid url"
    }]
    response2 = client.put(UNIT_URL+source+'/audios', json=update_data, headers=headers)
    assert_input_validation_error(response2)

def test_get_books_contenttype():
    '''Add some books data into the table and do content type related get tests'''
    res, source_name = check_post(gospel_books_data)
    assert res.status_code == 201

    check_default_get(UNIT_URL+source_name+"/books", assert_positive_get_for_books)

    # content_type
    response = client.get(UNIT_URL+source_name+'/books')
    assert response.status_code == 200
    assert len(response.json()) == len(gospel_books_data)
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" not in res
        assert "JSON" not in res
        assert "audio" not in res

    response = client.get(UNIT_URL+source_name+'/books?content_type=usfm')
    assert response.status_code == 200
    assert len(response.json()) == len(gospel_books_data)
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" in res
        assert "JSON" not in res
        assert "audio" not in res

    response = client.get(UNIT_URL+source_name+'/books?content_type=json')
    assert response.status_code == 200
    assert len(response.json()) == len(gospel_books_data)
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" not in res
        assert "JSON" in res
        assert "audio" not in res

    response = client.get(UNIT_URL+source_name+'/books?content_type=all')
    assert response.status_code == 200
    assert len(response.json()) == len(gospel_books_data)
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" in res
        assert "JSON" in res
        assert "audio" in res

    response = client.get(UNIT_URL+source_name+'/books?book_code=mat&content_type=audio')
    assert_not_available_content(response)

    # add audio
    resp = client.post(UNIT_URL+source_name+'/audios', json=audio_data, headers=headers)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible audios details uploaded successfully"

    response = client.get(UNIT_URL+source_name+'/books?content_type=audio')
    assert response.status_code == 200
    assert len(response.json()) == 6
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" not in res
        assert "JSON" not in res
        assert "audio" in res
        assert res['audio'] is not None

    # not available
    response = client.get(UNIT_URL+source_name+'/books?book_code=jud')
    assert_not_available_content(response)


def test_get_books_filter():
    '''add some usfm and audio data and test get api based on book_code and active filters '''
    res, source_name = check_post(gospel_books_data)
    assert res.status_code == 201

    # book_code without audio data
    response = client.get(UNIT_URL+source_name+'/books?book_code=mat')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['book']['bookCode'] == 'mat'

    resp = client.post(UNIT_URL+source_name+'/audios', json=audio_data, headers=headers)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible audios details uploaded successfully"
    added_books = ['mat', 'mrk', 'luk', 'jhn', '1jn', '2jn', '3jn', 'rev']

    resp = client.get(UNIT_URL+source_name+'/books')
    assert resp.status_code == 200
    assert len(resp.json()) == 8
    assert resp.json()[0]['book']['bookCode'] in added_books

    # book_code after uploading audio data
    response = client.get(UNIT_URL+source_name+'/books?book_code=mat')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['book']['bookCode'] == 'mat'

    response = client.get(UNIT_URL+source_name+'/books?book_code=rev')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['book']['bookCode'] == 'rev'

    # active filter
    res1 = client.get(UNIT_URL+source_name+'/books')
    res2 = client.get(UNIT_URL+source_name+'/books?active=True')
    assert res1.status_code == res2.status_code
    assert res1.json() == res2.json()

    res3 = client.get(UNIT_URL+source_name+'/books?active=False')
    assert_not_available_content(res3)

def test_get_books_versification():
    '''add some usfm and audio data and test get api based on book_code and active filters '''
    res, source_name = check_post(gospel_books_data)
    assert res.status_code == 201

    response = client.get(UNIT_URL+source_name+'/books?versification=True')
    assert response.status_code == 200
    assert len(response.json()) == 4
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" not in res
        assert "JSON" not in res
        assert "audio" not in res
        assert res['versification'] is not None

    resp = client.post(UNIT_URL+source_name+'/audios', json=audio_data, headers=headers)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible audios details uploaded successfully"

    #versification for books after adding audio
    only_audio_books = ['1jn', '2jn', '3jn', 'rev']
    response = client.get(UNIT_URL+source_name+'/books?versification=True')
    assert response.status_code == 200
    assert len(response.json()) == 8
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" not in res
        assert "JSON" not in res
        assert "audio" not in res
        assert res["versification"] is not None
        if res['book']['bookCode'] in only_audio_books:
            assert res['versification'] == []

    #versification for books with only audio
    response = client.get(UNIT_URL+source_name+'/books?versification=True&book_code=rev')
    assert response.status_code == 200
    assert response.json()[0]['versification'] == []

    #versification along with other filters
    response = client.get(UNIT_URL+source_name+'/books?versification=True&content_type=usfm')
    assert response.status_code == 200
    for res in response.json():
        assert 'versification' in res
        assert 'USFM' in res
        if res['book']['bookCode'] in only_audio_books:
            assert res['USFM'] is None

    response = client.get(UNIT_URL+source_name+'/books?versification=True&content_type=json')
    assert response.status_code == 200
    for res in response.json():
        assert 'versification' in res
        assert 'JSON' in res
        if res['book']['bookCode'] in only_audio_books:
            assert res["JSON"] is None

def test_get_verses():
    '''Upload some bibles and fetch verses'''
    res, source_name = check_post(gospel_books_data)
    assert res.status_code == 201

    response = client.get(UNIT_URL+source_name+'/verses')
    assert response.status_code == 200
    assert len(response.json()) == 8
    for item in response.json():
        assert_positive_get_for_verse(item)

    response = client.get(UNIT_URL+source_name+'/verses?book_code=mat')
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+source_name+'/verses?book_code=mrk&chapter=1')
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+source_name+'/verses?book_code=mat&chapter=1&verse=1')
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(UNIT_URL+source_name+ \
        '/verses?book_code=mat&chapter=1&verse=1&last_verse=10')
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+source_name+'/verses?book_code=mat&chapter=1&verse=10')
    assert_not_available_content(response)

    response = client.get(UNIT_URL+source_name+\
        '/verses?book_code=mat&chapter=1&verse=10&last_verse=20')
    assert_not_available_content(response)

    response = client.get(UNIT_URL+source_name+'/verses?book_code=act&chapter=1&verse=10')
    assert_not_available_content(response)

    # add audio
    resp = client.post(UNIT_URL+source_name+'/audios', json=audio_data, headers=headers)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible audios details uploaded successfully"

    response = client.get(UNIT_URL+source_name+'/verses?book_code=rev&chapter=1&verse=10')
    assert_not_available_content(response)


def test_audio_delete():
    '''add data, update active field with put and try get apis with active filters'''
    res, source_name = check_post(audio_data, "audio")
    assert res.status_code == 201
    assert res.json()['message'] == "Bible audios details uploaded successfully"

    res1 = client.get(UNIT_URL+source_name+'/books')
    assert res1.status_code == 200
    assert len(res1.json()) == 6

    res2 = client.get(UNIT_URL+source_name+'/books?content_type=audio')
    assert res2.status_code == 200
    assert len(res2.json()) == 6

    # delete one audio
    update_data = [{"books":["mat"], "active":False}]
    res3 = client.put(UNIT_URL+source_name+'/audios', json=update_data, headers=headers)
    assert res3.status_code == 201
    assert not res3.json()['data'][0]['active']

    res4 = client.get(UNIT_URL+source_name+'/books?content_type=audio')
    res5 = client.get(UNIT_URL+source_name+'/books')
    res6 = client.get(UNIT_URL+source_name+'/books?content_type=audio&active=False')
    assert res4.status_code == 200
    assert len(res4.json()) == 5
    assert res5.status_code == 200
    assert len(res5.json()) == 6
    assert res6.status_code == 200
    assert len(res6.json()) == 1

    # Add bibles
    resp = client.post(UNIT_URL+source_name+'/books', json=gospel_books_data, headers=headers)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"

    res4 = client.get(UNIT_URL+source_name+'/books?content_type=audio')
    res5 = client.get(UNIT_URL+source_name+'/books')
    res6 = client.get(UNIT_URL+source_name+'/books?content_type=audio&active=False')
    assert res4.status_code == 200
    assert len(res4.json()) == 5
    assert res5.status_code == 200
    assert len(res5.json()) == 8
    assert res6.status_code == 200
    assert len(res6.json()) == 1

    # try delete non-existant audio
    update_data = [{"books":["mrk"], "active":False}]
    res3 = client.put(UNIT_URL+source_name+'/audios', json=update_data, headers=headers)
    assert res3.status_code == 404

    # delete audio but not book
    update_data = [{"books":["jhn"], "active":False}]
    res3 = client.put(UNIT_URL+source_name+'/audios', json=update_data, headers=headers)
    assert res3.status_code == 201
    res4 = client.get(UNIT_URL+source_name+'/books?book_code=jhn&content_type=audio')
    res5 = client.get(UNIT_URL+source_name+'/books?book_code=jhn&content_type=usfm')
    assert_not_available_content(res4)
    assert res5.status_code == 200
    assert len(res5.json()) == 1


def test_book_delete():
    '''add data, update active field with put and try get apis with active filters'''

    resp, source = check_post(gospel_books_data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"

    res1 = client.get(UNIT_URL+source+'/books')
    res2 = client.get(UNIT_URL+source+'/verses')
    assert res1.status_code == 200
    assert len(res1.json()) == 4
    assert res2.status_code == 200
    assert len(res2.json()) == 8

    update_data = [
        {"bookCode": "mat", "active":False}
    ]
    resp = client.put(UNIT_URL+source+'/books', json=update_data, headers=headers)
    assert resp.status_code == 201

    res1 = client.get(UNIT_URL+source+'/books')
    res2 = client.get(UNIT_URL+source+'/verses')
    assert res1.status_code == 200
    assert len(res1.json()) == 3
    assert res2.status_code == 200
    assert len(res2.json()) == 6

    res1 = client.get(UNIT_URL+source+'/books?active=false')
    res2 = client.get(UNIT_URL+source+'/verses?active=false')
    assert res1.status_code == 200
    assert len(res1.json()) == 1
    assert res2.status_code == 200
    assert len(res2.json()) == 2

    res1 = client.get(UNIT_URL+source+'/books?book_code=mat')
    res2 = client.get(UNIT_URL+source+'/verses?book_code=mat')
    assert_not_available_content(res1)
    assert_not_available_content(res2)

    # add audio
    resp = client.post(UNIT_URL+source+'/audios', json=audio_data, headers=headers)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible audios details uploaded successfully"

    res1 = client.get(UNIT_URL+source+'/books?content_type=audio')
    res2 = client.get(UNIT_URL+source+'/books?content_type=all')
    assert res1.status_code == 200
    assert len(res1.json()) == 6
    assert res2.status_code == 200
    assert len(res2.json()) == 8
