'''Set testing environment and define common tests'''
from typing import Dict
from fastapi.testclient import TestClient
from app.main import app
from app.schema import schema_auth

client = TestClient(app)

def gql_request(query, operation="query", variables=None, headers=None):
    '''common format for gql reqests with test db session in context'''
    url = '/graphql'
    post_body = {
        "query": query,
        "operation": operation,
        "variables": variables
    }
    if headers is None:
        headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.post(url, headers=headers, json=post_body)
    return response.json()

def assert_input_validation_error(response):
    '''Check for input validation error in response'''
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()['error'] == "Input Validation Error"

def assert_not_available_content(response):
    '''Checks for empty array returned when requetsed content not available'''
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json())==0

def check_skip(unit_url,headers):
    '''All tests for the skip parameter of an API endpoint'''
    if "?" not in unit_url:
        unit_url += "?"
    else:
        unit_url += "&"
    response1 = client.get(unit_url+"skip=0",headers=headers)
    assert response1.status_code == 200
    assert isinstance( response1.json(), list)
    if len(response1.json()) > 1:
        response2 = client.get(unit_url+"skip=1",headers=headers)
        assert response2.status_code == 200
        assert isinstance( response2.json(), list)
        assert response1.json()[1] == response2.json()[0]

    # fetch a non existant page, with skip and limit values
    response = client.get(unit_url+"skip=50000&limit=10",headers=headers)
    assert_not_available_content(response)

    # skip should be an integer
    response = client.get(unit_url+"skip=abc",headers=headers)
    assert_input_validation_error(response)

    # skip should be a positive integer
    response = client.get(unit_url+"skip=-10",headers=headers)
    assert_input_validation_error(response)


def check_limit(unit_url,headers):
    '''All tests for the limit parameter of an API endpoint'''
    if "?" not in unit_url:
        unit_url += "?"
    else:
        unit_url += "&"
    response = client.get(unit_url+"limit=3",headers=headers)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) <= 3

    # fetch a non existant page, with skip and limit values
    response = client.get(unit_url+"skip=50000&limit=10",headers=headers)
    assert_not_available_content(response)

    # limit should be an integer
    response = client.get(unit_url+"limit=abc",headers=headers)
    assert_input_validation_error(response)

    # limit should be a positive integer
    response = client.get(unit_url+"limit=-1",headers=headers)
    assert_input_validation_error(response)

def check_default_get(unit_url, headers, assert_positive_get):
    '''checks for an array of items of particular type'''
    #without auth
    response = client.get(unit_url,headers=headers)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) > 0
    for item in response.json():
        assert_positive_get(item)

    check_skip(unit_url,headers)
    check_limit(unit_url,headers)

def check_soft_delete(unit_url, check_post, data, delete_data , headers):
    '''set active field to False'''
    response, resource_name = check_post(data)
    assert response.status_code == 201

    get_response1 = client.get(unit_url+resource_name,headers=headers)
    assert len(get_response1.json()) == len(data)


    # positive PUT
    for item in delete_data:
        item['active'] = False
    # headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(unit_url+resource_name,headers=headers, json=delete_data)
    assert response.status_code == 201
    assert response.json()['message'].endswith('updated successfully')
    for item in response.json()['data']:
        assert not item['active']

    get_response2 = client.get(unit_url+resource_name+'?active=true', headers=headers)
    assert len(get_response2.json()) == len(data) - len(delete_data)

    get_response3 = client.get(unit_url+resource_name+'?active=false',headers=headers)
    assert len(get_response3.json()) == len(delete_data)

def check_skip_limit_gql(query,api_name,headers=None):
    '''All tests for the skip and limit parameter of an API endpoint graphql'''

   #checking skip and limit
    var1 = {
  "skip": 0,
  "limit": 3
}
    var2 = {
  "skip": 1,
  "limit": 3
}   
    if headers is None:
        headers = {"contentType": "application/json", "accept": "application/json"}
    executed = gql_request(query=query, operation="query", variables=var1,headers=headers)
    assert isinstance(executed, Dict)
    if len(executed["data"][api_name]) >1:
        executed2 = gql_request(query=query, operation="query", variables=var2,headers=headers)
        assert isinstance(executed2, Dict)
        assert executed["data"][api_name][1] == executed2["data"][api_name][0]
        assert len(executed["data"][api_name]) <= 3
        assert len(executed2["data"][api_name]) <= 3

    # fetch a non existant page, with skip and limit values
    var3 = {
  "skip": 50000,
  "limit": 10
}

    executed3 = gql_request(query=query, operation="query", variables=var3,headers=headers)
    assert_not_available_content_gql(executed3["data"][api_name])

    # skip should be an integer
    var4 = {
  "skip": "abc",
  "limit": 10
}
    query4 = gql_request(query=query, operation="query", variables=var4,headers=headers)
    executed4 = gql_request(query4,headers=headers)
    assert "errors" in executed4.keys()

    # skip should be a positive integer
    var5 = {
  "skip": -5,
  "limit": 10
}
    query5 = gql_request(query=query, operation="query", variables=var5,headers=headers)
    executed5 = gql_request(query5,headers=headers)
    assert "errors" in executed5.keys()

    var6 = {
  "skip": 0,
  "limit":0
}
    executed6 = gql_request(query=query, operation="query", variables=var6,headers=headers)
    assert isinstance(executed6, Dict)
    assert executed6["data"][api_name] == None or executed6["data"][api_name] == []

    # limit should be an integer
    var7 = {
  "skip": "abc",
  "limit": 10
}
    executed7 = gql_request(query=query, operation="query", variables=var7,headers=headers)
    assert "errors" in executed7.keys()

    # limit should be a positive integer
    var8 = {
  "skip": 0,
  "limit": -1
}
    executed8 = gql_request(query=query, operation="query", variables=var8,headers=headers)
    assert "errors" in executed8.keys() or executed8["data"][api_name] == []

def assert_not_available_content_gql(item):
    '''Checks for empty array returned when requetsed content not available'''
    assert len(item) == 0


def resourcetypeapi_get_accessrule_checks_app_userroles(resourcetype, UNIT_URL, data , bible = False):
    """checks for resource api access based on user roles and apps"""
    from .test_versions import check_post as add_version
    from .conftest import initial_test_users
    from . test_auth_basic import login,SUPER_PASSWORD,SUPER_USER

    headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
    #create 5 resources for contents with 5 different permisions
    language_list = ['en','ml','tn','ab','af']
    permission_list = ["content","open-access","publishable","downloadable","derivable"]
    resourcename_list = []
    version_data = {
        "versionAbbreviation": "TTT",
        "versionName": "test version",
    }
    add_version(version_data)
    resource_data = {
        "resourceType": resourcetype,
        "language": "",
        "version": "TTT",
        "revision": 1,
        "year": 2020,
        "license": "CC-BY-SA",
        "accessPermissions": [],
        "metaData": {"owner": "someone", "access-key": "123xyz"}
    }
    #SuperAdmin login and token
    SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(SA_user_data)
    assert response.json()['message'] == "Login Succesfull"
    test_user_token = response.json()["token"]
    SA_TOKEN = "Bearer"+" "+test_user_token

    #create resource and corresponsing contents
    #resource can only created by VA or SA
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    for num in range(5):
        resource_data["language"] = language_list[num]
        resource_data["accessPermissions"] = [permission_list[num]]
        response = client.post('/v2/resources', headers=headers_auth, json=resource_data)
        assert response.status_code == 201
        assert response.json()['message'] == "Resource created successfully"
        resp_data = response.json()['data']['metaData']
        assert permission_list[num]  in resp_data['accessPermissions']
        resource_name = language_list[num] + "_TTT_1_" + resourcetype
        resourcename_list.append(resource_name)

        if bible :
            contentapi_post_url = UNIT_URL+resource_name+'/books'
            response = client.post(contentapi_post_url, headers=headers_auth, json=data)
            assert response.status_code == 201
        else:
            contentapi_post_url = UNIT_URL+resource_name
            response = client.post(contentapi_post_url, headers=headers_auth, json=data)
            assert response.status_code == 201

    API = schema_auth.App.API.value
    AG = schema_auth.App.AG.value
    SMAST = schema_auth.App.SMAST.value
    VACHAN = schema_auth.App.VACHAN.value
    VACHANADMIN = schema_auth.AdminRoles.VACHANADMIN.value
    Apps = [ API,AG,VACHAN,VACHANADMIN, SMAST]

    #Get without Login headers=headers_auth
    #permision -------------------------> content , downloadable , derivable
    print("resource respectivily for -------------------------> \
        content(en) , downloadable(ab) , derivable(af)")
    test_permissions_list  = ["en_TTT_1_" + resourcetype , "ab_TTT_1_" + resourcetype ,
                                "af_TTT_1_" + resourcetype]
    for i in range(len(test_permissions_list)):
        headers_auth = {"contentType": "application/json",
                "accept": "application/json"}  
        print(f"permisioln resource-------------------------> {test_permissions_list[i]}")
        
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = client.get(UNIT_URL+test_permissions_list[i]+'/books',headers=headers_auth)
                assert response.status_code == 401
                assert response.json()["error"] == "Authentication Error"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/versification',headers=headers_auth)
                assert response.status_code == 401
                assert response.json()["error"] == "Authentication Error"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/verses',headers=headers_auth)
                assert response.status_code == 401
                assert response.json()["error"] == "Authentication Error"
            else:    
                response = client.get(UNIT_URL+test_permissions_list[i],headers=headers_auth)
                assert response.status_code == 401
                assert response.json()["error"] == "Authentication Error"
        print(f"Test passed -----> NO LOGIN")

        #Get with AgUser
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = client.get(UNIT_URL+test_permissions_list[i]+'/books',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/versification',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/verses',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
            else:
                response = client.get(UNIT_URL+test_permissions_list[i],headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
        print(f"Test passed -----> AG USER")

        #Get with SanketMASTUser
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = client.get(UNIT_URL+test_permissions_list[i]+'/books',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/versification',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/verses',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
            else:
                response = client.get(UNIT_URL+test_permissions_list[i],headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
        print(f"Test passed -----> SanketMASTUser")

        #Get with VachanUser
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = client.get(UNIT_URL+test_permissions_list[i]+'/books',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/versification',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/verses',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
            else:
                response = client.get(UNIT_URL+test_permissions_list[i],headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
        print(f"Test passed -----> VACHAN USER")

        #Get with VachanAdmin
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response1 = client.get(UNIT_URL+test_permissions_list[i]+'/books',headers=headers_auth)
                response2 = client.get(UNIT_URL+test_permissions_list[i]+'/versification',headers=headers_auth)
                response3 = client.get(UNIT_URL+test_permissions_list[i]+'/verses',headers=headers_auth)
                if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN:
                    assert response1.status_code == 200
                    assert response2.status_code == 200
                    assert response3.status_code == 200
                else:
                    assert response1.status_code == 403
                    assert response1.json()["error"] == "Permission Denied"
                    assert response2.status_code == 403
                    assert response2.json()["error"] == "Permission Denied"
                    assert response3.status_code == 403
                    assert response3.json()["error"] == "Permission Denied"
            else:
                response = client.get(UNIT_URL+test_permissions_list[i],headers=headers_auth)
                if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN:
                    assert response.status_code == 200
                else:
                    assert response.status_code == 403
                    assert response.json()["error"] == "Permission Denied"
        print(f"Test passed -----> VACHAN ADMIN")

        #Get with API User
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = client.get(UNIT_URL+test_permissions_list[i]+'/books',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/versification',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/verses',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
            else:
                response = client.get(UNIT_URL+test_permissions_list[i],headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
        print(f"Test passed -----> API USER")

        #Get with AgAdmin
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = client.get(UNIT_URL+test_permissions_list[i]+'/books',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/versification',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/verses',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
            else:
                response = client.get(UNIT_URL+test_permissions_list[i],headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
        print(f"Test passed -----> AG ADMIN")

        #Get with SanketMASTAdmin
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = client.get(UNIT_URL+test_permissions_list[i]+'/books',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/versification',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
                response = client.get(UNIT_URL+test_permissions_list[i]+'/verses',headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
            else:
                response = client.get(UNIT_URL+test_permissions_list[i],headers=headers_auth)
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
        print(f"Test passed -----> SanketMASTAdmin")

        #Get with SuperAdmin
        headers_auth['Authorization'] = SA_TOKEN
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response1 = client.get(UNIT_URL+test_permissions_list[i]+'/books',headers=headers_auth)
                response2 = client.get(UNIT_URL+test_permissions_list[i]+'/versification',headers=headers_auth)
                response3 = client.get(UNIT_URL+test_permissions_list[i]+'/verses',headers=headers_auth)
                if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN:
                    assert response1.status_code == 200
                    assert response2.status_code == 200
                    assert response3.status_code == 200
                else:
                    assert response1.status_code == 403
                    assert response1.json()["error"] == "Permission Denied"
                    assert response2.status_code == 403
                    assert response2.json()["error"] == "Permission Denied"
                    assert response3.status_code == 403
                    assert response3.json()["error"] == "Permission Denied"
            else:
                response = client.get(UNIT_URL+test_permissions_list[i],headers=headers_auth)
                if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN:
                    assert response.status_code == 200
                else:
                    assert response.status_code == 403
                    assert response.json()["error"] == "Permission Denied"
        print(f"Test passed -----> SUPER ADMIN")

        #Get with Bcs Dev
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response1 = client.get(UNIT_URL+test_permissions_list[i]+'/books',headers=headers_auth)
                response2 = client.get(UNIT_URL+test_permissions_list[i]+'/versification',headers=headers_auth)
                response3 = client.get(UNIT_URL+test_permissions_list[i]+'/verses',headers=headers_auth)
                if headers_auth['app'] == API:
                    assert response1.status_code == 200
                    assert response2.status_code == 200
                    assert response3.status_code == 200
                else:
                    assert response1.status_code == 403
                    assert response1.json()["error"] == "Permission Denied"
                    assert response2.status_code == 403
                    assert response2.json()["error"] == "Permission Denied"
                    assert response3.status_code == 403
                    assert response3.json()["error"] == "Permission Denied"
            else:
                response = client.get(UNIT_URL+test_permissions_list[i],headers=headers_auth)
                if headers_auth['app'] == API:
                    assert response.status_code == 200
                else:
                    assert response.status_code == 403
                    assert response.json()["error"] == "Permission Denied"
        print(f"Test passed -----> BCS DEVELOPER")

    #test for permissions -----------------------------------------------> open-access

    print('permision -------------------------> open access')
    headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
    #No login
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[1]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[1]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[1]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 401
                assert response1.json()["error"] == "Authentication Error"
                assert response2.status_code == 401
                assert response2.json()["error"] == "Authentication Error"
                assert response3.status_code == 401
                assert response3.json()["error"] == "Authentication Error"
        else:
            response = client.get(UNIT_URL+resourcename_list[1],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response.status_code == 200
            else:    
                assert response.status_code == 401
                assert response.json()["error"] == "Authentication Error"
    print(f"Test passed -----> NO LOGIN")

    #Get with AgUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[1]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[1]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[1]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[1],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> AG USER")

    #Get with SanketMASTUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[1]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[1]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[1]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[1],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> SanketMASTUser")

    #Get with VachanUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[1]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[1]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[1]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[1],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> VACHAN USER")

    #Get with VachanAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[1]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[1]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[1]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN\
                or headers_auth['app'] == VACHAN:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[1],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN\
                or headers_auth['app'] == VACHAN:
                assert response.status_code == 200
            else:
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> VACHAN ADMIN")

    #Get with API User
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[1]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[1]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[1]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[1],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> API USER")

    #Get with AgAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[1]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[1]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[1]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[1],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> AG ADMIN")

    #Get with SanketMASTAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[1]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[1]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[1]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[1],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> SanketMASTAdmin")

    #Get with SuperAdmin
    headers_auth['Authorization'] = SA_TOKEN
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[1]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[1]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[1]+'/verses',headers=headers_auth)
            assert response1.status_code == 200
            assert response2.status_code == 200
            assert response3.status_code == 200
        else:
            response = client.get(UNIT_URL+resourcename_list[1],headers=headers_auth)
            assert response.status_code == 200
    print(f"Test passed -----> SUPER ADMIN")

    #Get with Bcs Dev
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[1]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[1]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[1]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[1],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response.status_code == 200
            else:
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> BCS DEVELOPER")

    #test for permissions -----------------------------------------------> publishable

    print('permision -------------------------> publishable')
    headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
    #No login
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[2]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[2]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[2]+'/verses',headers=headers_auth)
            if headers_auth['app'] == VACHAN:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 401
                assert response1.json()["error"] == "Authentication Error"
                assert response2.status_code == 401
                assert response2.json()["error"] == "Authentication Error"
                assert response3.status_code == 401
                assert response3.json()["error"] == "Authentication Error"
        else:
            response = client.get(UNIT_URL+resourcename_list[2],headers=headers_auth)
            if headers_auth['app'] == VACHAN:
                assert response.status_code == 200
            else:    
                assert response.status_code == 401
                assert response.json()["error"] == "Authentication Error"
    print(f"Test passed -----> NO LOGIN")

    #Get with AgUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[2]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[2]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[2]+'/verses',headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[2],headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> AG USER")

    #Get with SanketMASTUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[2]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[2]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[2]+'/verses',headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[2],headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> SanketMASTUser")

    #Get with VachanUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[2]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[2]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[2]+'/verses',headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == API:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[2],headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == API:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> VACHAN USER")

    #Get with VachanAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[2]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[2]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[2]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN\
                or headers_auth['app'] == VACHAN:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[2],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN\
                or headers_auth['app'] == VACHAN:
                assert response.status_code == 200
            else:
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> VACHAN ADMIN")

    #Get with API User
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[2]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[2]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[2]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[2],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> API USER")

    #Get with AgAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[2]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[2]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[2]+'/verses',headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[2],headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> AG ADMIN")

    #Get with SanketMASTAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[2]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[2]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[2]+'/verses',headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[2],headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert response.status_code == 200
            else:    
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> SanketMASTAdmin")

    #Get with SuperAdmin
    headers_auth['Authorization'] = SA_TOKEN
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[2]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[2]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[2]+'/verses',headers=headers_auth)
            assert response1.status_code == 200
            assert response2.status_code == 200
            assert response3.status_code == 200
        else:
            response = client.get(UNIT_URL+resourcename_list[2],headers=headers_auth)
            assert response.status_code == 200
    print(f"Test passed -----> SUPER ADMIN")

    #Get with Bcs Dev
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = client.get(UNIT_URL+resourcename_list[2]+'/books',headers=headers_auth)
            response2 = client.get(UNIT_URL+resourcename_list[2]+'/versification',headers=headers_auth)
            response3 = client.get(UNIT_URL+resourcename_list[2]+'/verses',headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response1.status_code == 200
                assert response2.status_code == 200
                assert response3.status_code == 200
            else:
                assert response1.status_code == 403
                assert response1.json()["error"] == "Permission Denied"
                assert response2.status_code == 403
                assert response2.json()["error"] == "Permission Denied"
                assert response3.status_code == 403
                assert response3.json()["error"] == "Permission Denied"
        else:
            response = client.get(UNIT_URL+resourcename_list[2],headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert response.status_code == 200
            else:
                assert response.status_code == 403
                assert response.json()["error"] == "Permission Denied"
    print(f"Test passed -----> BCS DEVELOPER")

###############################################################################################################
def resourcetypeapi_get_accessrule_checks_app_userroles_gql(resourcetype, content_qry, content_data, test_data, bible = False):
    """checks for resource api access based on user roles and apps"""
    from .test_gql_resources import SOURCE_GLOBAL_QUERY
    from .conftest import initial_test_users
    from app.graphql_api import types
    from . test_gql_auth_basic import login,SUPER_PASSWORD,SUPER_USER

    headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
    #create 5 resources for contents with 5 different permisions
    language_list = ['en','ml','tn','ab','af']
    permission_list = [types.ResourcePermissions.CONTENT.name,
        types.ResourcePermissions.OPENACCESS.name,
        types.ResourcePermissions.PUBLISHABLE.name ,
        types.ResourcePermissions.DOWNLOADABLE.name,
        types.ResourcePermissions.DERIVABLE.name]
    permission_list_val = ["content","open-access","publishable","downloadable","derivable"]
    resourcename_list = []

    resource_data = {
  "object": {
    "resourceType": resourcetype,
    "language": "hi",
    "version": "TTT",
    "year": 2020,
    "accessPermissions": [],
  }
}

    #SuperAdmin login and token
    SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(SA_user_data)
    token =  response["data"]["login"]["token"]
    SA_TOKEN = "Bearer"+" "+token

    #create resource and corresponsing contents
    #resource can only created by VA or SA
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    for num in range(5):
        resource_data["object"]["language"] = language_list[num]
        resource_data["object"]["accessPermissions"] = [permission_list[num]]
        response = executed = gql_request(queryRESOURCE_GLOBAL_QUERY,operation="mutation",
            variables=resource_data, headers=headers_auth)
        assert isinstance(executed, Dict)
        assert executed["data"]["addResource"]["message"] == "Resource created successfully"
        resource_name = response["data"]["addResource"]["data"]["resourceName"]
        resp_data = response['data']["addResource"]["data"]['metaData']
        assert permission_list_val[num]  in resp_data['accessPermissions']
        resourcename_list.append(resource_name)
        # print("exec------>",resource_name)

        content_data["object"]["resourceName"] = resource_name
        executed = gql_request(query=content_qry,operation="mutation", variables=content_data,
            headers=headers_auth)
        assert not "errors" in executed

    API = types.App.API.value
    AG = types.App.AG.value
    SMAST = types.App.SMAST.value
    VACHAN = types.App.VACHAN.value
    VACHANADMIN = types.App.VACHANADMIN.value
    Apps = [ API,AG,VACHAN,VACHANADMIN,SMAST]

    #Get without Login headers=headers_auth
    #permision -------------------------> content , downloadable , derivable
    print("resource respectivily for -------------------------> \
        content(en) , downloadable(ab) , derivable(af)")
    test_permissions_list  = ["en_TTT_1_" + contenttype , "ab_TTT_1_" + contenttype ,
                                "af_TTT_1_" + contenttype]
    for i in range(len(test_permissions_list)):
        headers_auth = {"contentType": "application/json",
                "accept": "application/json"}  
        print(f"permisioln resource-------------------------> {test_permissions_list[i]}")
        
        for num in range(4):
            headers_auth['app'] = Apps[num]
            test_data["get_var"]["resource"] = test_permissions_list[i]
            if bible:
                response = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
            else:
                response = gql_request(query=test_data["get_query"],variables=test_data["get_var"],headers=headers_auth)
                assert "errors" in response
        print(f"Test passed -----> NO LOGIN")

        #Get with AgUser
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
            else:
                response = gql_request(query=test_data["get_query"],variables=test_data["get_var"],headers=headers_auth)
                assert "errors" in response
        print(f"Test passed -----> AG USER")

        #Get with SanketMASTUser
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
            else:
                response = gql_request(query=test_data["get_query"],variables=test_data["get_var"],headers=headers_auth)
                assert "errors" in response
        print(f"Test passed -----> SanketMASTUser")

        #Get with VachanUser
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
            else:
                response = gql_request(query=test_data["get_query"],variables=test_data["get_var"],headers=headers_auth)
                assert "errors" in response
        print(f"Test passed -----> VACHAN USER")

        #Get with VachanAdmin
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            test_data["get_var"]["resource"] = test_permissions_list[i]
            if bible:
                response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN:
                    assert not  "errors" in response1
                    assert not "errors" in response2
                    assert not "errors" in response3
                else:
                    assert "errors" in response1
                    assert "errors" in response2
                    assert "errors" in response3
            else:
                response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
                if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN:
                    assert not "errors" in response
                    assert len(response["data"]) > 0
                else:
                    assert "errors" in response
        print(f"Test passed -----> VACHAN ADMIN")

        #Get with API User
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                pass
            else:
                response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response    
        print(f"Test passed -----> API USER")

        #Get with AgAdmin
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                pass
            else:
                response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
        print(f"Test passed -----> AG ADMIN")

        #Get with SanketMASTAdmin
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                response = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
                pass
            else:
                response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
                assert "errors" in response
        print(f"Test passed -----> SanketMASTAdmin")

        #Get with SuperAdmin
        headers_auth['Authorization'] = SA_TOKEN
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN:
                    assert not  "errors" in response1
                    assert not "errors" in response2
                    assert not "errors" in response3
                else:
                    assert "errors" in response1
                    assert "errors" in response2
                    assert "errors" in response3
            else:
                response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
                if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN:
                    assert not "errors" in response
                    assert len(response["data"]) > 0
                else:
                    assert "errors" in response

        print(f"Test passed -----> SUPER ADMIN")

        #Get with Bcs Dev
        headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
        for num in range(4):
            headers_auth['app'] = Apps[num]
            if bible:
                response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
                if headers_auth['app'] == API:
                    assert not  "errors" in response1
                    assert not "errors" in response2
                    assert not "errors" in response3
                else:
                    assert "errors" in response1
                    assert "errors" in response2
                    assert "errors" in response3
            else:
                response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
                if headers_auth['app'] == API:
                    assert not "errors" in response
                    assert len(response["data"]) > 0
                else:
                    assert "errors" in response
                                    
        print(f"Test passed -----> BCS DEVELOPER")

    # #test for permissions -----------------------------------------------> open-access

    print('permision -------------------------> open access')
    headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
    test_data["get_var"]["resource"] = resourcename_list[1]
    #No login
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response
    print(f"Test passed -----> NO LOGIN")

    #Get with AgUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response      
    print(f"Test passed -----> AG USER")

    #Get with SanketMASTUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response      
    print(f"Test passed -----> SanketMASTUser")

    #Get with VachanUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response          
    print(f"Test passed -----> VACHAN USER")

    #Get with VachanAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN\
                or headers_auth['app'] == VACHAN:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN\
                or headers_auth['app'] == VACHAN:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response          
    print(f"Test passed -----> VACHAN ADMIN")

    #Get with API User
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response              
    print(f"Test passed -----> API USER")

    #Get with AgAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response              
    print(f"Test passed -----> AG ADMIN")

    #Get with SanketMASTAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN\
                or headers_auth['app'] == AG:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response              
    print(f"Test passed -----> SanketMASTAdmin")

    #Get with SuperAdmin
    headers_auth['Authorization'] = SA_TOKEN
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            assert not  "errors" in response1
            assert not "errors" in response2
            assert not "errors" in response3        
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            assert not "errors" in response
    print(f"Test passed -----> SUPER ADMIN")

    #Get with Bcs Dev
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response      
    print(f"Test passed -----> BCS DEVELOPER")

    # #test for permissions -----------------------------------------------> publishable

    print('permision -------------------------> publishable')
    headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
    test_data["get_var"]["resource"] = resourcename_list[2]
    #No login
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response          
    print(f"Test passed -----> NO LOGIN")

    #Get with AgUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response              
    print(f"Test passed -----> AG USER")

    #Get with SanketMASTUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response              
    print(f"Test passed -----> SanketMASTUser")

    #Get with VachanUser
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == API:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == API:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response        
    print(f"Test passed -----> VACHAN USER")

    #Get with VachanAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN\
                or headers_auth['app'] == VACHAN:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHANADMIN\
                or headers_auth['app'] == VACHAN:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response     
    print(f"Test passed -----> VACHAN ADMIN")

    #Get with API User
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response         
    print(f"Test passed -----> API USER")

    #Get with AgAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response     
    print(f"Test passed -----> AG ADMIN")

    #Get with SanketMASTAdmin
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['SanketMASTAdmin']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == VACHAN or headers_auth['app'] == AG\
                or headers_auth['app'] == API:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response     
    print(f"Test passed -----> SanketMASTAdmin")

    #Get with SuperAdmin
    headers_auth['Authorization'] = SA_TOKEN
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            assert not  "errors" in response1
            assert not "errors" in response2
            assert not "errors" in response3
        else:    
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            assert not "errors" in response
    print(f"Test passed -----> SUPER ADMIN")

    #Get with Bcs Dev
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
    for num in range(4):
        headers_auth['app'] = Apps[num]
        if bible:
            response1 = gql_request(query=test_data["books"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response2 = gql_request(query=test_data["versification"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            response3 = gql_request(query=test_data["verses"]["get_query"],variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not  "errors" in response1
                assert not "errors" in response2
                assert not "errors" in response3
            else:
                assert "errors" in response1
                assert "errors" in response2
                assert "errors" in response3
        else:
            response = gql_request(query= test_data["get_query"], variables=test_data["get_var"],
                    headers=headers_auth)
            if headers_auth['app'] == API or headers_auth['app'] == VACHAN:
                assert not "errors" in response
                assert len(response["data"]) > 0
            else:
                assert "errors" in response         
    print(f"Test passed -----> BCS DEVELOPER")