'''Test cases for bible videos related APIs'''
import re
# from urllib import response
from . import client , contetapi_get_accessrule_checks_app_userroles
from . import check_default_get
from . import assert_input_validation_error, assert_not_available_content
from .test_resources import check_post as add_resource
from .test_versions import check_post as add_version
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user
from .conftest import initial_test_users

RESOURCE_URL = '/v2/resources'
UNIT_URL = '/v2/bibles/'
RESTORE_URL = '/v2/restore'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

gospel_books_data = [
        {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id mrk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
]
gospel_books_split_data = [
        {"USFM":"\\id rev\n\\c 1\n\\p\n\\v 1a test verse one a \n\\v 1b test verse one b \n\\v 2 test verse two"}
]
gospel_books_merged_data = [
        {"USFM":"\\id rom\n\\c 1\n\\p\n\\v 1-2 test verse one and two merged \n\\v 3 test verse two"}
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

def check_post(data: list, datatype='books'):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for bibles",
    }
    add_version(version_data)
    resource_data = {
        "contentType": "bible",
        "language": "gu",
        "version": "TTT",
        "year": 3030,
        "versionTag": 1
    }
    resource = add_resource(resource_data)
    table_name = resource.json()['data']['resourceName']
    #create with vachanadmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']

    #without auth
    resp = client.post(UNIT_URL+table_name+'/books', headers=headers, json=data)
    if resp.status_code == 422:
        assert resp.json()['error'] == 'Input Validation Error'
    else:
        assert resp.status_code == 401
        assert resp.json()['error'] == 'Authentication Error'
    #with auth
    resp = client.post(UNIT_URL+table_name+'/books', headers=headers_auth, json=data)
    return resp, table_name

def test_post_default():
    '''Positive test to upload bible videos'''

    resp,resource_name = check_post(gospel_books_data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"
    for i,item in enumerate(resp.json()['data']):
        assert_positive_get_for_books(item)
        book_code = re.match(r'\\id (\w\w\w)', gospel_books_data[i]['USFM']).group(1)
        assert item['book']['bookCode'] == book_code.lower()
    assert len(gospel_books_data) == len(resp.json()['data'])
    return resp,resource_name

def test_post_optional():
    '''Positive test fr post with optional JSON upload'''
    # only json
    post_data = [{"JSON":
        {"book": {"bookCode": "ACT"},
     "chapters": [
            {
                "chapterNumber": "1",
                "contents": [
                    {   "verseNumber": "1",
                        "verseText": "First verse of acts"},
                    {   "verseNumber": "2",
                        "verseText": "Second verse of acts"},
                    {   "verseNumber": "3",
                        "verseText": "Thrid verse of acts"}
                ]
            }
        ]
    }
    }]

    # both json and usfm
    post_data.append({ "USFM":"\\id rev\n\\c 1\n\\p\n\\v 1 one verse of revelations",
                    "JSON":{'book':{'bookCode':"REV"},"chapters":[
                    {"chapterNumber":1, "contents":[
                        {"verseNumber":"1", "verseText":"one verse of revelations"}
                    ]}
                ]}})

    resp = check_post(post_data)[0]
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"
    assert len(resp.json()['data']) == 2

def test_post_put_split_verse():
    """test posting split verse"""
    resp, resource_name = check_post(gospel_books_split_data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"
    for i,item in enumerate(resp.json()['data']):
        assert_positive_get_for_books(item)
        book_code = re.match(r'\\id (\w\w\w)', gospel_books_split_data[i]['USFM']).group(1)
        assert item['book']['bookCode'] == book_code.lower()
    assert len(gospel_books_split_data) == len(resp.json()['data'])

    #get bible data and check split verses are combined
    response = client.get(UNIT_URL+resource_name+'/verses?book_code=rev&chapter=1',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    for row in response.json():
        if row["reference"]["verseNumber"] == 1:
            assert row["verseText"] == "test verse one a test verse one b"
            #check metadata
            assert "publishedVersification" in row["metaData"]
            assert len(row["metaData"]["publishedVersification"]) == 2
            for dict in row["metaData"]["publishedVersification"]:
                dict["verseNumber"] in ('1a','1b')
                if dict["verseNumber"] == '1a':
                    dict["verseText"] == 'test verse one a'
                elif dict["verseNumber"] == '1b':
                    dict["verseText"] == 'test verse one b'

        if row["reference"]["verseNumber"] == 2:
            assert row["verseText"] == 'test verse two'

    
    #update with split verse
    update_data_split = [{
        "USFM": "\\id rev\n\\c 1\n\\p\n\\v 1a new content for rev \n\\v 1b test verse one updated b"}]
    response2 = client.put(UNIT_URL+resource_name+"/books", json=update_data_split, headers=headers_auth)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Bible books updated successfully"

    #get updated data combine verse re upload usfm
    response = client.get(UNIT_URL+resource_name+'/verses?book_code=rev&chapter=1',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    for row in response.json():
        if row["reference"]["verseNumber"] == 1:
            assert row["verseText"] == "new content for rev test verse one updated b"
            #check metadata
            assert "publishedVersification" in row["metaData"]
            assert len(row["metaData"]["publishedVersification"]) == 2
            for dict in row["metaData"]["publishedVersification"]:
                assert dict["verseNumber"] in ('1a','1b')
                if dict["verseNumber"] == '1a':
                    assert dict["verseText"] == 'new content for rev'
                elif dict["verseNumber"] == '1b':
                    assert dict["verseText"] == 'test verse one updated b'

    #check for sorted verses in exact order
    split_data_sort = [
        {"USFM":"\\id exo\n\\c 1\n\\p\n\\v 6ഉ test verse six g \n\\v 6എ test verse six c \n\\v 6അ test verse six b"},
        {"USFM":"\\id gen\n\\c 1\n\\p\n\\v 7l test verse seven l \n\\v 7d test verse seven d \n\\v 7x test verse seven x"},
        {"USFM":"\\id lev\n\\c 1\n\\p\n\\v 4k test verse four k \n\\v 4b test verse four b \n\\v 4j test verse four j"}
    ]
    expected_versetext_eng = "test verse four b test verse four j test verse four k"
    expected_versetext_mal = "test verse six b test verse six g test verse six c"
    expected_versetext_7 = "test verse seven d test verse seven l test verse seven x"

    #add
    resp = client.post(UNIT_URL+resource_name+'/books', headers=headers_auth, json=split_data_sort)
    response1 = client.get(UNIT_URL+resource_name+'/verses?book_code=lev&chapter=1',headers=headers_auth)
    response2 = client.get(UNIT_URL+resource_name+'/verses?book_code=exo&chapter=1',headers=headers_auth)
    response3 = client.get(UNIT_URL+resource_name+'/verses?book_code=gen&chapter=1',headers=headers_auth)
    assert response.status_code == 200
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"
    for row in response1.json():
        if row["reference"]["verseNumber"] == 4:
            assert row["verseText"] == expected_versetext_eng
    for row in response2.json():
        if row["reference"]["verseNumber"] == 6:
            assert row["verseText"] == expected_versetext_mal
    for row in response3.json():
        if row["reference"]["verseNumber"] == 7:
            assert row["verseText"] == expected_versetext_7
    #update sort
    split_data_sort = [
        {"USFM":"\\id exo\n\\c 1\n\\p\n\\v 6ഉ test verse six g \n\\v 6എ test verse six c edited \n\\v 6അ test verse six b"},
        {"USFM":"\\id lev\n\\c 1\n\\p\n\\v 4k test verse four k edited \n\\v 4b test verse four b \n\\v 4j test verse four j"}
    ]
    edited_versetext_eng = "test verse four b test verse four j test verse four k edited"
    edited_versetext_mal = "test verse six b test verse six g test verse six c edited"
    response_up1 = client.put(UNIT_URL+resource_name+"/books", json=split_data_sort, headers=headers_auth)
    assert response_up1.status_code == 201
    assert response_up1.json()['message'] == "Bible books updated successfully"

    response1 = client.get(UNIT_URL+resource_name+'/verses?book_code=exo&chapter=1',headers=headers_auth)
    response2 = client.get(UNIT_URL+resource_name+'/verses?book_code=lev&chapter=1',headers=headers_auth)
    for row in response1.json():
        if row["reference"]["verseNumber"] == 6:
            assert row["verseText"] == edited_versetext_mal
    for row in response2.json():
        if row["reference"]["verseNumber"] == 4:
            assert row["verseText"] == edited_versetext_eng

def test_post_put_merged_verse():
    """test posting merged verse"""
    resp, resource_name = check_post(gospel_books_merged_data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"
    for i,item in enumerate(resp.json()['data']):
        assert_positive_get_for_books(item)
        book_code = re.match(r'\\id (\w\w\w)', gospel_books_merged_data[i]['USFM']).group(1)
        assert item['book']['bookCode'] == book_code.lower()
    assert len(gospel_books_merged_data) == len(resp.json()['data'])

    # # #get bible data and check split verses are combined
    response = client.get(UNIT_URL+resource_name+'/verses?book_code=rom&chapter=1',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3
    for row in response.json():
        if row["reference"]["verseNumber"] == 1:
            assert row["verseText"] == "test verse one and two merged"
            assert "publishedVersification" in row["metaData"]
            assert len(row["metaData"]["publishedVersification"]) == 1
            for dict in row["metaData"]["publishedVersification"]:
                assert dict["verseNumber"] == '1-2'
                assert dict["verseText"] == 'test verse one and two merged'
        if row["reference"]["verseNumber"] == 2:
            assert row["verseText"] == ''
            assert "publishedVersification" in row["metaData"]
            assert len(row["metaData"]["publishedVersification"]) == 1
            for dict in row["metaData"]["publishedVersification"]:
                assert dict["verseNumber"] == '1-2'
                assert dict["verseText"] == 'test verse one and two merged'
        if row["reference"]["verseNumber"] == 3:
            assert row["verseText"] == "test verse two"
            assert row["metaData"] is None
    
    #update with merge verse
    update_data_merge = [{
        "USFM": "\\id rom\n\\c 1\n\\p\n\\v 1-2 new content for rom merged updated"}]
    response2 = client.put(UNIT_URL+resource_name+"/books", json=update_data_merge, headers=headers_auth)
    assert response2.status_code == 201
    assert response2.json()['message'] == "Bible books updated successfully"

    #get updated data combine verse re upload usfm
    response = client.get(UNIT_URL+resource_name+'/verses?book_code=rom&chapter=1',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    for row in response.json():
        if row["reference"]["verseNumber"] == 1:
            assert row["verseText"] == "new content for rom merged updated"
            assert "publishedVersification" in row["metaData"]
            assert len(row["metaData"]["publishedVersification"]) == 1
            for dict in row["metaData"]["publishedVersification"]:
                assert dict["verseNumber"] == '1-2'
                assert dict["verseText"] == 'new content for rom merged updated'
        if row["reference"]["verseNumber"] == 2:
            assert row["verseText"] == ''
            assert "publishedVersification" in row["metaData"]
            assert len(row["metaData"]["publishedVersification"]) == 1
            for dict in row["metaData"]["publishedVersification"]:
                assert dict["verseNumber"] == '1-2'
                assert dict["verseText"] == 'new content for rom merged updated'

def test_post_duplicate():
    '''test posting the same book twice'''
    data = gospel_books_data[:1]
    resp, table = check_post(data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"

    data2 = gospel_books_data[:1]
    resp2 = client.post(UNIT_URL+table+'/books', headers=headers_auth, json=data2)
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
    resp, resource_name = check_post(one_row)
    assert_input_validation_error(resp)

    # data object with missing both optional fields
    data = [{}]

    # incorrect data values in fields
    data = [
            {'USFM': '<id gen><c 1><p><v 1 test content>'}
    ]
    response = client.post(UNIT_URL+resource_name+"/books", headers=headers, json=data)
    assert response.status_code ==415
    assert "USFM is not of the required format" in response.json()['details']

    resource_name1 = resource_name.replace('bible', 'video')
    data = []
    response = client.post(UNIT_URL+resource_name1+'/books', headers=headers, json=data)
    assert response.status_code == 404

    resource_name2 = resource_name.replace('1', '7')
    response = client.post(UNIT_URL+resource_name2+'/books', headers=headers, json=[])
    assert response.status_code == 404

def test_put_books():
    '''adds some books and change them using put APIs'''
    resp, src = check_post(gospel_books_data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"

    #update without specifying the book code
    update_data = [{
        "USFM": "\\id mat\n\\c 1\n\\p\n\\v 1 new content for matthew"}]
    #without auth    
    response1 = client.put(UNIT_URL+src+"/books", json=update_data, headers=headers)
    assert response1.status_code == 401
    assert response1.json()['error'] == 'Authentication Error'

    #with auth
    response1 = client.put(UNIT_URL+src+"/books", json=update_data, headers=headers_auth)
    assert response1.status_code == 201
    assert response1.json()['message'] == "Bible books updated successfully"
    assert len(response1.json()['data']) == 1
    assert_positive_get_for_books(response1.json()['data'][0])
    resp_usfm = response1.json()['data'][0]["USFM"].lower().strip().replace("\n", "")
    assert  resp_usfm == update_data[0]["USFM"].replace("\n", "")
    assert response1.json()['data'][0]["book"]["bookCode"] == "mat"

    #only with JSON
    update_data[0]["USFM"] = None
    response2 = client.put(UNIT_URL+src+"/books", json=update_data, headers=headers_auth)
    assert_input_validation_error(response2)


    #to change status
    update_data = [
        {"active": False, "bookCode":"jhn"}
    ]
    response4 = client.put(UNIT_URL+src+"/books", json=update_data, headers=headers_auth)
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
    response5 = client.put(UNIT_URL+src+"/books", json=update_data, headers=headers_auth)
    assert response5.status_code == 404
    assert response5.json()['error'] == "Requested Content Not Available"

def test_upload_book_after_resource_update():
    '''Bugfix test for #529 '''
    resp = check_post([gospel_books_data[0]])[0]
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"

    # Case 1 : Update language field in resource
    resource_data_update = {
        "resourceName": 'gu_TTT_1_bible',
        "language": 'ml' 
    }
    response = client.put(RESOURCE_URL, headers=headers_auth, json=resource_data_update)
    table_name = response.json()['data']['resourceName']

    # Post same bible book after updating resource - negative test
    response = client.post(UNIT_URL+table_name+'/books', headers=headers_auth, json=[gospel_books_data[0]])
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

    # Post different bible book after updating resource - positive test
    new_book_data = [
            {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
        ]
    response = client.post(UNIT_URL+table_name+'/books', headers=headers_auth, json=new_book_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Bible books uploaded and processed successfully"

    # Case 2 : Update version field in resource
    version_data = {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
    }
    add_version(version_data)
    resource_update_data = {
        "resourceName": 'ml_TTT_1_bible',
        "version": 'XYZ' 
    }
    response = client.put(RESOURCE_URL, headers=headers_auth, json=resource_update_data)
    table_name = response.json()['data']['resourceName']

    # Post same bible book after updating resource
    response = client.post(UNIT_URL+table_name+'/books', headers=headers_auth, json=new_book_data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

    # Post different bible book after updating resource
    new_book_data = [
            {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
        ]
    response = client.post(UNIT_URL+table_name+'/books', headers=headers_auth, json=new_book_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Bible books uploaded and processed successfully"

def test_get_books_contenttype():
    '''Add some books data into the table and do content type related get tests'''
    res, resource_name = check_post(gospel_books_data)
    assert res.status_code == 201
    # headers = {"contentType": "application/json", "accept": "application/json"}
    check_default_get(UNIT_URL+resource_name+"/books", headers_auth,assert_positive_get_for_books)

    # content_type
    #without auth   
    response = client.get(UNIT_URL+resource_name+'/books',headers=headers)
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"

    #with auth
    response = client.get(UNIT_URL+resource_name+'/books',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == len(gospel_books_data)
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" not in res
        assert "JSON" not in res

    #without auth
    response = client.get(UNIT_URL+resource_name+'/books?content_type=usfm')
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"

    #with auth
    response = client.get(UNIT_URL+resource_name+'/books?content_type=usfm',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == len(gospel_books_data)
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" in res
        assert "JSON" not in res

    response = client.get(UNIT_URL+resource_name+'/books?content_type=json',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == len(gospel_books_data)
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" not in res
        assert "JSON" in res

    response = client.get(UNIT_URL+resource_name+'/books?content_type=all',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == len(gospel_books_data)
    for res in response.json():
        assert_positive_get_for_books(res)
        assert "USFM" in res
        assert "JSON" in res

    # not available
    response = client.get(UNIT_URL+resource_name+'/books?book_code=jud',headers=headers_auth)
    assert_not_available_content(response)


def test_get_books_filter():
    '''add some usfm data and test get api based on book_code and active filters '''
    res, resource_name = check_post(gospel_books_data)
    assert res.status_code == 201

    # book_code without audio data
    response = client.get(UNIT_URL+resource_name+'/books?book_code=mat',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['book']['bookCode'] == 'mat'

    added_books = ['mat', 'mrk', 'luk', 'jhn', '1jn', '2jn', '3jn', 'rev']

    resp = client.get(UNIT_URL+resource_name+'/books',headers=headers_auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 4
    assert resp.json()[0]['book']['bookCode'] in added_books

    # active filter
    res1 = client.get(UNIT_URL+resource_name+'/books',headers=headers_auth)
    res2 = client.get(UNIT_URL+resource_name+'/books?active=True',headers=headers_auth)
    assert res1.status_code == res2.status_code
    assert res1.json() == res2.json()

    res3 = client.get(UNIT_URL+resource_name+'/books?active=False',headers=headers_auth)
    assert_not_available_content(res3)

def test_get_books_versification():
    '''add some usfm data and test get api based on book_code and active filters '''
    res, resource_name = check_post(gospel_books_data)
    assert res.status_code == 201

    # #without auth
    response = client.get(UNIT_URL+resource_name+'/versification')
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"
    #with auth
    response = client.get(UNIT_URL+resource_name+'/versification',headers=headers_auth)
    assert response.status_code == 200
    assert "maxVerses" in response.json()
    assert len(response.json()['maxVerses']) == 4
    assert response.json()['maxVerses']['mat'][0] == 2
    assert response.json()['maxVerses']['mrk'][0] == 2
    assert response.json()['maxVerses']['luk'][0] == 2
    assert response.json()['maxVerses']['jhn'][0] == 2

def test_get_verses():
    '''Upload some bibles and fetch verses'''
    res, resource_name = check_post(gospel_books_data)
    assert res.status_code == 201

    #without auth
    response = client.get(UNIT_URL+resource_name+'/verses')
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"
    #with auth
    response = client.get(UNIT_URL+resource_name+'/verses',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 8
    for item in response.json():
        assert_positive_get_for_verse(item)

    response = client.get(UNIT_URL+resource_name+'/verses?book_code=mat',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+resource_name+'/verses?book_code=mrk&chapter=1',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+resource_name+'/verses?book_code=mat&chapter=1&verse=1',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(UNIT_URL+resource_name+ \
        '/verses?book_code=mat&chapter=1&verse=1&last_verse=10',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get(UNIT_URL+resource_name+'/verses?book_code=mat&chapter=1&verse=10',headers=headers_auth)
    assert_not_available_content(response)

    response = client.get(UNIT_URL+resource_name+\
        '/verses?book_code=mat&chapter=1&verse=10&last_verse=20',headers=headers_auth)
    assert_not_available_content(response)

    response = client.get(UNIT_URL+resource_name+'/verses?book_code=act&chapter=1&verse=10',headers=headers_auth)
    assert_not_available_content(response)

def test_book_delete():
    '''add data, update active field with put and try get apis with active filters'''

    resp, resource = check_post(gospel_books_data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"

    res1 = client.get(UNIT_URL+resource+'/books',headers=headers_auth)
    res2 = client.get(UNIT_URL+resource+'/verses',headers=headers_auth)
    assert res1.status_code == 200
    assert len(res1.json()) == 4
    assert res2.status_code == 200
    assert len(res2.json()) == 8

    update_data = [
        {"bookCode": "mat", "active":False}
    ]
    resp = client.put(UNIT_URL+resource+'/books', json=update_data, headers=headers_auth)
    assert resp.status_code == 201

    res1 = client.get(UNIT_URL+resource+'/books',headers=headers_auth)
    res2 = client.get(UNIT_URL+resource+'/verses',headers=headers_auth)
    assert res1.status_code == 200
    assert len(res1.json()) == 3
    assert res2.status_code == 200
    assert len(res2.json()) == 6

    res1 = client.get(UNIT_URL+resource+'/books?active=false',headers=headers_auth)
    res2 = client.get(UNIT_URL+resource+'/verses?active=false',headers=headers_auth)
    assert res1.status_code == 200
    assert len(res1.json()) == 1
    assert res2.status_code == 200
    assert len(res2.json()) == 2

    res1 = client.get(UNIT_URL+resource+'/books?book_code=mat',headers=headers_auth)
    res2 = client.get(UNIT_URL+resource+'/verses?book_code=mat',headers=headers_auth)
    assert_not_available_content(res1)
    assert_not_available_content(res2)
    res3 = client.get(UNIT_URL+resource+'/books?content_type=all',headers=headers_auth)
    assert res3.status_code == 200
    assert len(res3.json()) == 3

def test_created_user_can_only_edit():
    """only created user and SA can only edit"""
    SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    #creating one data with Super Admin and try to edit with VachanAdmin
    response = login(SA_user_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth['Authorization'] = "Bearer"+" "+test_user_token

    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for bibles",
    }
    add_version(version_data)
    resource_data = {
        "contentType": "bible",
        "language": "gu",
        "version": "TTT",
        "year": 3030,
        "versionTag": 1
    }
    #create resource
    response = client.post('/v2/resources', headers=headers_auth, json=resource_data)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource created successfully"
    resource_name = response.json()['data']['resourceName']

    #create bible
    resp = client.post(UNIT_URL+resource_name+'/books', headers=headers_auth, json=gospel_books_data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"

    #update bible with created SA user
    update_data = [{
        "USFM": "\\id mat\n\\c 1\n\\p\n\\v 1 new content for matthew"}]
    response1 = client.put(UNIT_URL+resource_name+"/books", json=update_data, headers=headers_auth)
    assert response1.status_code == 201
    assert response1.json()['message'] == "Bible books updated successfully"

    #update with VA not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response1 = client.put(UNIT_URL+resource_name+"/books", json=update_data, headers=headers_auth)
    assert response1.status_code == 403
    assert response1.json()['error'] == 'Permission Denied'

def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    data = [
    	    {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
    ]
    contetapi_get_accessrule_checks_app_userroles("bible",UNIT_URL,data, bible=True)

def test_delete_default():
    ''' positive test case, checking for correct return of deleted biblebook ID'''
    #create new data
    response,resource_name = test_post_default()
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    #Check bible book exist in dynamic table ater post
    post_response = client.get(UNIT_URL+resource_name+'/books?book_code=mat',\
        headers=headers_auth)
    assert post_response.status_code == 200
    assert len(post_response.json()) == 1
    for item in post_response.json():
        assert_positive_get_for_books(item)
    #check item exists in cleaned table after post
    post_response2 = client.get(UNIT_URL+resource_name+'/verses?book_code=mat&chapter=1&verse=1',headers=headers_auth)
    assert post_response2.status_code == 200
    assert len(post_response2.json()) == 1
    #Get bible bookId
    biblebook_response = client.get(UNIT_URL+resource_name+'/books',headers=headers_auth)
    biblebook_id = biblebook_response.json()[0]['bookContentId']

    #Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    response = client.delete(UNIT_URL+resource_name+'/books' + "?delete_id=" + str(biblebook_id), headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

     #Delete Bible Book with other API user,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev']:
        headers_au = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL+resource_name+'/books' + "?delete_id=" + str(biblebook_id), headers=headers_au)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete biblebook with Vachan Admin
    headers_va = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['VachanAdmin']['token']
            }
    response = client.delete(UNIT_URL+resource_name+'/books' + "?delete_id=" + str(biblebook_id), headers=headers_va)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Bible Book with id {biblebook_id} deleted successfully"
    biblebook_response = client.get(UNIT_URL+resource_name+'/books',headers=headers_auth)
    assert biblebook_response.status_code == 200
    #Check biblebook is deleted from table
    delete_response = client.get(UNIT_URL+resource_name+'/books?book_code=mat',\
        headers=headers_auth)
    assert_not_available_content(delete_response)
    #Check item exists in cleaned table
    delete_response2 = client.get(UNIT_URL+resource_name+'/verses?book_code=mat&chapter=1&verse=1',headers=headers_auth)
    assert_not_available_content(delete_response2)
    

def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted biblebook ID'''
    #Created User or Super Admin can only delete biblebook
    #creating data
    response,resource_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    biblebook_response = client.get(UNIT_URL+resource_name+'/books',headers=headers_sa)
    biblebook_id = biblebook_response.json()[0]['bookContentId']

   

     #Delete biblebook with Super Admin
    response = client.delete(UNIT_URL+resource_name+'/books' + "?delete_id=" + str(biblebook_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Bible Book with id {biblebook_id} deleted successfully"
    #Check biblebook is deleted from table
    biblebook_response = client.get(UNIT_URL+resource_name+'/books',headers=headers_sa)
    logout_user(test_user_token)
    return response,resource_name

def test_delete_biblebook_id_string():
    '''positive test case, biblebook id as string'''
    response,resource_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    biblebook_response = client.get(UNIT_URL+resource_name+'/books',headers=headers_sa)
    biblebook_id = biblebook_response.json()[0]['bookContentId']
    biblebook_id = str(biblebook_id)

    #Delete biblebook with Super Admin
    response = client.delete(UNIT_URL+resource_name+'/books' + "?delete_id=" + str(biblebook_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Bible Book with id {biblebook_id} deleted successfully"
    #Check biblebook biblebook is deleted from table
    biblebook_response = client.get(UNIT_URL+resource_name+'/books',headers=headers_sa)
    logout_user(test_user_token)

def test_delete_incorrectdatatype():
    '''negative testcase. Passing input data not in json format'''
    response,resource_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    biblebook_response = client.get(UNIT_URL+resource_name+'/books',headers=headers_sa)
    biblebook_id = biblebook_response.json()[0]['bookContentId']
    biblebook_id={ }

    #Delete biblebook with Super Admin
    response = client.delete(UNIT_URL+resource_name+'/books' + "?delete_id=" + str(biblebook_id), headers=headers_sa)
    assert_input_validation_error(response)
    logout_user(test_user_token)

def test_delete_missingvalue_biblebook_id():
    '''Negative Testcase. Passing input data without bookContentId'''
    response,resource_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    biblebook_id = " "
    response = client.delete(UNIT_URL+resource_name+'/books' + "?delete_id=" + str(biblebook_id), headers=headers_sa)
    assert_input_validation_error(response)
    logout_user(test_user_token)

def test_delete_missingvalue_resource_name():
    '''Negative Testcase. Passing input data without resourceName'''
    response,resource_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    biblebook_response = client.get(UNIT_URL+resource_name+'/books',headers=headers_sa)
    biblebook_id = biblebook_response.json()[0]['bookContentId']
    
    response = client.delete(UNIT_URL+'/books' + "?delete_id=" + str(biblebook_id), headers=headers_sa)
    assert response.status_code == 404
    logout_user(test_user_token)

def test_delete_notavailable_content():
    ''' request a non existing biblebook ID, Ensure there is no partial matching'''
    response,resource_name = test_post_default()

    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_sa= {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }

    biblebook_id=9999
    #Delete biblebook with Super Admin
    response=client.delete(UNIT_URL+resource_name+'/books' + "?delete_id=" + str(biblebook_id), headers=headers_sa)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    logout_user(test_user_token)

def test_restore_default():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response,resource_name = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}
    #Restoring data
    #Restore without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'


    #Restore content with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev,'VachanContentAdmin','VachanContentViewer' and APIUSer2
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev','APIUser2','VachanContentAdmin','VachanContentViewer']:
        headers = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.put(RESTORE_URL, headers=headers, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Restore content with Super Admin
    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleteditem_id} restored successfully"
    #Check bible book exists in dynamic table after restore
    restore_response =  client.get(UNIT_URL+resource_name+'/books?book_code=mat',\
        headers=headers_auth)
    assert restore_response.status_code == 200
    assert len(restore_response.json()) == 1
    for item in restore_response.json():
        assert_positive_get_for_books(item)
    #check item exists in cleaned table
    restore_response2 =client.get(UNIT_URL+resource_name+'/verses?book_code=mat&chapter=1&verse=1',\
        headers=headers_auth)
    assert restore_response2.status_code == 200
    assert len(restore_response2.json()) == 1
    logout_user(test_user_token)

def test_restore_item_id_string():
    '''positive test case, passing deleted item id as string'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response = test_delete_default_superadmin()[0]
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring string data
    deleteditem_id = str(deleteditem_id)
    data = {"itemId": deleteditem_id}

#Login as Super Admin
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                     }

    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleteditem_id} restored successfully"
    logout_user(token_admin)

def test_restore_incorrectdatatype():
    '''Negative Test Case. Passing input data not in json format'''
    #Creating and Deleting data
    response = test_delete_default_superadmin()[0]
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Login as Super Admin
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                     }

    #Passing input data not in json format
    data = deleteditem_id
    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)
    logout_user(token_admin)

def test_restore_missingvalue_itemid():
    '''itemId is mandatory in input data object'''
    data = {}
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']
    headers_admin = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                    }
    response = client.put(RESTORE_URL, headers=headers_admin, json=data)
    assert_input_validation_error(response)
    logout_user(token_admin)

def test_restore_notavailable_item():
    ''' request a non existing restore ID, Ensure there is no partial matching'''
    data = {"itemId":20000}
    data_admin   = {
    "user_email": SUPER_USER,
    "password": SUPER_PASSWORD
    }
    response =login(data_admin)
    assert response.json()['message'] == "Login Succesfull"
    token_admin =  response.json()['token']
    headers_admin = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token_admin
                    }

    response = client.put(RESTORE_URL, headers=headers_admin, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"

def test_restoreitem_with_notavailable_resource():
    ''' Negative test case.request to restore an item whoose resource is not available'''
    #only Super Admin can restore deleted data
    #Creating and Deleting data
    response,resource_name = test_delete_default_superadmin()
    deleteditem_id = response.json()['data']['itemId']
    data = {"itemId": deleteditem_id}
    #Login as Super Admin
    as_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(as_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+test_user_token
            }
    #Delete Associated Resource
    get_resource_response = client.get(RESOURCE_URL + "?resource_name="+resource_name, headers=headers_auth)
    resource_id = get_resource_response.json()[0]["resourceId"]
    response = client.delete(RESOURCE_URL +  "?delete_id=" + str(resource_id), headers=headers_auth)
    assert response.status_code == 200
    #Restoring data
    #Restore content with Super Admin after deleting resource
    restore_response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    restore_response.status_code = 404
    logout_user(test_user_token)

def test_bible_upload_with_split_verses():
    '''Text the fix on this issue https://github.com/Bridgeconn/vachan-api/issues/538'''
    buggy_books_data = [{"USFM": "\\id JOB\n\\c 24\n\\p\n"+\
        "\n\\v 1 normal \n\\v 2 again normal \n\\v 3a split, first part "+\
        "\n\\v 3b split, second half \n\\v 4 normal and final"}]
    resp,_ = check_post(buggy_books_data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"
