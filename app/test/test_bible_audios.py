'''Test cases for bible audios related APIs'''
from . import client , resourcetypeapi_get_accessrule_checks_app_userroles
from . import check_default_get
from . import assert_input_validation_error, assert_not_available_content
from .test_versions import check_post as add_version
from .test_resources import check_post as add_resource
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user
from .conftest import initial_test_users

UNIT_URL = '/v2/resources/bible/audios/'
RESOURCE_URL = '/v2/resources'
RESTORE_URL = '/v2/restore'
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"}

def assert_positive_get(item):
    '''Check for the properties in the normal return object'''
    assert "audioId" in item
    assert isinstance(item['audioId'], int)
    assert "active" in item

def check_post(data: list):
    '''prior steps and post attempt, without checking the response'''
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for audiobible",
    }
    add_version(version_data)
    resource_data = {
        "resourceType": "audiobible",
        "language": "ins",
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
    '''Positive test to upload audiobible'''
    data = [
    	{'name':"creation", "audioFormat":"mp3","link":"http://somewhere.com/something"},
        {'name':"abraham's family","audioFormat":"mar",
        "link":"http://somewhere.com/something"},
        {'name':"Isarel's travel routes","audioFormat":"ape",
        "link":"http://somewhere.com/something"},
        {'name':"the Gods reveals himself in new testament",
        "audioFormat":"mp3",
        "reference": {"book":"MAT", "chapter":2, "verseNumber":3, \
            "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"},
    ]
    response,resource_name = check_post(data)
    assert response.status_code == 201
    assert response.json()['message'] == "Audio Bibles added successfully"
    for item in response.json()['data']:
        assert_positive_get(item)
    assert len(data) == len(response.json()['data'])
    return response,resource_name

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''
    # single data object instead of list
    data = {'name':"the Geneology of Jesus Christ",
        "audioFormat":"mp3",
        "link":"http://somewhere.com/something"}
    resp, resource_name = check_post(data)
    assert_input_validation_error(resp)

    # incorrect data values in fields
    data = [
        {'name':"the Geneology of Jesus Christ",
        "audioFormat":"mp3",
        "link":"not a url"}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {'name':"the Geneology of Jesus Christ",
        "link":"noProtocol.com/something"}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    resource_name1 = resource_name.replace('audiobible', 'audio')
    data = []
    response = client.post(UNIT_URL+resource_name1, headers=headers_auth, json=data)
    assert response.status_code == 404

    resource_name2 = resource_name.replace('1', '11')
    response = client.post(UNIT_URL+resource_name2, headers=headers_auth, json=[])
    assert response.status_code == 404

    #passing book and bookEnd as integer - negative test
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    data = [
        {'name':"creation", "audioFormat":"mp3",
        "reference": {"book":1, "chapter":2, "verseNumber":3,"bookEnd":20,
                    "chapterEnd":5, "verseEnd":6 }
        }
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #passing book and bookEnd not in bookCodePattern expression - negative test
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    data = [
        {'name':"creation", "audioFormat":"mp3",
        "reference": {"book":"MATHEW", "chapter":2, "verseNumber":3,
                    "bookEnd":"JOHN", "chapterEnd":5, "verseEnd":6 }
        }
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #passing non integer value for chapter and verse - negative test
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    data = [
        {'name':"creation", "audioFormat":"mp3",
        "reference": {"book":"MAT", "chapter":"firstchapter","verseNumber":"firstverse",
                    "bookEnd":"JHN", "chapterEnd":"lastchapter", "verseEnd":"lastverse"}
        }
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #passing integer value to audio format - negative test
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    data = [
        {'name':"creation", "audioFormat":"mp3",
        "reference": {"book":"MAT", "chapter":"firstchapter","verseNumber":"firstverse",
                    "bookEnd":"JHN", "chapterEnd":"lastchapter", "verseEnd":"lastverse"}
        }
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

def test_get_after_data_upload():
    '''Add some audiobibles data into the table and do all get tests'''  
    data = [
        {'name':"creation", "audioFormat":"mp3",
        "link":"http://somewhere.com/something",
        'reference': {"book":"MAT", "chapter":2, "verseNumber":3,
                    "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        'metaData':{'otherName': 'ABP, Audio Bible Project'}},
        {'name':"Noah's Ark",
        "link":"http://somewhere.com/something"},
        {'name':"abraham's family",
        "link":"http://somewhere.com/something"},
        {'name':"Isarel's travel routes",
        "link":"http://somewhere.com/something"},
        {'name':"Paul's travel routes",
        "link":"http://somewhere.com/something"},
        {'name':"the Gods reveals himself in new testament",
        "audioFormat":"mp3",
        'reference': {"book":"MRK", "chapter":2, "verseNumber":10,
                    "bookEnd":"LUK", "chapterEnd":15, "verseEnd":10 },
        "link":"http://somewhere.com/something"}
    ]
    res, resource_name = check_post(data)
    assert res.status_code == 201
    check_default_get(UNIT_URL+resource_name, headers_auth,assert_positive_get)

    # filter with name
    #without auth
    response = client.get(UNIT_URL+resource_name+'?name=creation')
    assert response.status_code == 401
    assert response.json()["error"] == "Authentication Error"

    #with auth
    response = client.get(UNIT_URL+resource_name+'?name=creation',headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with audio format
    response = client.get(UNIT_URL+resource_name+"?audio_format=mp3",headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # filter with link
    response = client.get(UNIT_URL+resource_name+"?link=http://somewhere.com/something",
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 6

    # filter with metadata - exact match
    response = client.get(UNIT_URL+resource_name+
        '?metadata={"otherName": "ABP, Audio Bible Project"}',
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # filter with metadata - fuzzy match
    response = client.get(UNIT_URL+resource_name+'?metadata={"otherName": "Bible Project"}' ,
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
                "verseNumber":10,"bookEnd":"MRK", "chapterEnd":10, "verseEnd":15 }',
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    for item in response.json():
        assert_positive_get(item)

    # filtering with cross-book reference
    response = client.get(UNIT_URL+resource_name+
    '?reference= {"book":"MRK", "chapter":1, \
                "verseNumber":10,"bookEnd":"LUK", "chapterEnd":10, "verseEnd":1 }',
        headers=headers_auth)
    assert response.status_code == 200
    assert len(response.json()) == 1
    for item in response.json():
        assert_positive_get(item)

    # not available resources
    response = client.get(UNIT_URL+resource_name+'?name=Music',headers=headers_auth)
    assert_not_available_content(response)

    response = client.get(UNIT_URL+resource_name+
        '?name=vision',headers=headers_auth)
    assert_not_available_content(response)

def test_searching():
    '''Being able to query audiobibles with name,audio format,reference and metadata'''
    data = [
        {
            'name':"Creation of World",
            "audioFormat":"mp3",
            'reference': {"book":"MAT", "chapter":2, "verseNumber":3,
                "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
            'link':"http://somewhere.com/something",
            'metaData': {'otherName': 'ABP, Audio Bible Project'}
        }
    ]

    res, resource_name = check_post(data)
    assert res.status_code == 201
    check_default_get(UNIT_URL+resource_name, headers_auth,assert_positive_get)

    # searching with name - positive test
    response = client.get(UNIT_URL+resource_name+'?search_word=of',headers = headers_auth)
    print("*****res:",response.json())
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['name'] == "Creation of World":
            found = True
    assert found

    # searching with audioformat:- positive test
    url_with_query_string = UNIT_URL+resource_name+"?audio_format=mp3"
    response = client.get(url_with_query_string, headers=headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['name'] == "Creation of World":
            found = True
    assert found

     # searching with link - positive test
    url_with_query_string = UNIT_URL+resource_name+"?link=http://somewhere.com/something"
    response = client.get(url_with_query_string, headers=headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['name'] == "Creation of World":
            found = True
    assert found

    # searching with reference:exact match - positive test
    response = client.get(UNIT_URL+resource_name+"?search_word=MAT",headers = headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['name'] == "Creation of World":
            found = True
    assert found

    # searching with reference:partial match - positive test
    response = client.get(UNIT_URL+resource_name+"?search_word=MAT 2",headers = headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['name'] == "Creation of World":
            found = True
    assert found

    # searching with not available reference keyword- negative test
    response = client.get(UNIT_URL+resource_name+"?search_word=chapter:999",
        headers = headers_auth)
    assert len(response.json()) ==  0
    assert_not_available_content(response)

    # searching with metadata with special characters:exact match - positive test
    response = client.get(UNIT_URL+resource_name+"?search_word=ABP, Audio Bible Project",
        headers = headers_auth)
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['name'] == "Creation of World":
            found = True
    assert found

    # searching with partial metadata:fuzzy match - positive test
    response = client.get(UNIT_URL+resource_name+"?search_word=Bible Project",headers = headers_auth)
    print("?????resp:",response.json())
    assert len(response.json()) > 0
    found = False
    for item in response.json():
        assert_positive_get(item)
        if item['name'] == "Creation of World":
            found = True
    assert found

    # searching with invalid search word - negative test
    response = client.get(UNIT_URL+resource_name+"?search_word=Bibles",headers = headers_auth)
    assert len(response.json()) ==  0
    found = False
    for item in response.json():
        if item['name'] == "Creation of World":
            found = True
    assert not found

def test_get_incorrect_data():
    '''Check for input validations in get'''
    resource_name = 'ur_TTT'
    response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    assert_input_validation_error(response)
    resp, resource_name = check_post([])
    assert resp.status_code == 201
    resource_name = resource_name.replace('audiobible', 'audio')
    response = client.get(UNIT_URL+resource_name, headers=headers_auth)
    assert response.status_code == 404

def test_references():
    '''Tests for handling verses in reference'''
    data = [
        {'name':"12 apostles",
        "reference": {"book":"MAT", "chapter":2, "verseNumber":3, \
            "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"},
        {'name':"miracles",
        "reference": {"book":"MRK", "chapter":2, \
            "bookEnd":"LUK", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"},
        {'name':"origin of world",
        "reference": {"book":"GEN", "chapter":1, "verseNumber":1, \
            "bookEnd":"GEN", "chapterEnd":2},
        "link":"http://somewhere.com/something"}
    ]
    response, resource_name = check_post(data)
    assert response.status_code == 201

    get_response = client.get(UNIT_URL+resource_name,headers=headers_auth)

    # Case 1 : passing both starting and ending verses - positive test
    assert get_response.json()[0]['name'] == "12 apostles"
    assert get_response.json()[0]['reference']['verseNumber'] == 3
    assert get_response.json()[0]['reference']['verseEnd'] == 6

    # Case 2: passing only ending and  verse- positive test
    assert get_response.json()[1]['name'] == "miracles"
    assert get_response.json()[1]['reference']['verseNumber'] == 0
    assert get_response.json()[1]['reference']['verseEnd'] == 6

    # Case 3 : passing only starting verse- positive test
    assert get_response.json()[2]['name'] == "origin of world"
    assert get_response.json()[2]['reference']['verseNumber'] == 1
    assert get_response.json()[2]['reference']['verseEnd'] == 999
   
    # case 4: verse start > verse end - negative test
    data = [
        {'name':"resurrection",
        "reference": {"book":"MAT", "chapter":2, "verseNumber":30, \
            "bookEnd":"JHN", "chapterEnd":10, "verseEnd":6 },
        "link":"http://somewhere.com/something"}
    ]
    response = client.post('/v2/resources', headers=headers_auth, json=data)
    assert response.status_code == 422
    assert_input_validation_error(response)

    # Handling chapters
    # case 1 : assigning invalid values to chapter - negative test
    data = [
        {'name':"resurrection",
        "reference": {"book":"MAT", "chapter":0, "verseNumber":3, \
            "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"}
    ]
    response = client.post('/v2/resources', headers=headers_auth, json=data)
    assert response.status_code == 422
    assert_input_validation_error(response)

    # case 2 - chapter = -1 - negative test
    data = [
        {'name':"resurrection",
        "reference": {"book":"MAT", "chapter":-1 ,"verseNumber":3, \
            "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"}
    ]
    response = client.post('/v2/resources', headers=headers_auth, json=data)
    assert response.status_code == 422
    assert_input_validation_error(response)

    # case 3: chapter start > chapter end - negative test
    data = [
        {'name':"resurrection",
        "reference": {"book":"MAT", "chapter":20, "verseNumber":3, \
            "bookEnd":"JHN", "chapterEnd":2, "verseEnd":6 },
        "link":"http://somewhere.com/something"}
    ]
    response = client.post('/v2/resources', headers=headers_auth, json=data)
    assert response.status_code == 422
    assert_input_validation_error(response)

     # case 4: not passing chapter field - negative test
    data = [
        {'name':"resurrection",
        "reference": {"book":"MAT", "verseNumber":3, \
            "bookEnd":"JHN", "verseEnd":6 },
        "link":"http://somewhere.com/something"}
    ]
    response = client.post('/v2/resources', headers=headers_auth, json=data)
    assert response.status_code == 422
    assert_input_validation_error(response)

def test_put_after_upload():
    '''Positive tests for put'''
    data = [
        {'name':"12 apostles",
        "reference": {"book":"MAT", "chapter":2, "verseNumber":3, \
            "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"},
        {'name':"miracles",
        "reference": {"book":"MRK", "chapter":2, "verseNumber":3, \
            "bookEnd":"LUK", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"}
    ]
    response, resource_name = check_post(data)
    assert response.status_code == 201

    get_response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    audio_id_1 = get_response.json()[0]['audioId']
    audio_id_2 = get_response.json()[1]['audioId']

    # positive PUT
    new_data = [
        {'audioId':audio_id_1,
        'name':"12 apostles",
        "reference": {"book":"MRK", "chapter":10, "verseNumber":11, \
            "bookEnd":"LUK", "chapterEnd":12, "verseEnd":13 },
        "link":"http://anotherplace.com/something",
        "metaData":{"newkey1":"newvalue1"}},
        {'audioId':audio_id_2,
        'name':"miracles",
        "reference": {"book":"MAT", "chapter":10, "verseNumber":11, \
            "bookEnd":"JHN", "chapterEnd":12, "verseEnd":13 },
        "link":"http://somewhereelse.com/something",
        "metaData":{"newkey2":"newvalue2"}}
    ]
    #without auth
    response = client.put(UNIT_URL+resource_name, json=new_data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    #with auth
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    
    assert response.json()['message'] == 'Audio Bibles updated successfully'
    for i,item in enumerate(response.json()['data']):
        assert_positive_get(item)
        assert response.json()['data'][i]['name'] == new_data[i]['name']
        assert response.json()['data'][i]['reference']['book'] == new_data[i]['reference']['book']
        assert response.json()['data'][i]['reference']['chapter'] == new_data[i]['reference']['chapter']
        assert response.json()['data'][i]['reference']['verseNumber'] == new_data[i]['reference']['verseNumber']
        assert response.json()['data'][i]['reference']['bookEnd'] == new_data[i]['reference']['bookEnd']
        assert response.json()['data'][i]['reference']['chapterEnd'] == new_data[i]['reference']['chapterEnd']
        assert response.json()['data'][i]['reference']['verseEnd'] == new_data[i]['reference']['verseEnd']
        assert response.json()['data'][i]['metaData'] == new_data[i]['metaData']

    resource_name = resource_name.replace('1', '10')
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=[])
    assert response.status_code == 404

def test_put_incorrect_data():
    ''' tests to check input validation in put API'''

    post_data = [
        {'name':"miracles",
        "link":"http://somewhere.com/something"},
        {'name':"12 apostles",
        "link":"http://somewhere.com/something"}
    ]
    resp, resource_name = check_post(post_data)
    assert resp.status_code == 201

    get_response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    audio_id_1 = get_response.json()[0]['audioId']
    audio_id_2 = get_response.json()[1]['audioId']
    # single data object instead of list
    data =  {'audioId': audio_id_1,
            'name':"apostles",
            "link":"http://anotherplace.com/something"}
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # data object with missing mandatory fields
    data = [
        {'name':"12 apostles",
        "link":"http://anotherplace.com/something"}
            ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    data = [
        {"link":"http://somewhere.com/something"}    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    # incorrect data values in fields
    #updating with reference in incorrect syntax of bookCode
    data = [
        {'audioId': audio_id_2,
        'name':"12 apostles",
        "reference": {"book":"MATHEW", "chapter":2, "verseNumber":3,
                    "bookEnd":"JOHN", "chapterEnd":5, "verseEnd":6 }
        }
                ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #updating with link in incorrect syntax
    data = [
        {'audioId': audio_id_2,
        'name':"12 apostles",
        "link":"filename.txt"}    ]
    response = client.put(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #updating with incorrect resource name
    resource_name1 = resource_name.replace('audiobible', 'audio')
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
        "resourceType": "audiobible",
        'language': 'ml',
        "version": "TTT",
        "year": 2020
    }
    #create resource
    response = client.post('/v2/resources', headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == "Resource created successfully"
    resource_name = response.json()['data']['resourceName']

    #create audiobibles
    data = [
        {'name':"12 apostles",
        "link":"http://somewhere.com/something"},
        {'name':"miracles",
        "link":"http://somewhere.com/something"}
    ]
    response = client.post(UNIT_URL+resource_name, headers=headers_auth, json=data)
    assert response.status_code == 201

    get_response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    audio_id_1 = get_response.json()[0]['audioId']
    audio_id_2 = get_response.json()[1]['audioId']

    #update audiobibles with created SA user
    new_data = [
        {'audioId': audio_id_1,
        'name':"12 apostles",
        "link":"http://anotherplace.com/something"},
        {'audioId': audio_id_1,
        'name':"miracles",
        "link":"http://somewhereelse.com/something"}]
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 201
    assert response.json()['message'] == 'Audio Bibles updated successfully'

    #update with VA not created user
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=new_data)
    assert response.status_code == 403
    assert response.json()['error'] == 'Permission Denied'

def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    data = [
    	{'name':"12 apostles",
        "link":"http://somewhere.com/something"}
    ]
    resourcetypeapi_get_accessrule_checks_app_userroles("audiobible",UNIT_URL,data)

def test_soft_delete():
    '''check soft delete in audiobibles'''
    data = [
        {'name':"the Gods reveals himself in new testament",
        "reference": {"book":"MAT", "chapter":2, "verseNumber":3,\
            "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
        "link":"http://somewhere.com/something"
        }
            ]
    response, resource_name = check_post(data)
    assert response.json()

    get_response1 = client.get(UNIT_URL+resource_name,headers=headers_auth)
    audio_id = get_response1.json()[0]['audioId']
    delete_data = [
        {
            'audioId':audio_id,
            'name' :"the Gods reveals himself in new testament"
        }
    ]
    assert len(get_response1.json()) == len(data)
    delete_data[0]['active'] = False

    response = client.put(UNIT_URL+resource_name,headers=headers_auth, json=delete_data)
    assert response.status_code == 201
    assert response.json()
    assert response.json()["message"] == "Audio Bibles updated successfully"

    get_response2 = client.get(UNIT_URL+resource_name, headers=headers_auth)
    assert len(get_response2.json()) == len(data) - len(delete_data)

    get_response3 = client.get(UNIT_URL+resource_name+'?active=false',headers=headers_auth)
    assert len(get_response3.json()) == len(delete_data)

def test_delete_default():
    ''' positive test case, checking for correct return of deleted audiobible ID'''
    #create new data
    response,resource_name = test_post_default()
    headers_auth = {"contentType": "application/json",#pylint: disable=redefined-outer-name
                "accept": "application/json"}
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    post_response = client.get(UNIT_URL+resource_name+ \
        "?book_code=Bible%20project%20audio&name=creation",\
        headers=headers_auth)
    assert post_response.status_code == 200
    assert len(post_response.json()) == 1
    for item in post_response.json():
        assert_positive_get(item)
    audio_response = client.get(UNIT_URL+resource_name,headers=headers_auth)
    audio_id = audio_response.json()[0]['audioId']

    #Delete without authentication
    headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
    response = client.delete(UNIT_URL+resource_name + \
        "?audio_id=" + str(audio_id), headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

     #Delete audiobible with other API user,AgAdmin,AgUser,VachanUser,BcsDev,'VachanContentAdmin','VachanContentViewer'
    for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev','VachanContentAdmin','VachanContentViewer']:
        headers_au = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users[user]['token']
        }
        response = client.delete(UNIT_URL+resource_name + \
            "?audio_id=" + str(audio_id), headers=headers_au)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Delete audiobible with Vachan Admin
    headers_va = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+initial_test_users['VachanAdmin']['token']
            }
    response = client.delete(UNIT_URL+resource_name + \
        "?audio_id=" + str(audio_id), headers=headers_va)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Audio Bible id {audio_id} deleted successfully"


def test_delete_default_superadmin():
    ''' positive test case, checking for correct return of deleted audiobible ID'''
    #Created User or Super Admin can only delete audiobible
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

    audio_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    audio_id = audio_response.json()[0]['audioId']

     #Delete audiobible with Super Admin
    response = client.delete(UNIT_URL+resource_name + "?audio_id=" +\
         str(audio_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Audio Bible id {audio_id} deleted successfully"
    #Check audiobible is deleted from table
    audio_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    post_response = client.get(UNIT_URL+resource_name+ \
        "?book_code=Bible%20project%20audio&name=creation",\
        headers=headers_sa)
    assert_not_available_content(post_response)
    logout_user(test_user_token)
    return response,resource_name

def test_delete_audio_id_string():
    '''positive test case, audiobible id as string'''
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

    audio_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    audio_id = audio_response.json()[0]['audioId']
    audio_id = str(audio_id)

    #Delete audiobible with Super Admin
    response = client.delete(UNIT_URL+resource_name + \
        "?audio_id=" + str(audio_id), headers=headers_sa)
    assert response.status_code == 200
    assert response.json()['message'] ==\
         f"Audio Bible id {audio_id} deleted successfully"
    #Check audiobible audiobible is deleted from table
    audio_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    logout_user(test_user_token)


def test_delete_missingvalue_audio_id():
    '''Negative Testcase. Passing input data without audioId'''
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
    response = client.delete(UNIT_URL+resource_name + "?audio_id=", headers=headers_sa)
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
    audio_response = client.get(UNIT_URL+resource_name,headers=headers_sa)
    audio_id = audio_response.json()[0]['audioId']

    response = client.delete(UNIT_URL+ "?audio_id=" + str(audio_id), headers=headers_sa)
    assert response.status_code == 404
    logout_user(test_user_token)

def test_delete_notavailable_content():
    ''' request a non existing audiobible ID, Ensure there is no partial matching'''
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
    audio_id=20000
     #Delete audiobible with Super Admin
    response = client.delete(UNIT_URL+resource_name + \
        "?audio_id=" + str(audio_id), headers=headers_sa)
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


    #Restore content with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev,'VachanContentAdmin','VachanContentViewer'
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev','VachanContentAdmin','VachanContentViewer']:
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
    #Check audiobible exists after restore
    restore_response =  client.get(UNIT_URL+resource_name+ \
        "?name=creation",\
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
    response = client.delete(RESOURCE_URL + "?resource_id=" + str(resource_id), headers=headers_auth)
    assert response.status_code == 200
    #Restoring data
    #Restore content with Super Admin after deleting resource
    restore_response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    restore_response.status_code = 404
    logout_user(test_user_token)