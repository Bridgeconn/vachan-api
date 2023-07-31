'''Test cases for parascripturals related APIs'''
from . import client , contetapi_get_accessrule_checks_app_userroles
from . import check_default_get
from . import assert_input_validation_error, assert_not_available_content
from .test_versions import check_post as add_version
from .test_resources import check_post as add_resource
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/resources/parascripturals/'
RESOURCE_URL = '/v2/resources'
RESTORE_URL = '/v2/restore'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "parascriptId" in item
    assert isinstance(item['parascriptId'], int)
    assert "category" in item
    assert "title" in item
    assert "active" in item

def check_post(data: list):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for parascriptural",
    }
    add_version(version_data)
    resource_data = {
        "contentType": "parascriptural",
        "language": "ur",
        "version": "TTT",
        "year": 2020,
        "versionTag": 1
    }
    # headers = {"contentType": "application/json", "accept": "application/json"}
    resource = add_resource(resource_data)
    resource_name = resource.json()['data']['resourceName']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    #without auth
    response = client.post(UNIT_URL+resource_name, headers=headers, json=data)
    if response.status_code == 422:
        assert response.json()['error'] == 'Input Validation Error'
    else:
        assert response.status_code == 401
        assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    return response, resource_name

def test_post_default():
    '''Positive test to upload parascriptural'''
    data = [
    	{'category':'Bible project video','title':"creation", "link":"http://somewhere.com/something"},
        {'category':'Bible project video', 'title':"abraham's family",
        "link":"http://somewhere.com/something"},
        {'category':'Bible Stories', 'title':"Isarel's travel routes",
        "link":"http://somewhere.com/something"},
        {'category':'Bible Stories', 'title':"the Gods reveals himself in new testament",
        "reference": {"book":"MAT", "chapter":2, "verseNumber":3, \
            "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"},
    ]
    response,resource_name = check_post(data)
    assert response.status_code == 201
    assert response.json()['message'] == "Parascripturals added successfully"
    for item in response.json()['data']:
        assert_positive_get(item)
    assert len(data) == len(response.json()['data'])
    return response,resource_name

def test_post_duplicate():
    '''Negative test to add two parascripturals Links with same type and title'''
    data = [
        {'category':'Bible Stories', 'title':"the Gods reveals himself in new testament",
        "link":"http://somewhere.com/new"}
    ]
    resp, resource_name = check_post(data)
    assert resp.status_code == 201
    assert resp.json()['message'] == "Parascripturals added successfully"

    data[0]['link'] = 'http://anotherplace/item'
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert response.status_code == 409
    assert response.json()['error'] == "Already Exists"

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''
    # single data object instead of list
    data = {'category':'Bible Stories', 'title':"the Geneology of Jesus Christ",
        "link":"http://somewhere.com/something"}
    resp, resource_name = check_post(data)
    assert_input_validation_error(resp)

    # data object with missing mandatory fields
    data = [
        {'category':'Bible Stories',
        "link":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'title':"the Geneology of Jesus Christ",
        "link":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields
    data = [
        {'category':'mat', 'title':"the Geneology of Jesus Christ",
        "link":"not a url"}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)


    data = [
        {'category':'Bible Stories', 'title':"the Geneology of Jesus Christ",
        "link":"noProtocol.com/something"}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    resource_name1 = resource_name.replace('parascriptural', 'para')
    data = []
    response = client.post(UNIT_URL+resource_name1, headers=headers_auth, json=data)
    assert response.status_code == 404

    resource_name2 = resource_name.replace('1', '11')
    response = client.post(UNIT_URL+resource_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

    # data object with missing mandatory fields
    data = [
        {'category':'Bible Stories',
        "link":"http://somewhere.com/something"}
    ]

    #passing book and bookEnd as integer - negative test
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    data = [
        {'category':"Bible Stories", 'title':"creation", 'description': "theme for test",
        'content':"some content for test",
        "reference": {"book":1, "chapter":2, "verseNumber":3,"bookEnd":20, 
                    "chapterEnd":5, "verseEnd":6 }
        }
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #passing book and bookEnd not in bookCodePattern expression - negative test
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    data = [
        {'category':"Bible Stories", 'title':"creation", 'description': "theme for test",
        'content':"some content for test",
        "reference": {"book":"MATHEW", "chapter":2, "verseNumber":3,
                    "bookEnd":"JOHN", "chapterEnd":5, "verseEnd":6 }
        }
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #passing non integer value for chapter and verse - negative test
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    data = [
        {'category':"Bible Stories", 'title':"creation", 'description': "theme for test",
        'content':"some content for test",
        "reference": {"book":"MAT", "chapter":"firstchapter","verseNumber":"firstverse",
                    "bookEnd":"JHN", "chapterEnd":"lastchapter", "verseEnd":"lastverse"}
        }
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_get_after_data_upload():
    '''Add some parascripturals data into the table and do all get tests'''  
    data = [
        {'category':"Bible Stories", 'title':"creation", 'description': "theme for test",
        'content':"some content for test",
        "link":"http://somewhere.com/something",
        'reference': {"book":"MAT", "chapter":2, "verseNumber":3,
                    "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        'metaData':{'otherName': 'BPV, Bible Project Video'}},
        {'category':'Bible Stories', 'title':"Noah's Ark",
        "link":"http://somewhere.com/something"},
        {'category':'Bible Stories', 'title':"abraham's family",
        "link":"http://somewhere.com/something"},
        {'category':'Bible project video', 'title':"Isarel's travel routes",
        "link":"http://somewhere.com/something"},
        {'category':'Bible project video', 'title':"Paul's travel routes",
        "link":"http://somewhere.com/something"},
        {'category':'Bible project video', 'title':"the Gods reveals himself in new testament",
        'reference': {"book":"MRK", "chapter":2, "verseNumber":10,
                    "bookEnd":"LUK", "chapterEnd":15, "verseEnd":10 },
        "link":"http://somewhere.com/something"}
    ]
    res, resource_name = check_post(data)
    assert res.status_code == 201
    check_default_get(UNIT_URL+resource_name, headers_auth,assert_positive_get)

    #filter by parascript type
    #without auth
    response = client.get(UNIT_URL+resource_name+'?category=Bible%20Stories')
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"
    #with auth
    response = client.get(UNIT_URL+resource_name+'?category=Bible%20Stories',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 3

    # filter with title
    response = client.get(UNIT_URL+resource_name+'?title=creation',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # both title and book
    response = client.get(UNIT_URL+resource_name+
        "?category=Bible%20Stories&title=Noah's%20Ark",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with description
    response = client.get(UNIT_URL+resource_name+"?description=theme for test",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with description - fuzzy match
    response = client.get(UNIT_URL+resource_name+"?description=for test",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with content - exact match
    response = client.get(UNIT_URL+resource_name+
        "?content=some content for test",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with content - fuzzy match match
    response = client.get(UNIT_URL+resource_name+"?content=content for",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with link
    response = client.get(UNIT_URL+resource_name+"?link=http://somewhere.com/something",
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 6

    # filter with metadata - exact match
    response = client.get(UNIT_URL+resource_name+
        '?metadata={"otherName": "BPV, Bible Project Video"}',
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with metadata - fuzzy match
    response = client.get(UNIT_URL+resource_name+'?metadata={"otherName": "Project Video"}' ,
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filtering with single reference
    response = client.get(UNIT_URL+resource_name+
        '?reference={"book":"MRK", "chapter":10, "verseNumber":12}',
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2
    for item in response.json():
        assert_positive_get(item)

    # filtering with cross-chapter reference
    response = client.get(UNIT_URL+resource_name+
    '?reference= {"book":"MRK", "chapter":1, \
                "verseNumber":10,"bookEnd":"LUK", "chapterEnd":10, "verseEnd":1 }',
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    for item in response.json():
        assert_positive_get(item)

    # not available resources
    response = client.get(UNIT_URL+resource_name+'?category=Animations',headers=headers_auth)
    assert_not_available_content(response)

    response = client.get(UNIT_URL+resource_name+
        '?category=Bible%20Stories&title=vision',headers=headers_auth)
    assert_not_available_content(response)

def test_searching():
    '''Being able to query parascripturals with category,title,
    content,description,reference and metadata'''
    data = [
        {
            'category':"Bible Stories",
            'title':"Creation of World",
            'description': "theme for test",
            'content':"some content for test",
            'reference': {"book":"MAT", "chapter":2, "verseNumber":3,
                "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
            'link':"http://somewhere.com/something",
            'metaData': {'otherName': 'BPV, Videos of Bible chapters'}
        }
    ]

    res, resource_name = check_post(data)
    assert res.status_code == 201
    check_default_get(UNIT_URL+resource_name, headers_auth,assert_positive_get)

    # searching with category - positive test
    response = client.get(UNIT_URL+resource_name+'?search_word=Stories',headers = headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found

    # searching with title - positive test
    response = client.get(UNIT_URL+resource_name+'?search_word=of',headers = headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found

    # searching with description:exact match - positive test
    url_with_query_string = UNIT_URL+resource_name+"?search_word=theme for test"
    response = client.get(url_with_query_string, headers=headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found

    # searching with description:fuzzy match - positive test
    query_string = "for"
    url_with_query_string = UNIT_URL+resource_name+"?search_word=" + query_string
    response = client.get(url_with_query_string, headers=headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found

    # searching with content:exact match - positive test
    url_with_query_string = UNIT_URL+resource_name+"?search_word=some content for test"
    response = client.get(url_with_query_string, headers=headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found

    # searching with content:fuzzy match - positive test
    query_string = "content for"
    url_with_query_string = UNIT_URL+resource_name+"?search_word=" + query_string
    response = client.get(url_with_query_string, headers=headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found

     # searching with link - positive test
    url_with_query_string = UNIT_URL+resource_name+"?link=http://somewhere.com/something"
    response = client.get(url_with_query_string, headers=headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found
    # searching with reference:exact match - positive test
    response = client.get(UNIT_URL+resource_name+"?search_word=JHN",headers = headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found

    # searching with reference:partial match - positive test
    response = client.get(UNIT_URL+resource_name+"?search_word=JH",headers = headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found

    # searching with not available reference keyword- negative test
    response = client.get(UNIT_URL+resource_name+"?search_word=chapter:999",
        headers = headers_auth)
    assert len(response.json()) ==  0
    assert_not_available_content(response)

    # searching with metadata with special characters:exact match - positive test
    response = client.get(UNIT_URL+resource_name+"?search_word=BPV, Videos of Bible chapters",
        headers = headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found

    # searching with partial metadata:fuzzy match - positive test
    response = client.get(UNIT_URL+resource_name+"?search_word=of chapters",headers = headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['title'] == "Creation of World":
            found = True
    assert found

    # searching with invalid search word - negative test
    response = client.get(UNIT_URL+resource_name+"?search_word=Bibles",headers = headers_auth)
    assert len(response.json()) ==  0
    found = False
    for item in response.json():
        if item['title'] == "Creation of World":
            found = True
    assert not found

def test_get_incorrect_data():
    '''Check for input validations in get'''
    resource_name = 'ur_TTT'
    response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert_input_validation_error(response)
    resp, resource_name = check_post([])
    assert resp.status_code == 201
    resource_name = resource_name.replace('parascriptural', 'graphics')
    response = client.get(UNIT_URL+resource_name, headers=headers_auth)
    assert response.status_code == 404

def test_put_after_upload():
    '''Positive tests for put'''
    data = [
        {'category':'Bible Stories', 'title':"12 apostles",
        "reference": {"book":"MAT", "chapter":2, "verseNumber":3, \
            "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"},
        {'category':'Bible Project Video', 'title':"miracles",
        "reference": {"book":"MRK", "chapter":2, "verseNumber":3, \
            "bookEnd":"LUK", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"}
    ]
    response, resource_name = check_post(data)
    assert response.status_code == 201

    # positive PUT
    new_data = [
        {'category':'Bible Stories', 'title':"12 apostles",
        "reference": {"book":"MRK", "chapter":10, "verseNumber":11, \
            "bookEnd":"LUK", "chapterEnd":12, "verseEnd":13 },
        "link":"http://anotherplace.com/something",
        "metaData":{"newkey1":"newvalue1"}},
        {'category':'Bible Project Video', 'title':"miracles",
        "reference": {"book":"MAT", "chapter":10, "verseNumber":11, \
            "bookEnd":"JHN", "chapterEnd":12, "verseEnd":13 },
        "link":"http://somewhereelse.com/something",
        "metaData":{"newkey2":"newvalue2"}}
    ]
    #without auth
    response = client.put(UNIT_URL+resource_name,headers=headers, json=new_data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    print("***********:",response.json())
    assert response.json()['message'] == 'Parascripturals updated successfully'
    for i,item in enumerate(response.json()['data']):
        assert_positive_get(item)
        print("item:",item)
        # assert response.json()['data'][i]['bible'] is None
        assert response.json()['data'][i]['category'] == new_data[i]['category']
        assert response.json()['data'][i]['title'] == new_data[i]['title']
        assert response.json()['data'][i]['reference']['book'] == new_data[i]['reference']['book']
        assert response.json()['data'][i]['reference']['chapter'] == new_data[i]['reference']['chapter']
        assert response.json()['data'][i]['reference']['verseNumber'] == new_data[i]['reference']['verseNumber']
        assert response.json()['data'][i]['reference']['bookEnd'] == new_data[i]['reference']['bookEnd']
        assert response.json()['data'][i]['reference']['chapterEnd'] == new_data[i]['reference']['chapterEnd']
        assert response.json()['data'][i]['reference']['verseEnd'] == new_data[i]['reference']['verseEnd']
        assert response.json()['data'][i]['metaData'] == new_data[i]['metaData']

    # not available PUT
    new_data[0]['category'] = 'Bible Stories New'
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=new_data)
    assert response.status_code == 404

    resource_name = resource_name.replace('1', '10')
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''

    post_data = [
        {'category':'Bible Stories', 'title':"miracles",
        "link":"http://somewhere.com/something"},
        {'category':'Bible project video', 'title':"12 apostles",
        "link":"http://somewhere.com/something"}
    ]
    resp, resource_name = check_post(post_data)
    assert resp.status_code == 201

    # single data object instead of list
    data =  {'category':'Bible Stories', 'title':"12 apostles",
        "link":"http://anotherplace.com/something"}
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # data object with missing mandatory fields
    data = [
        {'title':"12 apostles",
        "link":"http://anotherplace.com/something"}
            ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'category':'Bible Stories',
        "link":"http://somewhere.com/something"}    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields
    #updating with reference in incorrect syntax of bookCode
    data = [
        {'category':'Bible Stories', 'title':"12 apostles",
        "reference": {"book":"MATHEW", "chapter":2, "verseNumber":3,
                    "bookEnd":"JOHN", "chapterEnd":5, "verseEnd":6 }
        }
                ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #updating with link in incorrect syntax
    data = [
        {'category':'Bible Stories', 'title':"12 apostles",
        "link":"filename.txt"}    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #updating with incorrect resource name
    resource_name1 = resource_name.replace('parascriptural', 'graphics')
    response = client.put(UNIT_URL+resource_name1, headers=headers_auth, json=[])
    assert response.status_code == 404

    resource_name2 = resource_name.replace('1', '10')
    response = client.put(UNIT_URL+resource_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

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
        "versionName": "test version",
    }
    add_version(version_data)
    data = {
        "contentType": "parascriptural",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    #create resource
    response = client.post('/v2/resources', headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource created successfully"
    resource_name = response.json()['data']['resourceName']

    #create parascripturals
    data = [
        {'category':'Bible Stories', 'title':"12 apostles",
        "link":"http://somewhere.com/something"},
        {'category':'Bible project video', 'title':"miracles",
        "link":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert response.status_code == 201

    #update parascripturals with created SA user
    new_data = [
        {'category':'Bible Stories', 'title':"12 apostles",
        "link":"http://anotherplace.com/something"},
        {'category':'Bible project video', 'title':"miracles",
        "link":"http://somewhereelse.com/something"}]
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Parascripturals updated successfully'

    #update with VA not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    data = [
    	{'category':'Bible Stories', 'title':"12 apostles",
        "link":"http://somewhere.com/something"}
    ]
    contetapi_get_accessrule_checks_app_userroles("parascriptural",UNIT_URL,data)

def test_soft_delete():
    '''check soft delete in parascripturals'''
    data = [
        {'category':'Bible Stories', 'title':"the Gods reveals himself in new testament",
        "reference": {"book":"MAT", "chapter":2, "verseNumber":3,\
            "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"
        }
            ]

    delete_data = [
        {'category':'Bible Stories', 'title':'the Gods reveals himself in new testament'}
    ]

    response, resource_name = check_post(data)
    assert response.json()

    get_response1 = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert len(get_response1.json()) == len(data)
    delete_data[0]['active'] = False

    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=delete_data)
    assert response.status_code == 201
    assert response.json()
    assert response.json()["message"] == "Parascripturals updated successfully"
    # for i,item in enumerate(response.json()['data']['output']['data']): #pylint: disable=unused-variable
    #     assert not item['active']

    get_response2 = client.get(UNIT_URL+resource_name, headers=headers_auth)
    assert len(get_response2.json()) == len(data) - len(delete_data)

    get_response3 = client.get(UNIT_URL+resource_name+'?active=false',headers=headers_auth)
    assert len(get_response3.json()) == len(delete_data)

def test_delete_default():
    ''' positive test case, checking for correct return of deleted parascriptural ID'''
    #create new data
    response,resource_name = test_post_default()
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    post_response = client.get(UNIT_URL+resource_name+ \
        "?book_code=Bible%20project%20video&title=creation",\
        headers=headers_auth)
    assert post_response.status_code == 200
    assert len(post_response.json()) == 1
    for item in post_response.json():
        assert_positive_get(item)
    parascript_response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    parascript_id = parascript_response.json()[0]['parascriptId']

    #Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    response = client.delete(UNIT_URL+resource_name + \
        "?delete_id=" + str(parascript_id), headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

     #Delete parascriptural with other API user,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev']:
        headers_au = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL+resource_name + \
            "?delete_id=" + str(parascript_id), headers=headers_au)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete parascriptural with Vachan Admin
    headers_va = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['VachanAdmin']['token']
            }
    response = client.delete(UNIT_URL+resource_name + \
        "?delete_id=" + str(parascript_id), headers=headers_va)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Parascriptural id {parascript_id} deleted successfully"


def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted parascriptural ID'''
    #Created User or Super Admin can only delete parascriptural
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

    parascript_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    parascript_id = parascript_response.json()[0]['parascriptId']

     #Delete parascriptural with Super Admin
    response = client.delete(UNIT_URL+resource_name + "?delete_id=" +\
         str(parascript_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Parascriptural id {parascript_id} deleted successfully"
    #Check parascriptural is deleted from table
    parascript_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    post_response = client.get(UNIT_URL+resource_name+ \
        "?book_code=Bible%20project%20video&title=creation",\
        headers=headers_sa)
    assert_not_available_content(post_response)
    logout_user(test_user_token)
    return response,resource_name

def test_delete_parascript_id_string():
    '''positive test case, parascriptural id as string'''
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

    parascript_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    parascript_id = parascript_response.json()[0]['parascriptId']
    parascript_id = str(parascript_id)

    #Delete parascriptural with Super Admin
    response = client.delete(UNIT_URL+resource_name + \
        "?delete_id=" + str(parascript_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Parascriptural id {parascript_id} deleted successfully"
    #Check parascriptural parascriptural is deleted from table
    parascript_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    logout_user(test_user_token)


def test_delete_missingvalue_parascript_id():
    '''Negative Testcase. Passing input data without parascriptId'''
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
    response = client.delete(UNIT_URL+resource_name + "?delete_id=", headers=headers_sa)
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
    parascript_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    parascript_id = parascript_response.json()[0]['parascriptId']

    response = client.delete(UNIT_URL+ "?delete_id=" + str(parascript_id), headers=headers_sa)
    assert response.status_code == 404
    logout_user(test_user_token)

def test_delete_notavailable_content():
    ''' request a non existing parascriptural ID, Ensure there is no partial matching'''
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
    parascript_id=20000
     #Delete parascriptural with Super Admin
    response = client.delete(UNIT_URL+resource_name + \
        "?delete_id=" + str(parascript_id), headers=headers_sa)
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


    #Restore content with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev']:
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
    #Check parascriptural exists after restore
    restore_response =  client.get(UNIT_URL+resource_name+ \
        "?category=Bible project video&title=creation",\
        headers=headers_auth)
    assert restore_response.status_code == 200
    assert len(restore_response.json()) == 1
    for item in restore_response.json():
        assert_positive_get(item)
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
    data = {"itemId":9999}
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
    response = client.delete(RESOURCE_URL + "?delete_id=" + str(resource_id), headers=headers_auth)
    assert response.status_code == 200
    #Restoring data
    #Restore content with Super Admin after deleting resource
    restore_response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    restore_response.status_code = 404
    logout_user(test_user_token)