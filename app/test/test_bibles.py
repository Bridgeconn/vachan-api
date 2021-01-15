'''Test cases for bible videos related APIs'''
import json
from . import client
from . import check_default_get, check_soft_delete
from . import assert_input_validation_error, assert_not_available_content
from .test_sources import check_post as add_source
from .test_versions import check_post as add_version

UNIT_URL = '/v2/bibles/'
headers = {"contentType": "application/json", "accept": "application/json"}

gospel_books_data = [
        {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":json.loads('''{
    "book": {
        "bookCode": "MAT"
    },
    "chapters": [
        {
            "chapterNumber": "1",
            "contents": [
                {
                    "p": null
                },
                {
                    "verseNumber": "1",
                    "verseText": "test verse one",
                    "contents": [
                        "test verse one"
                    ]
                },
                {
                    "verseNumber": "2",
                    "verseText": "test verse two",
                    "contents": [
                        "test verse two"
                    ]
                }
            ]
        }
    ],
    "_messages": {
        "_warnings": [
            "Empty lines present. ",
            "Book code is in lowercase. "
        ]
    }
}''')},    
        {"USFM":"\\id mrk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":json.loads('''{
    "book": {
        "bookCode": "MRK"
    },
    "chapters": [
        {
            "chapterNumber": "1",
            "contents": [
                {
                    "p": null
                },
                {
                    "verseNumber": "1",
                    "verseText": "test verse one",
                    "contents": [
                        "test verse one"
                    ]
                },
                {
                    "verseNumber": "2",
                    "verseText": "test verse two",
                    "contents": [
                        "test verse two"
                    ]
                }
            ]
        }
    ],
    "_messages": {
        "_warnings": [
            "Empty lines present. ",
            "Book code is in lowercase. "
        ]
    }
}''')},    
        {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":json.loads('''{
    "book": {
        "bookCode": "LUK"
    },
    "chapters": [
        {
            "chapterNumber": "1",
            "contents": [
                {
                    "p": null
                },
                {
                    "verseNumber": "1",
                    "verseText": "test verse one",
                    "contents": [
                        "test verse one"
                    ]
                },
                {
                    "verseNumber": "2",
                    "verseText": "test verse two",
                    "contents": [
                        "test verse two"
                    ]
                }
            ]
        }
    ],
    "_messages": {
        "_warnings": [
            "Empty lines present. ",
            "Book code is in lowercase. "
        ]
    }
}''')},    
        {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":json.loads('''{
    "book": {
        "bookCode": "JHN"
    },
    "chapters": [
        {
            "chapterNumber": "1",
            "contents": [
                {
                    "p": null
                },
                {
                    "verseNumber": "1",
                    "verseText": "test verse one",
                    "contents": [
                        "test verse one"
                    ]
                },
                {
                    "verseNumber": "2",
                    "verseText": "test verse two",
                    "contents": [
                        "test verse two"
                    ]
                }
            ]
        }
    ],
    "_messages": {
        "_warnings": [
            "Empty lines present. ",
            "Book code is in lowercase. "
        ]
    }
}''')},    
    ]

def assert_positive_get_for_books(item):
    '''Check for the properties in the normal return object'''
    assert "book" in item
    assert  isinstance(item['book'], dict)
    assert "bookId" in item['book']
    assert "bookCode" in item['book']
    assert "bookName" in item['book']
    assert "active" in item


def check_post(data: list):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for bibles",
    }
    add_version(version_data)
    source_data = {
        "contentType": "bible",
        "language": "guj",
        "version": "TTT",
        "year": 3030,
        "revision": 1
    }
    source = add_source(source_data)
    table_name = source.json()['data']['sourceName']
    resp = client.post(UNIT_URL+table_name+'/books', headers=headers, json=data)
    return resp, table_name

def test_post_default():
    '''Positive test to upload bible videos'''

    resp = check_post(gospel_books_data)[0]
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"
    for i,item in enumerate(resp.json()['data']):
        assert_positive_get_for_books(item)
        assert item['book']['bookCode'] == gospel_books_data[i]['JSON']['book']['bookCode'].lower()
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

    ## same book repeated in one set
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
        {'USFM': '\\id gen\\c 1\\p\\v 1 test content'}
    ]
    response = client.post(UNIT_URL+source_name+"/books", headers=headers, json=data)
    assert_input_validation_error(response)

    data = [{'JSON':gospel_books_data[0]['JSON']}]
    response = client.post(UNIT_URL+source_name+"/books", headers=headers, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields
    data = [
            {'USFM': '\\id gen\\c 1\\p\\v 1 test content',
             'JSON':{"book":"GEN"}}
    ]
    response = client.post(UNIT_URL+source_name+"/books", headers=headers, json=data)
    assert response.status_code ==415
    assert "JSON is not of the required format" in response.json()['details']

    source_name1 = source_name.replace('bible', 'video')
    data = []
    response = client.post(UNIT_URL+source_name1+'/books', headers=headers, json=data)
    assert response.status_code == 404

    source_name2 = source_name.replace('1', '7')
    response = client.post(UNIT_URL+source_name2+'/books', headers=headers, json=[])
    assert response.status_code == 404
