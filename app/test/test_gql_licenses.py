"""Test cases for licenses in GQL"""
from typing import Dict
#pylint: disable=E0401
from .test_licenses import assert_positive_get
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import gql_request,assert_not_available_content_gql

def test_get():
    '''positive test case, without optional params'''
    query = """
        {
    licenses{
        name
        code
        license
        permissions
        active
    }
    }
    """
    executed = gql_request(query)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["licenses"])>0
    assert isinstance(executed["data"]["licenses"], list)
    for item in executed["data"]["licenses"]:
        assert_positive_get(item)

    # '''positive test case, with one optional params, code'''
    query2 = """
        {
    licenses(licenseCode:"ISC"){
        name
        code
        license
        permissions
        active
    }
    }
    """
    executed2 = gql_request(query2)
    assert isinstance(executed2, Dict)
    assert len(executed2["data"]["licenses"]) == 1
    assert isinstance(executed2["data"]["licenses"], list)
    for item in executed2["data"]["licenses"]:
        assert_positive_get(item)
    assert executed2["data"]["licenses"][0]["code"] == "ISC"

    # '''positive test case, with one optional params, code in lower case'''
    query3 = """
        {
    licenses(licenseCode:"isc"){
        name
        code
        license
        permissions
        active
    }
    }
    """
    executed3 = gql_request(query3)
    assert isinstance(executed3, Dict)
    assert len(executed3["data"]["licenses"]) == 1
    assert isinstance(executed3["data"]["licenses"], list)
    for item in executed3["data"]["licenses"]:
        assert_positive_get(item)
    assert executed3["data"]["licenses"][0]["code"] == "ISC"

    # '''positive test case, with one optional params, name'''
    query4 = """
        {
    licenses(licenseName:"Creative Commons License"){
        name
        code
        license
        permissions
        active
    }
    }
    """
    executed4 = gql_request(query4)
    assert isinstance(executed4, Dict)
    assert len(executed4["data"]["licenses"]) == 1
    assert isinstance(executed4["data"]["licenses"], list)
    for item in executed4["data"]["licenses"]:
        assert_positive_get(item)
    assert executed4["data"]["licenses"][0]["code"] == "CC-BY-SA"

    # '''positive test case, with two optional params'''
    query5 = """
        {
    licenses(licenseCode:"ISC",active:true){
        name
        code
        license
        permissions
        active
    }
    }
    """
    executed5 = gql_request(query5)
    assert isinstance(executed5, Dict)
    assert len(executed5["data"]["licenses"]) == 1
    assert isinstance(executed5["data"]["licenses"], list)
    for item in executed5["data"]["licenses"]:
        assert_positive_get(item)
    assert executed5["data"]["licenses"][0]["code"] == "ISC"
    assert executed5["data"]["licenses"][0]["active"]

    # ''' request a not available license, with code''
    query6 = """
        {
    licenses(licenseCode:"kfc"){
        name
        code
        license
        permissions
        active
    }
    }
    """
    executed6 = gql_request(query6)
    assert isinstance(executed6, Dict)
    item = executed6["data"]["licenses"]
    assert_not_available_content_gql(item)

    # '''filter with permissions'''
    query7 = """
        {
    licenses(permission:commercial){
        name
        code
        license
        permissions
        active
    }
    }
    """
    executed7 = gql_request(query7)
    assert isinstance(executed7, Dict)
    assert len(executed7["data"]["licenses"]) > 0

    # ''' request a not available license, with license name'''
    query8 = """
        {
    licenses(licenseName:"not-a-license"){
        name
        code
        license
        permissions
        active
    }
    }
    """
    executed8 = gql_request(query8)
    assert isinstance(executed8, Dict)
    item = executed8["data"]["licenses"]
    assert_not_available_content_gql(item)

    # '''license code should not have spaces'''
    query9 = """
        {
    licenses(licenseCode:"ISC 0II"){
        name
        code
        license
        permissions
        active
    }
    }
    """
    executed9 = gql_request(query9)
    assert isinstance(executed9, Dict)
    item = executed9["data"]["licenses"]
    assert_not_available_content_gql(item)

    # '''permissions should take only predefined values'''
    query10 = """
        {
    licenses(permission:abcd){
        name
        code
        license
        permissions
        active
    }
    }
    """
    executed10 = gql_request(query10)
    assert isinstance(executed10, Dict)
    assert "errors" in executed10.keys()

def test_post():
    '''positive test case, checking for correct return object'''
    variables = {
    "object": {
        "license": "A very very long license text",
        "name": "Test License version 1",
        "code": "LIC-1",
        "permissions": ["private"]
    }
    }
    query = """
        mutation createlicense($object:InputAddLicense!){
    addLicense(licenseArgs:$object){
        message
        data{
        name
        code
        license
        permissions
        active
        }
    }
    }
    """
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables)
    assert isinstance(executed, Dict)
    assert executed["data"]["addLicense"]["message"] == "License uploaded successfully"
    item =executed["data"]["addLicense"]["data"]
    assert_positive_get(item)
    assert executed["data"]["addLicense"]["data"]["code"] == "LIC-1"

def test_post_casesensitive():
    '''positive test case, checking for case conversion of code'''
    variables1 = {
    "object": {
        "name": "Test License version 1",
        "code": "lic-1",
        "license": "a long long long text"
    }
    }
    query1 = """
        mutation createlicense($object:InputAddLicense!){
    addLicense(licenseArgs:$object){
        message
        data{
        name
        code
        license
        permissions
        active
        }
    }
    }
    """
    operation="mutation"
    executed1 = gql_request(query=query1, operation=operation, variables=variables1)
    assert isinstance(executed1, Dict)
    assert executed1["data"]["addLicense"]["message"] == "License uploaded successfully"
    item =executed1["data"]["addLicense"]["data"]
    assert_positive_get(item)
    assert executed1["data"]["addLicense"]["data"]["code"] == "LIC-1"
    assert executed1["data"]["addLicense"]["data"]["permissions"] == ["private"]


def test_post_mandatory():
    '''without mandatory fields'''
    query = """
        mutation createlicense($object:InputAddLicense!){
    addLicense(licenseArgs:$object){
        message
        data{
        name
        code
        license
        permissions
        active
        }
    }
    }
    """
    variables = {
    "object": {
        "name": "Test License version 4",
        "code": "LIC-4"
    }
    }
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables)
    assert isinstance(executed, Dict)
    assert "errors" in executed.keys()

    variables2 = {
    "object": {
        "code": "lic-4",
        "license": "Test License version 4"
    }
    }
    executed2 = gql_request(query=query, operation=operation, variables=variables2)
    assert isinstance(executed2, Dict)
    assert "errors" in executed2.keys()

    variables3 = {
    "object": {
        "license": "long long text",
        "name": "Test License version 4"
    }
    }
    executed3 = gql_request(query=query, operation=operation, variables=variables3)
    assert isinstance(executed3, Dict)
    assert "errors" in executed3.keys()

    # '''code should have letters numbers  . _ or - only validation check'''
    variables4 = {
    "object": {
        "license": "new-lang",
        "code": "AB@",
        "name": "new name"
    }
    }
    executed4 = gql_request(query=query, operation=operation, variables=variables4)
    assert isinstance(executed4, Dict)
    assert "errors" in executed4.keys()

    variables5 = {
    "object": {
      "license": "new-lang",
      "code": "AB 1",
      "name": "new name"
    }
    }
    executed5 = gql_request(query=query, operation=operation, variables=variables5)
    assert isinstance(executed5, Dict)
    assert "errors" in executed5.keys()

    # '''permissions should be from the pre-defined list''
    variables6 = {
    "object": {
      "license": "new- license text",
      "code": "MMM",
      "name": "new name",
      "permissions": ["regular"]
    }
    }
    executed6 = gql_request(query=query, operation=operation, variables=variables6)
    assert isinstance(executed6, Dict)
    assert "errors" in executed6.keys()

def test_put():
    '''Add a new license and then alter it'''
    variables = {
    "object": {
        "license": "A very very long license text",
        "name": "Test License version 1",
        "code": "LIC-1",
        "permissions": ["private"]
    }
    }
    query = """
        mutation createlicense($object:InputAddLicense!){
    addLicense(licenseArgs:$object){
        message
        data{
        name
        code
        license
        permissions
        active
        }
    }
    }
    """
    operation="mutation"
    executed = gql_request(query=query, operation=operation, variables=variables)
    assert isinstance(executed, Dict)
    assert executed["data"]["addLicense"]["message"] == "License uploaded successfully"
    item =executed["data"]["addLicense"]["data"]
    assert_positive_get(item)
    assert executed["data"]["addLicense"]["data"]["code"] == "LIC-1"

    #update section
    up_variable = {
    "object": {
        "code": "LIC-1",
        "name":"New name for test license"
        }
    }
    up_query = """
        mutation editlicense($object:InputEditLicense){
        editLicense(licenseArgs:$object){
            message
            data{
            name
            code
            license
            permissions
            active
            }
        }
        }
    """
    up_executed = gql_request(query=up_query, operation=operation, variables=up_variable)
    assert isinstance(up_executed, Dict)
    assert up_executed["data"]["editLicense"]["message"] == "License edited successfully"
    assert up_executed["data"]["editLicense"]["data"]["name"] == "New name for test license"

    up_variable2 = {
    "object": {
        "code": "LIC-1",
        "license":"A different text"
        }
    }
    up_executed2 = gql_request(query=up_query, operation=operation, variables=up_variable2)
    assert isinstance(up_executed2, Dict)
    assert up_executed2["data"]["editLicense"]["message"] == "License edited successfully"
    assert up_executed2["data"]["editLicense"]["data"]["license"] == "A different text"

    up_variable3 = {
    "object": {
        "code": "LIC-1",
        "permissions":["patent","private"]
        }
    }
    up_executed3 = gql_request(query=up_query, operation=operation, variables=up_variable3)
    assert isinstance(up_executed3, Dict)
    assert up_executed3["data"]["editLicense"]["message"] == "License edited successfully"
    assert up_executed3["data"]["editLicense"]["data"]["permissions"] == ["patent","private"]

    # unavailable code
    up_variable4 = {
    "object": {
        "code": "LIC-12"
        }
    }
    up_executed4 = gql_request(query=up_query, operation=operation, variables=up_variable4)
    assert isinstance(up_executed4, Dict)
    assert "errors" in up_executed4.keys()

    # without code
    up_variable5 = {
    "object": {
        "name": "some name",
        "active":False
        }
    }
    up_executed5 = gql_request(query=up_query, operation=operation, variables=up_variable5)
    assert isinstance(up_executed5, Dict)
    assert "errors" in up_executed5.keys()

    #deactivate or soft-delete
    query_read = """
        {
    licenses{
        name
        code
        license
        permissions
        active
    }
    }
    """
    rd_executed = gql_request(query_read)
    assert isinstance(rd_executed, Dict)
    assert len(rd_executed["data"]["licenses"])<=3
    assert isinstance(rd_executed["data"]["licenses"], list)

    up_variable6 = {
    "object": {
        "code": "LIC-1",
        "active":False
        }
    }
    up_executed6 = gql_request(query=up_query, operation=operation, variables=up_variable6)
    assert isinstance(up_executed6, Dict)
    assert "errors" not in up_executed6.keys()

    query_read2 = """
        {
    licenses{
        name
        code
        license
        permissions
        active
    }
    }
    """
    rd_executed2 = gql_request(query_read2)
    assert isinstance(rd_executed2, Dict)
    assert len(rd_executed["data"]["licenses"]) - len(rd_executed2["data"]["licenses"]) == 1
