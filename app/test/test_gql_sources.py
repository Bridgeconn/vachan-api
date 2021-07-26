"""Test cases for Sources in GQL"""
from typing import Dict
#pylint: disable=E0401
from .test_sources import assert_positive_get
from .test_gql_versions import GLOBAL_QUERY as version_query
from .test_gql_versions import check_post as version_add
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import check_skip_limit_gql, gql_request,assert_not_available_content_gql

SOURCE_GLOBAL_VARIABLES = {
  "object": {
    "contentType": "commentary",
    "language": "hi",
    "version": "TTT",
    "revision": "1",
    "year": 2021,
    "license": "CC-BY-SA",
    "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
  }
}

SOURCE_GLOBAL_QUERY = """
    mutation createsource($object:InputAddSource){
    addSource(sourceArg:$object){
        message
        data{
        sourceName
        contentType{
            contentId
            contentType
        }
        language{
            languageId
            language
            code
            scriptDirection
            metaData
        }
        version{
            versionId
            versionAbbreviation
            versionName
            revision
            metaData
        }
        year
        license{
            name
            code
            license
            permissions
            active
        }
        metaData
        active
        }
    }
    }
    """

def check_post(query,variables):
    """positive post test"""
    executed = gql_request(query=query,operation="mutation", variables=variables)
    assert isinstance(executed, Dict)
    assert executed["data"]["addSource"]["message"] == "Source created successfully"
    item =executed["data"]["addSource"]["data"]
    assert_positive_get(item)
    return executed

def test_post_default():
    '''Positive test to add a new source'''
    version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version"
    }
    }
    #Create a version
    version_add(version_query,version_variable)
    #create source
    check_post(SOURCE_GLOBAL_QUERY,SOURCE_GLOBAL_VARIABLES)

    query_check = """
      {
  contents(arg_text){
    sourceName
  }
}
    """
    check_skip_limit_gql(query_check,"contents")

def test_post_wrong_version():
    '''Negative test with not available version or revision'''
    version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version"
    }
    }
    #Create a version
    version_add(version_query,version_variable)

    #wrong version
    variables1 = {
    "object": {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTD",
        "revision": "1",
        "year": 2021,
        "license": "ISC",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed1 = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables1)
    assert isinstance(executed1, Dict)
    assert "errors" in executed1.keys()

    #wrong revision
    variables2 = {
    "object": {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "revision": "2",
        "year": 2021,
        "license": "ISC",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed2 = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables2)
    assert isinstance(executed2, Dict)
    assert "errors" in executed2.keys()

    #working post
    check_post(SOURCE_GLOBAL_QUERY,SOURCE_GLOBAL_VARIABLES)

def test_post_wrong_lang():
    '''Negative test with not available language'''
    version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version"
    }
    }
    #Create a version
    version_add(version_query,version_variable)

    variables = {
    "object": {
        "contentType": "commentary",
        "language": "aaj",
        "version": "TTT",
        "revision": "1",
        "year": 2021,
        "license": "ISC",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables)
    assert isinstance(executed, Dict)
    assert "errors" in executed.keys()

def test_post_wrong_content():
    '''Negative test with not available content type'''
    version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version"
    }
    }
    #Create a version
    version_add(version_query,version_variable)
    variables = {
    "object": {
        "contentType": "bibl",
        "language": "hi",
        "version": "TTT",
        "revision": "1",
        "year": 2021,
        "license": "ISC",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables)
    assert isinstance(executed, Dict)
    assert "errors" in executed.keys()

    # '''Negative test with not a valid license from license table'''
    variables2 = {
    "object": {
        "contentType": "infographic",
        "language": "hi",
        "version": "TTT",
        "revision": "1",
        "year": 2021,
        "license": "XYZ-123",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables2)
    assert isinstance(executed, Dict)
    assert "errors" in executed.keys()

def test_post_wrong_year():
    '''Negative test with text in year field'''
    variables = {
    "object": {
        "contentType": "bible",
        "language": "hi",
        "version": "TTT",
        "revision": "1",
        "year": "twenty twenty",
        "license": "ISC",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables)
    assert isinstance(executed, Dict)
    assert "errors" in executed.keys()

def test_post_wrong_metadata():
    '''Negative test with incorrect format for metadata'''
    variables = {
    "object": {
        "contentType": "bible",
        "language": "hi",
        "version": "TTT",
        "revision": "1",
        "year": 2021,
        "license": "ISC",
        "metaData": "{\"owner\"=\"someone\",\"access-key\"=\"123xyz\"}"
    }
    }
    executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables)
    assert isinstance(executed, Dict)
    assert "errors" in executed.keys()

def test_post_missing_mandatory_info():
    '''Negative tests with mandatory contents missing'''
    # no contentType
    variables = {
    "object": {
        "language": "hi",
        "version": "TTT",
        "revision": "1",
        "year": 2021,
        "license": "ISC",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables)
    assert isinstance(executed, Dict)
    assert "errors" in executed.keys()

    # no language
    variables2 = {
    "object": {
        "contentType": "bible",
        "version": "TTT",
        "revision": "1",
        "year": 2021,
        "license": "ISC",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed2 = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables2)
    assert isinstance(executed2, Dict)
    assert "errors" in executed2.keys()

    # no version
    variables3 = {
    "object": {
        "contentType": "bible",
        "language": "hi",
        "revision": "1",
        "year": 2021,
        "license": "ISC",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed3 = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables3)
    assert isinstance(executed3, Dict)
    assert "errors" in executed3.keys()

    #no year
    variables4 = {
    "object": {
        "contentType": "bible",
        "language": "hi",
        "version": "TTT",
        "revision": "1",
        "license": "ISC",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed4 = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables4)
    assert isinstance(executed4, Dict)
    assert "errors" in executed4.keys()

def test_post_missing_some_info():
    '''Positive test with non mandatory contents missing.
    If revision not specified, 1 is assumed. Other fields are nullable or have default value'''
    version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version"
    }
    }
    #Create a version
    version_add(version_query,version_variable)
    #create source
    variables = {
    "object": {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "year": 2021
    }
    }
    check_post(SOURCE_GLOBAL_QUERY,variables)

def test_post_duplicate():
    '''Add the same source twice'''
    version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version"
    }
    }
    #Create a version
    version_add(version_query,version_variable)
    variables = {
    "object": {
        "contentType": "commentary",
        "language": "hi",
        "version": "TTT",
        "year": 2021
    }
    }
    check_post(SOURCE_GLOBAL_QUERY,variables)
    executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables)
    assert isinstance(executed, Dict)
    assert "errors" in executed.keys()

SOURCE_GET = """
    {
  contents{
    sourceName
    contentType{
      contentId
      contentType
    }
    language{
      languageId
      language
      code
      scriptDirection
      metaData
    }
    version{
      versionId
      versionAbbreviation
      versionName
      revision
      metaData
    }
    year
    license{
      name
      code
      license
      permissions
      active
    }
    metaData
    active
  }
}
"""

def test_get_empty():
    '''Test get before adding data to table. Usually done on freshly set up test DB.
    If the testing is done on a DB that already has some data, the response wont be empty.'''
    executed = gql_request(query=SOURCE_GET)
    assert isinstance(executed, Dict)
    if len(executed["data"]["contents"]) == 0:
        assert_not_available_content_gql(executed["data"]["contents"])


def test_get_wrong_values():
    '''Checks input validation for query params'''
    get_query = """
            {
    contents(versionAbbreviation:1){
        sourceName
        contentType{
        contentId
        contentType
        }
    }
    }
    """
    executed = gql_request(query=get_query)
    assert isinstance(executed, Dict)
    assert "errors" in executed.keys()

    get_query2 = """
            {
    contents(revision:X){
        sourceName
        contentType{
        contentId
        contentType
        }
    }
    }
    """
    executed2 = gql_request(query=get_query2)
    assert isinstance(executed2, Dict)
    assert "errors" in executed2.keys()

    get_query3 = """
        {
  contents(languageCode:"hin6i"){
    sourceName
    contentType{
      contentId
      contentType
    }
  }
}
    """
    executed3 = gql_request(query=get_query3)
    assert isinstance(executed3, Dict)
    assert_not_available_content_gql(executed3["data"]["contents"])

def test_get_after_adding_data():
    '''Add some sources to DB and test fecthing those data'''
    version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version"
    }
    }
    #Create a version
    version_add(version_query,version_variable)
    variables = {
    "object": {
        "contentType": "infographic",
        "version": "TTT",
        "year": 2021,
    }
    }
    for lang in ['hi', 'mr', 'te']:
        variables["object"]['language'] = lang
        check_post(SOURCE_GLOBAL_QUERY,variables)

    version_variable["object"]['revision'] = 2
    version_add(version_query,version_variable)
    variables["object"]['revision'] = '2'
    for lang in ['hi', 'mr', 'te']:
        variables["object"]['language'] = lang
        check_post(SOURCE_GLOBAL_QUERY,variables)

    variables["object"]['contentType'] = 'commentary'
    variables["object"]['revision'] = 1
    variables["object"]['metaData'] = "{\"owner\":\"myself\"}"
    variables["object"]['license'] = "ISC"
    for lang in ['hi', 'mr', 'te']:
        variables["object"]['language'] = lang
        check_post(SOURCE_GLOBAL_QUERY,variables)

    executed = gql_request(query=SOURCE_GET)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["contents"]) > 0
    items = executed["data"]["contents"]
    for item in items:
        assert_positive_get(item)

    # filter with contentType
    query1= """
        {
  contents(contentType:"commentary",latestRevision:false){
    sourceName
    contentType{
      contentId
      contentType
    }
    language{
      languageId
      language
      code
      scriptDirection
      metaData
    }
    version{
      versionId
      versionAbbreviation
      versionName
      revision
      metaData
    }
    year
    license{
      name
      code
      license
      permissions
      active
    }
    metaData
    active
  }
}
    """
    executed1 = gql_request(query=query1)
    assert isinstance(executed1, Dict)
    assert len(executed1["data"]["contents"]) >= 3
    items = executed1["data"]["contents"]
    for item in items:
        assert_positive_get(item)

    # filter with language
    query2 = """
        {
  contents(languageCode:"hi",latestRevision:false){
    sourceName
    contentType{
      contentId
      contentType
    }
    language{
      languageId
      language
      code
      scriptDirection
      metaData
    }
    version{
      versionId
      versionAbbreviation
      versionName
      revision
      metaData
    }
    year
    license{
      name
      code
      license
      permissions
      active
    }
    metaData
    active
  }
}
    """
    executed2 = gql_request(query=query2)
    assert isinstance(executed2, Dict)
    assert len(executed2["data"]["contents"]) >= 3
    items = executed2["data"]["contents"]
    for item in items:
        assert_positive_get(item)

    # filter with revision
    query3 = """
        {
  contents(revision:2){
    sourceName
    contentType{
      contentId
      contentType
    }
    language{
      languageId
      language
      code
      scriptDirection
      metaData
    }
    version{
      versionId
      versionAbbreviation
      versionName
      revision
      metaData
    }
    year
    license{
      name
      code
      license
      permissions
      active
    }
    metaData
    active
  }
}
    """
    executed3 = gql_request(query=query3)
    assert isinstance(executed3, Dict)
    assert len(executed3["data"]["contents"]) >= 3
    items = executed3["data"]["contents"]
    for item in items:
        assert_positive_get(item)

    # filter with version
    query4 = """
        {
  contents(versionAbbreviation:"TTT",latestRevision:false){
    sourceName
    contentType{
      contentId
      contentType
    }
    language{
      languageId
      language
      code
      scriptDirection
      metaData
    }
    version{
      versionId
      versionAbbreviation
      versionName
      revision
      metaData
    }
    year
    license{
      name
      code
      license
      permissions
      active
    }
    metaData
    active
  }
}
    """
    executed4 = gql_request(query=query4)
    assert isinstance(executed4, Dict)
    assert len(executed4["data"]["contents"]) >= 9
    items = executed4["data"]["contents"]
    for item in items:
        assert_positive_get(item)

    # filter with license
    query5 = """
        {
  contents(licenseCode:"CC-BY-SA"){
    sourceName
    contentType{
      contentId
      contentType
    }
    language{
      languageId
      language
      code
      scriptDirection
      metaData
    }
    version{
      versionId
      versionAbbreviation
      versionName
      revision
      metaData
    }
    year
    license{
      name
      code
      license
      permissions
      active
    }
    metaData
    active
  }
}
    """
    executed5 = gql_request(query=query5)
    assert isinstance(executed5, Dict)
    assert len(executed5["data"]["contents"]) >= 3
    items = executed5["data"]["contents"]
    for item in items:
        assert_positive_get(item)

    # filter with license ISC
    query6 = """
        {
  contents(licenseCode:"ISC"){
    sourceName
    contentType{
      contentId
      contentType
    }
    language{
      languageId
      language
      code
      scriptDirection
      metaData
    }
    version{
      versionId
      versionAbbreviation
      versionName
      revision
      metaData
    }
    year
    license{
      name
      code
      license
      permissions
      active
    }
    metaData
    active
  }
}
    """
    executed6 = gql_request(query=query6)
    assert isinstance(executed6, Dict)
    assert len(executed6["data"]["contents"]) >= 3
    items = executed6["data"]["contents"]
    for item in items:
        assert_positive_get(item)

# filter with version and revision
    query7 = """
    {
  contents(versionAbbreviation:"TTT",revision:1){
    sourceName
    contentType{
      contentId
      contentType
    }
    language{
      languageId
      language
      code
      scriptDirection
      metaData
    }
    version{
      versionId
      versionAbbreviation
      versionName
      revision
      metaData
    }
    year
    license{
      name
      code
      license
      permissions
      active
    }
    metaData
    active
  }
}
"""
    executed7 = gql_request(query=query7)
    assert isinstance(executed7, Dict)
    assert len(executed7["data"]["contents"]) >= 3
    items = executed7["data"]["contents"]
    for item in items:
        assert_positive_get(item)
    

def test_put_default():
    '''Add some data and test updating them'''
    version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version"
    }
    }
    #Create a version
    version_add(version_query,version_variable)
    version_variable["object"]['revision'] = 2
    version_add(version_query,version_variable)
    variables = {
    "object": {
        "contentType": "commentary",
        "version": "TTT",
        'language': 'ml',
        "year": 2021,
    }
    }
    check_post(SOURCE_GLOBAL_QUERY,variables)

    #data update
    up_query="""
        mutation editsource($object:InputEditSource){
  editSource(sourceArg:$object){
    message
    data{
      sourceName
      contentType{
        contentId
        contentType
      }
      language{
        languageId
        language
        code
        scriptDirection
        metaData
      }
      version{
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
      }
      year
      license{
        name
        code
        license
        permissions
        active
      }
      metaData
      active
    }
  }
}
    """
    up_variables={
  "object": {
    "sourceName": "ml_TTT_1_commentary",
    "revision": 2
  }
}
    executed = gql_request(query=up_query,operation="mutation", variables=up_variables)
    assert isinstance(executed, Dict)
    assert executed["data"]["editSource"]["message"] == "Source edited successfully"
    item =executed["data"]["editSource"]["data"]
    assert_positive_get(item)
    assert item["version"]["revision"] == 2
    assert item['sourceName'] == "ml_TTT_2_commentary"

    up_variables2={
  "object": {
    "sourceName": "ml_TTT_2_commentary",
    "metaData": "{\"owner\":\"new owner\"}"
  }
}
    executed2 = gql_request(query=up_query,operation="mutation", variables=up_variables2)
    assert isinstance(executed2, Dict)
    assert executed2["data"]["editSource"]["message"] == "Source edited successfully"
    item =executed2["data"]["editSource"]["data"]
    assert_positive_get(item)
    assert item['metaData']['owner'] == "new owner"

def test_soft_delete():
    '''Soft delete is achived by updating the active flag to Fasle'''
    version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version"
    }
    }
    #Create a version
    version_add(version_query,version_variable)
    variables = {
    "object": {
        "contentType": "commentary",
        "version": "TTT",
        'language': 'ml',
        "year": 2021,
    }
    }
    executed = check_post(SOURCE_GLOBAL_QUERY,variables)
    assert executed["data"]["addSource"]["data"]["active"]

       #data update
    up_query="""
        mutation editsource($object:InputEditSource){
  editSource(sourceArg:$object){
    message
    data{
      sourceName
      contentType{
        contentId
        contentType
      }
      language{
        languageId
        language
        code
        scriptDirection
        metaData
      }
      version{
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
      }
      year
      license{
        name
        code
        license
        permissions
        active
      }
      metaData
      active
    }
  }
}
    """
    up_variables={
  "object": {
    'sourceName': 'ml_TTT_1_commentary',
    "active": False
  }
}
    executed2 = gql_request(query=up_query,operation="mutation", variables=up_variables)
    assert isinstance(executed2, Dict)
    assert executed2["data"]["editSource"]["message"] == "Source edited successfully"
    item =executed2["data"]["editSource"]["data"]
    assert_positive_get(item)
    assert not item['active']

    query1 = """
        {
  contents(active:false){
    sourceName
    contentType{
      contentId
      contentType
    }
    language{
      languageId
      language
      code
      scriptDirection
      metaData
    }
    version{
      versionId
      versionAbbreviation
      versionName
      revision
      metaData
    }
    year
    license{
      name
      code
      license
      permissions
      active
    }
    metaData
    active
  }
}
    """
    executed = gql_request(query=query1)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["contents"]) > 0
    items = executed["data"]["contents"]
    for item in items:
        assert_positive_get(item)
        assert not item["active"]
#pylint: disable=C0302
    assert 'ml_TTT_1_commentary' in [item['sourceName'] for item in items]
