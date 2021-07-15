"""Test cases for Versions GQL"""
from typing import Dict

#pylint: disable=E0401
from .test_versions import assert_positive_get
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import gql_request,assert_not_available_content_gql

GLOBAL_VARIABLES = {
    "object": {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "revision": 1,
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }

GLOBAL_QUERY = """
    mutation createversion($object:InputAddVersion){
    addVersion(versionArg:$object){
        message
        data{
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
        }
    }
    }
    """

def check_post(query, variables):
    """common for check post"""
    executed = gql_request(query=query,operation="mutation", variables=variables)
    assert isinstance(executed, Dict)
    assert executed["data"]["addVersion"]["message"] == "Version created successfully"
    item =executed["data"]["addVersion"]["data"]
    item["versionId"] = int(item["versionId"])
    assert_positive_get(item)
    assert item["versionAbbreviation"] == variables["object"]["versionAbbreviation"]
    return executed

def assert_error_check(query, variables):
    """common error check"""
    executed = gql_request(query=query,operation="mutation", variables=variables)
    assert "errors" in executed.keys()

def test_post_default():
    '''Positive test to add a new version'''
    check_post(GLOBAL_QUERY,GLOBAL_VARIABLES)

def test_post_multiple_with_same_abbr():
    '''Positive test to add two version, with same abbr and diff revision'''
    variables = GLOBAL_VARIABLES
    variables["object"]["revision"] = 2
    check_post(GLOBAL_QUERY,variables)

def test_post_multiple_with_same_abbr_negative():
    '''Negative test to add two version, with same abbr and revision'''
    check_post(GLOBAL_QUERY,GLOBAL_VARIABLES)
    executed2 =  gql_request(query=GLOBAL_QUERY,operation="mutation", variables=GLOBAL_VARIABLES)
    assert isinstance(executed2, Dict)
    assert "errors" in executed2.keys()

def test_post_without_revision():
    '''revision field should have a default value, even not provided'''
    variables = {
    "object": {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }
    executed = check_post(GLOBAL_QUERY,variables)
    assert executed["data"]["addVersion"]["data"]["revision"] == 1

def test_post_without_metadata():
    '''metadata field is not mandatory'''
    variables = {
    "object": {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "revision": 1
    }
    }
    executed = check_post(GLOBAL_QUERY,variables)
    assert executed["data"]["addVersion"]["data"]["metaData"] is None

def test_post_without_abbr():
    '''versionAbbreviation is mandatory'''
    variables = {
    "object": {
        "versionName": "Xyz version to test",
        "revision": 1
    }
    }
    assert_error_check(GLOBAL_QUERY,variables)

def test_post_wrong_abbr():
    '''versionAbbreviation cannot have space, dot etc'''
    variables = {
    "object": {
        "versionAbbreviation": "XY Z",
        "versionName": "Xyz version to test",
        "revision": 1
    }
    }
    assert_error_check(GLOBAL_QUERY,variables)

    variables2 = {
    "object": {
        "versionAbbreviation": "XY.Z",
        "versionName": "Xyz version to test",
        "revision": 1
    }
    }
    assert_error_check(GLOBAL_QUERY,variables2)

def test_post_wrong_revision():
    '''revision cannot have space, dot letters etc'''
    variables = {
    "object": {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "revision": 1
    }
    }

    variables["object"]["revision"] = "1 2"
    assert_error_check(GLOBAL_QUERY,variables)

    variables["object"]["revision"] = "1a"
    assert_error_check(GLOBAL_QUERY,variables)

    variables["object"]["revision"] = "1 2"
    assert_error_check(GLOBAL_QUERY,variables)

def test_post_without_name():
    '''versionName is mandatory'''
    variables = {
    "object": {
        "versionAbbreviation": "XYZ",
        "revision": 1
    }
    }
    assert_error_check(GLOBAL_QUERY,variables)

QUERY_GET = """
    {
    versions{
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
    }
    }
"""

def test_get():
    '''Test get before adding data to table. Usually run on new test DB on local or github.
    If the testing is done on a DB that already has data(staging), the response wont be empty.'''
    executed =  gql_request(query=QUERY_GET)
    if len(executed["data"]["versions"]) == 0:
        assert_not_available_content_gql(executed["data"]["versions"])

def test_get_wrong_abbr():
    '''abbreviation with space, number'''
    query = """
        {
    versions(versionAbbreviation:"A A"){
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
    }
    }
    """
    executed =  gql_request(query=query)
    assert_not_available_content_gql(executed["data"]["versions"])

    query2 = """
        {
    versions(versionAbbreviation:123){
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
    }
    }
    """
    executed =  gql_request(query=query2)
    assert "errors" in executed.keys()

def test_get_wrong_revision():
    '''revision as text'''
    query = """
        {
    versions(revision:"red"){
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
    }
    }
    """
    executed =  gql_request(query=query)
    assert "errors" in executed.keys()

def test_get_after_adding_data():
    '''Add some data to versions table and test get method'''
    variables = {
    "object": {
       'versionAbbreviation': "AAA",
        'versionName': 'test name A',
        'revision': 1
    }
    }
    check_post(GLOBAL_QUERY,variables)
    variables["object"]["revision"] = 2
    check_post(GLOBAL_QUERY,variables)

    variables2 = {
    "object": {
        'versionAbbreviation': "BBB",
        'versionName': 'test name B',
        'revision': 1
    }
    }
    check_post(GLOBAL_QUERY,variables2)
    variables2["object"]["revision"] = 2
    check_post(GLOBAL_QUERY,variables2)

    executed_get = gql_request(QUERY_GET)
    assert isinstance(executed_get, Dict)
    assert len(executed_get["data"]["versions"]) == 4
    items =executed_get["data"]["versions"]
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)

    #get test after successfull creation
    # filter with abbr
    query1 = """
            {
    versions(versionAbbreviation:"AAA"){
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
    }
    }
    """
    executed1 = gql_request(query1)
    assert isinstance(executed1, Dict)
    items =executed1["data"]["versions"]
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)
        assert item["versionAbbreviation"] == "AAA"

    # filter with abbr, for not available content
    query2 = """
            {
    versions(versionAbbreviation:"SSS"){
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
    }
    }
    """
    executed2 = gql_request(query2)
    assert_not_available_content_gql(executed2["data"]["versions"])

    # filter with name
    query3 = """
            {
    versions(versionName:"test name B"){
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
    }
    }
    """
    executed3 = gql_request(query3)
    assert isinstance(executed3, Dict)
    assert len(executed3["data"]["versions"]) == 2
    items =executed3["data"]["versions"]
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)
        assert item["versionName"] == "test name B"

    # filter with abbr and revision
    query4 = """
            {
    versions(versionAbbreviation:"AAA",revision:2){
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
    }
    }
    """
    executed4 = gql_request(query4)
    assert isinstance(executed4, Dict)
    items =executed4["data"]["versions"]
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)
        assert item["versionAbbreviation"] == "AAA"
        assert item["revision"] ==  2

    variables3 = {
    "object": {
       'versionAbbreviation': "CCC",
        'versionName': 'test name C',
        'metaData': "{\"owner\":\"myself\"}"
    }
    }
    check_post(GLOBAL_QUERY,variables3)

    # check for metaData and default value for metadata
    query5 = """
            {
    versions(versionAbbreviation:"CCC"){
        versionId
        versionAbbreviation
        versionName
        revision
        metaData
    }
    }
    """
    executed5 = gql_request(query5)
    assert isinstance(executed5, Dict)
    assert len(executed5["data"]["versions"]) == 1
    items =executed5["data"]["versions"]
    for item in items:
        if 'versionId' in item:
            item["versionId"] = int(item["versionId"])
            assert_positive_get(item)
        assert item["versionAbbreviation"] == "CCC"
        assert item["revision"] == 1
        assert item['metaData']['owner'] == "myself"
