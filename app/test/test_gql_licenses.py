from typing import Dict
from .test_licenses import assert_positive_get
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
    variables1 = {
    "object": {
        "code": "LIC-1",
        "permissions":["Private", "Patent"]
    }
    }
    query_update = """
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
    executed1 = gql_request(query=query_update, operation=operation, variables=variables1)
    assert isinstance(executed1, Dict)
    assert executed1["data"]["editLicense"]["message"] == "License edited successfully"
    assert executed1["data"]["editLicense"]["data"]["permissions"] == ["Private", "Patent"]
    
