'''Test cases for extract text related APIs'''
from requests.api import head
from app.schema import schemas, schema_auth
from . import client
from . import assert_input_validation_error, assert_not_available_content
from . import check_default_get
from .test_versions import check_post as add_version
from .test_resources import check_post as add_resource
from .test_bibles import gospel_books_data
from .conftest import initial_test_users

UNIT_URL = 'v2/resources/'
SENT_URL = UNIT_URL+ "get-sentence"
headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "Authentication":"Bearer"+" "+initial_test_users['APIUser']['token']
            }

def assert_positive_get(item):
    '''Check for properties a normal sentence response will have'''
    assert "sentenceId" in item
    assert isinstance(item['sentenceId'], int)
    assert "surrogateId" in item
    assert isinstance(item['surrogateId'], str)
    assert "sentence" in item

commentary_data = [
        {'bookCode':'gen', 'chapter':0, 'commentary':'book intro to Genesis'},
        {'bookCode':'gen', 'chapter':1, 'verseStart':0, 'verseEnd': 0,
            'commentary':'chapter intro to Genesis 1'},
        {'bookCode':'gen', 'chapter':1, 'verseStart':1, 'verseEnd': 10,
            'commentary':'the begining'},
        {'bookCode':'gen', 'chapter':1, 'verseStart':3, 'verseEnd': 30,
            'commentary':'the creation'},
        {'bookCode':'gen', 'chapter':1, 'verseStart':-1, 'verseEnd': -1,
            'commentary':'Chapter Epilogue. God completes creation in 6 days.'},
        {'bookCode':'gen', 'chapter':-1, 'commentary':'book Epilogue.'},

        {'bookCode':'exo', 'chapter':1, 'verseStart':1,
            "verseEnd":1, 'commentary':'first verse of Exodus'},
        {'bookCode':'exo', 'chapter':1, 'verseStart':1,
        "verseEnd":10, 'commentary':'first para of Exodus'},
        {'bookCode':'exo', 'chapter':1, 'verseStart':1,
        "verseEnd":25, 'commentary':'first few paras of Exodus'},
        {'bookCode':'exo', 'chapter':1, 'verseStart':20,
        "verseEnd":25, 'commentary':'a middle para of Exodus'},
        {'bookCode':'exo', 'chapter':0, 'commentary':'Book intro to Exodus'}
    ]


def create_resources():
    '''prior steps and post attempt, without checking the response'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    headers_auth["App"] = schema_auth.App.VACHAN.value
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version for get sentence",
    }
    add_version(version_data)
    resource_data = {
        "resourceType": "bible",
        "language": "hi",
        "version": "TTT",
        "year": 2020,
        "revision": 1,
        "accessPermissions":[schemas.ResourcePermissions.CONTENT.value, schemas.ResourcePermissions.OPENACCESS.value]
    }
    resource = add_resource(resource_data)
    bible_name = resource.json()['data']['resourceName']
    resp = client.post(f'/v2/resources/bibles/{bible_name}/books', headers=headers_auth, json=gospel_books_data)
    assert resp.status_code == 201

    resource_data = {
        "resourceType": "commentary",
        "language": "en",
        "version": "TTT",
        "year": 2020,
        "revision": 1,
        "accessPermissions":[schemas.ResourcePermissions.CONTENT.value, schemas.ResourcePermissions.OPENACCESS.value]

    }
    resource = add_resource(resource_data)
    commentary_name = resource.json()['data']['resourceName']
    resp = client.post(f'/v2/commentaries/{commentary_name}', headers=headers_auth, json=commentary_data)
    assert resp.status_code == 201

    return bible_name, commentary_name

def test_get_poisitive():
	'''normal tests for all possible get queries'''
	# Before adding data
	resp = client.get(SENT_URL+"?resource_name=hi_TTT_1_bible", headers= headers_auth)
	assert resp.status_code == 404

	# Add data
	bible_name, commentary_name = create_resources()

	headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
	headers_auth['App'] = schema_auth.App.API.value
	check_default_get(SENT_URL, headers_auth, assert_positive_get)

	# filtering with various params
	resp = client.get(SENT_URL, headers=headers)
	assert resp.status_code == 401
	assert resp.json()['error'] == 'Authentication Error'
	#with auth
	resp = client.get(SENT_URL, headers=headers_auth)
	assert resp.status_code == 200
	full_resp = resp.json()
	for item in full_resp:
		assert_positive_get(item)

	#without auth
	resp = client.get(SENT_URL+"?language_code=hi", headers=headers)
	assert resp.status_code == 401
	assert resp.json()['error'] == 'Authentication Error'
	#with auth
	resp = client.get(SENT_URL+"?language_code=hi", headers=headers_auth)
	assert resp.status_code == 200
	only_hi = resp.json()
	for item in only_hi:
		assert_positive_get(item)
	assert 0 < len(only_hi) <= len(full_resp)

	resp = client.get(SENT_URL+"?resource_type=commentary", headers=headers_auth)
	assert resp.status_code == 200
	only_commentary = resp.json()
	for item in only_commentary:
		assert_positive_get(item)
	assert 0 < len(only_commentary) < len(full_resp)+len(only_commentary)

	resp = client.get(SENT_URL+'?resource_name='+bible_name, headers=headers_auth)
	assert resp.status_code == 200
	chosen_bible = resp.json()
	assert len(chosen_bible) == 8
	for item in chosen_bible:
		assert_positive_get(item)

	resp = client.get(SENT_URL+'?resource_name='+commentary_name, headers=headers_auth)
	assert resp.status_code == 200
	chosen_commentary = resp.json()
	assert len(chosen_commentary) == 11
	for item in chosen_commentary:
		assert_positive_get(item)

	for buk in ['mat','mrk','luk','jhn']:
		resp = client.get(SENT_URL+'?resource_name='+bible_name+'&books='+buk, headers=headers_auth)
		assert resp.status_code == 200
		chosen_book = resp.json()
		assert len(chosen_book) == 2
		for item in chosen_book:
			assert_positive_get(item)


	resp = client.get(SENT_URL+'?resource_name='+commentary_name+'&books=gen', headers=headers_auth)
	assert resp.status_code == 200
	chosen_book = resp.json()
	assert len(chosen_book) == 6
	for item in chosen_book:
		assert_positive_get(item)

	resp = client.get(SENT_URL+'?resource_name='+commentary_name+'&books=exo', headers=headers_auth)
	assert resp.status_code == 200
	chosen_book = resp.json()
	assert len(chosen_book) == 5
	for item in chosen_book:
		assert_positive_get(item)

def test_get_negatives():
	'''error or not available cases'''
	# Add data
	bible_name, commentary_name = create_resources()
	headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
	headers_auth['App'] = schema_auth.App.API.value

	for buk in ['mat','mrk','luk','jhn']:
		resp = client.get(SENT_URL+'?resource_name='+commentary_name+'&books='+buk, headers=headers_auth)
		assert_not_available_content(resp)

	for buk in ['gen', 'exo']:
		resp = client.get(SENT_URL+'?resource_name='+bible_name+'&books='+buk, headers=headers_auth)
		assert_not_available_content(resp)

	# wrong resource_name
	resp = client.get(SENT_URL+'?resource_name='+bible_name.replace('bible','commentary')+'&books=mat', headers=headers_auth)
	assert resp.status_code == 404

	# wrong content
	resp = client.get(SENT_URL+'?resource_type=usfm&books=mat', headers=headers_auth)
	assert resp.status_code == 404

	# wrong lang
	resp = client.get(SENT_URL+'?language_code=ur', headers=headers_auth)
	assert resp.status_code == 404

	# worng pattern for book
	resp = client.get(SENT_URL+'?books=matthew', headers=headers_auth)
	assert_input_validation_error(resp)

	# worng pattern for resource
	resp = client.get(SENT_URL+'?resource_name=bible', headers=headers_auth)
	assert_input_validation_error(resp)

	# worng pattern for lang
	resp = client.get(SENT_URL+'?language_code="hindi or malayalam"', headers=headers_auth)
	assert_input_validation_error(resp)


	# worng pattern for book
