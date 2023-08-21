'''Tests the translation APIs that do need projects available in DB'''
import json
import time
from app.main import log
from app.schema import schema_auth, schemas
from . import client
from . import check_default_get
from . import assert_not_available_content,assert_input_validation_error
from .conftest import initial_test_users
from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER,logout_user


UNIT_URL = '/v2/lookup/stopwords'
GER_URL = '/v2/nlp/stopwords'
JOBS_URL = '/v2/jobs'
RESTORE_URL = '/v2/admin/restore'

headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json", "accept": "application/json"}

update_obj1 = {
        "stopWord": "उसका",
        "active": False,
        "metaData": {
        "type": "verb"
     }
    }
update_obj2 = {
        "stopWord": "हम",
        "active": False,
    }
update_wrong_obj =  {
        "stopWord": "prayed",
        "active": False,
        "metaData": {
        "type": "verb"
     }
    }
add_obj = [
  "asd",
  "ert",
  "okl"
]

sentences = [
    "इसलिए हे भाइयों, हमने अपनी सारी सकेती और क्लेश में तुम्हारे विश्वास से तुम्हारे विषय में शान्ति पाई।",
    "क्योंकि अब यदि तुम प्रभु में स्थिर रहो तो हम जीवित हैं।",
    "और जैसा आनन्द हमें तुम्हारे कारण अपने परमेश्वर के सामने है, उसके बदले तुम्हारे विषय में हम किस रीति से परमेश्वर का धन्यवाद करें?",
    "हम रात दिन बहुत ही प्रार्थना करते रहते हैं, कि तुम्हारा मुँह देखें, और तुम्हारे विश्वास की घटी पूरी करें।",
    "अब हमारा परमेश्वर और पिता आप ही और हमारा प्रभु यीशु, तुम्हारे यहाँ आने के लिये हमारी अगुआई करे।",
    "और प्रभु ऐसा करे, कि जैसा हम तुम से प्रेम रखते हैं; वैसा ही तुम्हारा प्रेम भी आपस में, और सब मनुष्यों के साथ बढ़े, और उन्नति करता जाए"
]
sentence_list = [{"sentenceId":i, "sentence":s} for i,s in enumerate(sentences)]

def assert_positive_get_stopwords(item):
    '''Check for the properties in the normal return object'''
    assert "stopWord" in item
    assert "stopwordType" in item
    if item["stopwordType"] == "auto generated":
        assert "confidence" in item
        assert isinstance(item["confidence"], float)
    assert "active" in item

def test_get_default():
    '''positive test case, without optional params'''
    check_default_get(UNIT_URL+'/hi', headers=headers,assert_positive_get=
        assert_positive_get_stopwords)

def assert_positive_response(out):
    '''Check the properties in the update response'''
    assert "message" in out
    assert "data" in out

def test_get_stop_words():
    '''Positve tests for get stopwords API'''
    default_response = client.get(UNIT_URL+'/hi?', headers=headers)
    assert default_response.status_code == 200
    assert isinstance(default_response.json(), list)
    for item in default_response.json():
        assert_positive_get_stopwords(item)

    response = client.get(UNIT_URL+'/hi?include_system_defined=False', headers=headers)
    assert response.status_code == 200
    sw_types = {sw_dic['stopwordType'] for sw_dic in response.json()}
    assert "system defined" not in sw_types

    response = client.get(UNIT_URL+'/hi?include_user_defined=False', headers=headers)
    assert response.status_code == 200
    sw_types = {sw_dic['stopwordType'] for sw_dic in response.json()}
    assert "user defined" not in sw_types

    response = client.get(UNIT_URL+'/hi?include_auto_generated=False', headers=headers)
    assert response.status_code == 200
    sw_types = {sw_dic['stopwordType'] for sw_dic in response.json()}
    assert "auto generated" not in sw_types

    response = client.get(UNIT_URL+'/hi?only_active=True', headers=headers)
    assert response.status_code == 200
    out = {sw_dic['active'] for sw_dic in response.json()}
    assert False not in out

def test_get_notavailable_code():
    ''' request a not available language_code'''
    response = client.get(UNIT_URL+"/abc")
    assert_not_available_content(response)

def test_update_stopword():
    '''Positve tests for update stopwords API'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']

    response = client.put(UNIT_URL+'/hi?',headers=headers_auth, json=update_obj1)
    assert response.status_code == 201
    assert_positive_response(response.json())
    assert_positive_get_stopwords(response.json()['data'])
    assert response.json()['message'] == "Stopword info updated successfully"

    response = client.put(UNIT_URL+'/hi?',headers=headers_auth, json=update_obj2)
    assert response.status_code == 201
    assert_positive_response(response.json())
    assert_positive_get_stopwords(response.json()['data'])
    assert response.json()['message'] == "Stopword info updated successfully"

    response = client.put(UNIT_URL+'/hi?',headers=headers_auth, json=update_wrong_obj)
    assert response.status_code == 404

def test_add_stopword():
    '''Positve tests for add stopwords API'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']

    response = client.post(UNIT_URL+'/aa?',headers=headers_auth, json=add_obj)
    assert response.status_code == 201
    assert_positive_response(response.json())
    for item in response.json()['data']:
        assert_positive_get_stopwords(item)
        assert item['stopwordType'] == "user defined"
        assert item['active'] is True
        assert item['stopWord'] in add_obj
    assert len(response.json()['data']) == len(add_obj)

    response = client.post(UNIT_URL+'/aa?',headers=headers_auth, json=["asd"])
    assert response.status_code == 201
    assert_positive_response(response.json())
    assert not response.json()['data']
    assert response.json()['message'] == "0 stopwords added successfully"

    response = client.post(UNIT_URL+'/aa?',headers=headers_auth, json=["hty"])
    assert response.status_code == 201
    assert_positive_response(response.json())
    assert response.json()['data']
    assert response.json()['data'][0]['stopWord'] == "hty"
    assert response.json()['data'][0]['stopwordType'] == "user defined"
    assert response.json()['data'][0]['active'] is True
    assert len(response.json()['data']) == 1


    response = client.post(UNIT_URL+'/hi?',headers=headers_auth, json=["की"])
    assert response.status_code == 201
    assert_positive_response(response.json())
    assert not response.json()['data']
    assert response.json()['message'] == "0 stopwords added successfully"

    response = client.post(UNIT_URL+'/hi?',headers=headers_auth, json=["चुनाव"])
    assert response.status_code == 201
    assert_positive_response(response.json())
    assert response.json()['data']
    assert response.json()['data'][0]['stopWord'] == "चुनाव"
    assert response.json()['data'][0]['stopwordType'] == "user defined"
    assert response.json()['data'][0]['active'] is True
    assert len(response.json()['data']) == 1

# def test_create_job():
#     '''Positve tests for create job API'''
#     response = client.post(JOBS_URL,headers=headers)
#     assert response.status_code == 201
#     assert_positive_response(response.json())
#     assert "jobId" in response.json()['data']
#     assert "status" in response.json()['data']
#     assert response.json()['data']['status'] == 'job created'

# def test_check_job_status():
#     '''Positve tests for checking job status API'''
#     response = client.post(JOBS_URL,headers=headers)
#     assert response.status_code == 201
#     job_id = response.json()['data']['jobId']
#     response = client.get(JOBS_URL+'/?job_id='+str(job_id),headers=headers)
#     assert response.status_code == 200
#     assert_positive_response(response.json())
#     assert "jobId" in response.json()['data']
#     assert "status" in response.json()['data']
#     if response.json()['data']['status'] == 'job finished':
#         assert 'output' in response.json()['data']

def get_job_status(job_id):
    '''Retrieve status of a job'''
    # registered user can get job status
    response = client.get(JOBS_URL+'/?job_id='+str(job_id),headers=headers)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'
    
    headers_auth['Authorization'] = "Bearer"+" "+ initial_test_users['APIUser']['token']
    response = client.get(JOBS_URL+'/?job_id='+str(job_id),headers=headers_auth)
    assert response.status_code == 200
    assert_positive_response(response.json())
    assert "jobId" in response.json()['data']
    assert "status" in response.json()['data']
    return response

def test_jobs():
  """get job test"""
  #not available jobid
  headers_auth['Authorization'] = "Bearer"+" "+ initial_test_users['APIUser']['token']
  response = client.get(JOBS_URL+'/?job_id='+str(999999999999999999),headers=headers_auth)
  assert response.status_code == 404
  assert response.json()["error"] == "Requested Content Not Available"

def assert_positive_sw_out(item):
    '''Check for the properties in output of sw job'''
    assert "stopWord" in item
    assert "confidence" in item
    assert isinstance(item["confidence"], float)
    assert "active" in item

def add_version():
    '''adds version in db'''
    version_data = {
        "versionAbbreviation": "TW",
        "versionName": "test version",
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    headers_auth['app'] = schema_auth.AdminRoles.VACHANADMIN.value
    result = client.post('/v2/resources/versions', headers=headers_auth, json=version_data)
    assert result.status_code == 201

def add_bible_resource():
    '''creates bible resource'''
    src_data = {
    "resourceType": "bible",
    "language": "hi",
    "version": "TW",
    "revision": 1,
    "year": 2020,
    "license": "CC-BY-SA",
    "metaData": {"owner": "someone" },
    "accessPermissions": [schemas.ResourcePermissions.OPENACCESS, schemas.ResourcePermissions.CONTENT]
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    resource = client.post('/v2/resources', headers=headers_auth, json=src_data)
    assert resource.status_code == 201
    table_name = resource.json()['data']['resourceName']
    return table_name

def add_dict_resource():
    '''creates vocabulary resource'''
    resource_data = {
        "resourceType": "vocabulary",
        "language": "hi",
        "version": "TW",
        "revision": 1,
        "year": 2000,
        "accessPermissions": [schemas.ResourcePermissions.OPENACCESS, schemas.ResourcePermissions.CONTENT]
    }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    resource = client.post('/v2/resources', headers=headers_auth, json=resource_data)
    assert resource.status_code == 201
    table_name = resource.json()['data']['resourceName']
    return table_name

def add_bible_books(table_name):
    '''uploads bible books in db'''
    data = []
    input_files = ['41-MAT.usfm', '42-MRK.usfm', '43-LUK.usfm']
    for book in input_files:
        book_data = open('test/resources/' + book, 'r',encoding='utf-8').read()
        data.append({"USFM":book_data})
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.post('/v2/resources/bibles/'+table_name+'/books', headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()["message"] == "Bible books uploaded and processed successfully"

def add_tw_dict(table_name):
    '''uploads tw vocabulary'''
    data = json.load(open('test/resources/hindi.json'))
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.post('/v2/vocabularies/'+table_name, headers=headers_auth, json=data)
    assert response.status_code == 201

def test_generate_stopwords():
    '''Positve tests for generate stopwords API'''
    add_version()
    table_name = add_bible_resource()
    add_bible_books(table_name)

    dict_table_name = add_dict_resource()
    add_tw_dict(dict_table_name)
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']

    response = client.post(GER_URL+'/generate?language_code=hi',headers=headers_auth)
    assert response.status_code == 201
    assert_positive_response(response.json())
    assert "jobId" in response.json()['data']
    assert "status" in response.json()['data']
    for i in range(10):
        job_response = get_job_status(response.json()['data']['jobId'])
        status = job_response.json()['data']['status']
        if status == 'job finished':
            break
        log.info("sleeping for a minute in SW generate test")
        time.sleep(60)
    assert job_response.json()['data']['status'] == 'job finished'
    assert 'output' in job_response.json()['data']
    for item in job_response.json()['data']['output']['data']:
        assert_positive_sw_out(item)
    assert job_response.json()['message'] == "Stopwords identified out of limited resources. Manual verification recommended"

    response = client.post(GER_URL+'/generate?language_code=hi&use_server_data=False',
                headers=headers_auth, json=sentence_list)
    assert response.status_code == 201
    assert_positive_response(response.json())
    assert "jobId" in response.json()['data']
    assert "status" in response.json()['data']
    job_id = response.json()['data']['jobId']
    for i in range(5):
        job_response = get_job_status(job_id)
        status = job_response.json()['data']['status']
        if status == 'job finished':
            break
        log.info("sleeping for a minute in SW generate test")
        time.sleep(60)
    assert job_response.json()['data']['status'] == 'job finished'
    assert job_response.json()['message'] == "Not enough data to generate stopwords"

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
    response = client.post(GER_URL+'/generate?language_code=hi',headers=headers_auth,
             json=sentence_list)
    assert response.status_code == 201
    assert_positive_response(response.json())
    assert "jobId" in response.json()['data']
    assert "status" in response.json()['data']
    for i in range(10):
        job_response1 = get_job_status(response.json()['data']['jobId'])
        status = job_response1.json()['data']['status']
        if status == 'job finished':
            break
        log.info("sleeping for a minute in SW generate test")
        time.sleep(60)
    assert job_response1.json()['data']['status'] == 'job finished'
    assert 'output' in job_response1.json()['data']
    for item in job_response1.json()['data']['output']['data']:
        assert_positive_sw_out(item)
    assert job_response1.json()['message'] == "Stopwords identified out of limited resources. Manual verification recommended"

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    response = client.post(GER_URL+'/generate?language_code=hi&source_name='+dict_table_name,
        headers=headers_auth, json=sentence_list)
    assert response.status_code == 201
    assert_positive_response(response.json())
    assert "jobId" in response.json()['data']
    assert "status" in response.json()['data']
    for i in range(10):
        job_response2 = get_job_status(response.json()['data']['jobId'])
        status = job_response2.json()['data']['status']
        if status == 'job finished':
            break
        log.info("sleeping for a minute in SW generate test")
        time.sleep(60)
    assert job_response2.json()['data']['status'] == 'job finished'
    assert 'output' in job_response2.json()['data']
    for item in job_response2.json()['data']['output']['data']:
        assert_positive_sw_out(item)
    assert len(job_response2.json()['data']['output']['data']) < len(job_response1.json()
                                                            ['data']['output']['data'])
    assert job_response2.json()['message'] == "Automatically generated stopwords for the given language"

def test_delete_stopword():
    '''Test the removal of a stopword'''
    #Adding stopwords
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.post(UNIT_URL+'/aa?',headers=headers_auth, json=add_obj)
    assert response.status_code == 201
    assert_positive_response(response.json())
    for item in response.json()['data']:
        assert_positive_get_stopwords(item)

    #Ensure stopword is added
    get_response = client.get(UNIT_URL+'/aa?',headers=headers_auth)
    assert get_response.status_code == 200
    assert isinstance(get_response.json(), list)
    for item in get_response.json():
        assert_positive_get_stopwords(item)

    #deleting stopword with no auth - Negative Test
    resp =client.delete(UNIT_URL+'/aa?lang=aa&stopword=asd',headers=headers)
    assert resp.status_code == 401
    assert resp.json()['details'] == "Access token not provided or user not recognized."

    #Deleting stopword with different auth of registerdUser - Positive Test
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    response = client.delete(UNIT_URL+'/aa?lang=aa&stopword=asd',headers=headers_auth)
    assert response.status_code == 201
    assert "successfull" in response.json()['message']

    # Ensure deleted stopword is not present
    get_response = client.get(UNIT_URL+'/aa?',headers=headers_auth)
    assert get_response.status_code == 200
    assert isinstance( get_response.json(), list)
    assert len(get_response.json())==2

    #Create and Delete glossary with superadmin - Positive test
    # Login as Super Admin
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth['Authorization'] = "Bearer"+" "+test_user_token
    response = client.post(UNIT_URL+'/aa?',headers=headers_auth, json=add_obj)
    response =client.delete(UNIT_URL+'/aa?lang=aa&stopword=asd',headers=headers_auth)
    assert response.status_code == 201
    assert "successfull" in response.json()['message']

    # Ensure deleted stopword is not present
    get_response = client.get(UNIT_URL+'/aa?',headers=headers_auth) #, json=["asd"])
    assert get_response.status_code == 200
    assert isinstance( get_response.json(), list)
    assert len(get_response.json())==2

    #Delete with not available resource language
    response =client.delete(UNIT_URL+'/aa?lang=x-ttt&stopword=asd',headers=headers_auth)
    assert response.status_code == 404
    assert "Language not available" in response.json()['details']
    logout_user(test_user_token)


def test_restore_stopword():
    '''positive test case, checking for correct return object'''
    #only Super Admin can restore deleted data
    #Adding a stopword and deleting it
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    response = client.post(UNIT_URL+'/aa?',headers=headers_auth, json=add_obj)
    delete_resp = client.delete(UNIT_URL+'/aa?lang=aa&stopword=asd',headers=headers_auth)

    # Ensure deleted stopword is not present
    get_response = client.get(UNIT_URL+'/aa?',headers=headers_auth)
    assert get_response.status_code == 200
    assert isinstance( get_response.json(), list)
    assert len(get_response.json())==2

    deleteditem_id = delete_resp.json()['data']['itemId']
    data = {"itemId": deleteditem_id}

    #Restoring data
    #Restore stopword without authentication - Negative Test
    response = client.put(RESTORE_URL, headers=headers, json=data)
    assert response.status_code == 401
    assert response.json()['error'] == 'Authentication Error'

    #Restore stopword with other API user,VachanAdmin,AgAdmin,AgUser,VachanUser,BcsDev,'VachanContentAdmin','VachanContentViewer'-Negative Test
    for user in ['APIUser','VachanAdmin','AgAdmin','AgUser','VachanUser','BcsDev','VachanContentAdmin','VachanContentViewer']:
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users[user]['token']
        response = client.put(RESTORE_URL, headers=headers_auth, json=data)
        assert response.status_code == 403
        assert response.json()['error'] == 'Permission Denied'

    #Restore glossary with Super Admin - Positive Test
     # Login as Super Admin
    sa_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(sa_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    headers_auth['Authorization'] = "Bearer"+" "+test_user_token

    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 201
    assert response.json()['message'] == \
    f"Deleted Item with identity {deleteditem_id} restored successfully"

    # Check stopword is restored
    get_response = client.get(UNIT_URL+'/aa?',headers=headers_auth)
    assert get_response.status_code == 200
    assert isinstance( get_response.json(), list)
    assert len(get_response.json())== 3

    #restore with missing data - Negative Test
    data = {}
    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert_input_validation_error(response)

    #Restore with invalid item id - Negative Test
    data = {"itemId":9999}
    response = client.put(RESTORE_URL, headers=headers_auth, json=data)
    assert response.status_code == 404
    assert response.json()['error'] == "Requested Content Not Available"
    logout_user(test_user_token)