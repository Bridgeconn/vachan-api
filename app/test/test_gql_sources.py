# """Test cases for Sources in GQL"""
# from typing import Dict

# from app.schema import schema_auth
# from app.graphql_api import types
# #pylint: disable=E0401
# from .test_sources import assert_positive_get
# from .test_gql_versions import GLOBAL_QUERY as version_query
# from .test_gql_versions import check_post as version_add
# #pylint: disable=E0611
# #pylint: disable=R0914
# #pylint: disable=R0915
# from . import check_skip_limit_gql, gql_request,assert_not_available_content_gql
# from .conftest import initial_test_users
# from . test_gql_auth_basic import login,SUPER_PASSWORD,SUPER_USER

# headers_auth = {"contentType": "application/json",
#                 "accept": "application/json", "App":schema_auth.App.VACHANADMIN.value}
# headers = {"contentType": "application/json", "accept": "application/json"}

# SOURCE_GLOBAL_VARIABLES = {
#   "object": {
#     "contentType": "commentary",
#     "language": "hi",
#     "version": "TTT",
#     "versionTag": "1",
#     "year": 2021,
#     "license": "CC-BY-SA",
#     "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#   }
# }

# SOURCE_GLOBAL_QUERY = """
#     mutation createsource($object:InputAddSource){
#     addSource(sourceArg:$object){
#         message
#         data{
#         sourceName
#         contentType{
#             contentId
#             contentType
#         }
#         language{
#             languageId
#             language
#             code
#             scriptDirection
#             metaData
#         }
#         version{
#             versionId
#             versionAbbreviation
#             versionName
#             versionTag
#             metaData
#         }
#         year
#         license{
#             name
#             code
#             license
#             permissions
#             active
#         }
#         metaData
#         active
#         }
#     }
#     }
#     """

# SOURCE_GLOBAL_QUERY_UPDATE="""
#         mutation editsource($object:InputEditSource){
#   editSource(sourceArg:$object){
#     message
#     data{
#       sourceName
#       contentType{
#         contentId
#         contentType
#       }
#       language{
#         languageId
#         language
#         code
#         scriptDirection
#         metaData
#       }
#       version{
#         versionId
#         versionAbbreviation
#         versionName
#         versionTag
#         metaData
#       }
#       year
#       license{
#         name
#         code
#         license
#         permissions
#         active
#       }
#       metaData
#       active
#     }
#   }
# }
#     """

# headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']    

# def check_post(query,variables):
#     """positive post test"""
#     headers_auth['App'] = schema_auth.App.VACHANADMIN.value
#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
#     #without auth
#     executed = gql_request(query=query,operation="mutation", variables=variables)
#     assert "errors" in executed
#     #with auth
#     executed = gql_request(query=query,operation="mutation", variables=variables,
#       headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert executed["data"]["addSource"]["message"] == "Source created successfully"
#     item =executed["data"]["addSource"]["data"]
#     assert_positive_get(item)
#     return executed

# def test_post_default():
#     '''Positive test to add a new source'''
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     #create source
#     check_post(SOURCE_GLOBAL_QUERY,SOURCE_GLOBAL_VARIABLES)

    

#     query_check = """
#       query contents($skip:Int, $limit:Int){
#   contents(skip:$skip,limit:$limit){
#     sourceName
#   }
# }
#     """
#     check_skip_limit_gql(query_check,"contents",headers_auth)

# def test_post_wrong_version():
#     '''Negative test with not available version or versionTag'''
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)

#     #wrong version
#     variables1 = {
#     "object": {
#         "contentType": "commentary",
#         "language": "hi",
#         "version": "TTD",
#         "versionTag": "1",
#         "year": 2021,
#         "license": "ISC",
#         "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#     }
#     }
#     executed1 = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables1,
#       headers=headers_auth)
#     assert isinstance(executed1, Dict)
#     assert "errors" in executed1.keys()

#     #wrong versionTag
#     variables2 = {
#     "object": {
#         "contentType": "commentary",
#         "language": "hi",
#         "version": "TTT",
#         "versionTag": "2",
#         "year": 2021,
#         "license": "ISC",
#         "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#     }
#     }
#     executed2 = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables2,
#       headers=headers_auth)
#     assert isinstance(executed2, Dict)
#     assert "errors" in executed2.keys()

#     #working post
#     check_post(SOURCE_GLOBAL_QUERY,SOURCE_GLOBAL_VARIABLES)

# def test_post_wrong_lang():
#     '''Negative test with not available language'''
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)

#     variables = {
#     "object": {
#         "contentType": "commentary",
#         "language": "aaj",
#         "version": "TTT",
#         "versionTag": "1",
#         "year": 2021,
#         "license": "ISC",
#         "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#     }
#     }
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables,
#       headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert "errors" in executed.keys()

# def test_post_wrong_content():
#     '''Negative test with not available content type'''
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     variables = {
#     "object": {
#         "contentType": "bibl",
#         "language": "hi",
#         "version": "TTT",
#         "versionTag": "1",
#         "year": 2021,
#         "license": "ISC",
#         "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#     }
#     }
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables,
#       headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert "errors" in executed.keys()

#     # '''Negative test with not a valid license from license table'''
#     variables2 = {
#     "object": {
#         "contentType": "infographic",
#         "language": "hi",
#         "version": "TTT",
#         "versionTag": "1",
#         "year": 2021,
#         "license": "XYZ-123",
#         "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#     }
#     }
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables2,
#       headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert "errors" in executed.keys()

# def test_post_wrong_year():
#     '''Negative test with text in year field'''
#     variables = {
#     "object": {
#         "contentType": "bible",
#         "language": "hi",
#         "version": "TTT",
#         "versionTag": "1",
#         "year": "twenty twenty",
#         "license": "ISC",
#         "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#     }
#     }
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables,
#     headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert "errors" in executed.keys()

# def test_post_wrong_metadata():
#     '''Negative test with incorrect format for metadata'''
#     variables = {
#     "object": {
#         "contentType": "bible",
#         "language": "hi",
#         "version": "TTT",
#         "versionTag": "1",
#         "year": 2021,
#         "license": "ISC",
#         "metaData": "{\"owner\"=\"someone\",\"access-key\"=\"123xyz\"}"
#     }
#     }
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables,
#       headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert "errors" in executed.keys()

# def test_post_missing_mandatory_info():
#     '''Negative tests with mandatory contents missing'''
#     # no contentType
#     variables = {
#     "object": {
#         "language": "hi",
#         "version": "TTT",
#         "versionTag": "1",
#         "year": 2021,
#         "license": "ISC",
#         "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#     }
#     }
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables,
#       headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert "errors" in executed.keys()

#     # no language
#     variables2 = {
#     "object": {
#         "contentType": "bible",
#         "version": "TTT",
#         "versionTag": "1",
#         "year": 2021,
#         "license": "ISC",
#         "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#     }
#     }
#     executed2 = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables2,
#       headers=headers_auth)
#     assert isinstance(executed2, Dict)
#     assert "errors" in executed2.keys()

#     # no version
#     variables3 = {
#     "object": {
#         "contentType": "bible",
#         "language": "hi",
#         "versionTag": "1",
#         "year": 2021,
#         "license": "ISC",
#         "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#     }
#     }
#     executed3 = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables3,
#       headers=headers_auth)
#     assert isinstance(executed3, Dict)
#     assert "errors" in executed3.keys()

#     #no year
#     variables4 = {
#     "object": {
#         "contentType": "bible",
#         "language": "hi",
#         "version": "TTT",
#         "versionTag": "1",
#         "license": "ISC",
#         "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
#     }
#     }
#     executed4 = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables4,
#       headers=headers_auth)
#     assert isinstance(executed4, Dict)
#     assert "errors" in executed4.keys()

# def test_post_missing_some_info():
#     '''Positive test with non mandatory contents missing.
#     If versionTag not specified, 1 is assumed. Other fields are nullable or have default value'''
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     #create source
#     variables = {
#     "object": {
#         "contentType": "commentary",
#         "language": "hi",
#         "version": "TTT",
#         "year": 2021
#     }
#     }
#     check_post(SOURCE_GLOBAL_QUERY,variables)

# def test_post_duplicate():
#     '''Add the same source twice'''
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     variables = {
#     "object": {
#         "contentType": "commentary",
#         "language": "hi",
#         "version": "TTT",
#         "year": 2021
#     }
#     }
#     check_post(SOURCE_GLOBAL_QUERY,variables)
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables,
#       headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert "errors" in executed.keys()

# SOURCE_GET = """
#     {
#   contents{
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#     language{
#       languageId
#       language
#       code
#       scriptDirection
#       metaData
#     }
#     version{
#       versionId
#       versionAbbreviation
#       versionName
#       versionTag
#       metaData
#     }
#     year
#     license{
#       name
#       code
#       license
#       permissions
#       active
#     }
#     metaData
#     active
#   }
# }
# """

# def test_get_empty():
#     '''Test get before adding data to table. Usually done on freshly set up test DB.
#     If the testing is done on a DB that already has some data, the response wont be empty.'''
#     executed = gql_request(query=SOURCE_GET,headers=headers_auth)
#     assert isinstance(executed, Dict)
#     if len(executed["data"]["contents"]) == 0:
#         assert_not_available_content_gql(executed["data"]["contents"])


# def test_get_wrong_values():
#     '''Checks input validation for query params'''
#     get_query = """
#             {
#     contents(versionAbbreviation:1){
#         sourceName
#         contentType{
#         contentId
#         contentType
#         }
#     }
#     }
#     """
#     executed = gql_request(query=get_query,headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert "errors" in executed.keys()

#     get_query3 = """
#         {
#   contents(languageCode:"hin6i"){
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#   }
# }
#     """
#     executed3 = gql_request(query=get_query3,headers=headers_auth)
#     assert isinstance(executed3, Dict)
#     assert_not_available_content_gql(executed3["data"]["contents"])

# def test_get_after_adding_data():
#     '''Add some sources to DB and test fecthing those data'''
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     variables = {
#     "object": {
#         "contentType": "infographic",
#         "version": "TTT",
#         "year": 2021,
#     }
#     }
#     for lang in ['hi', 'mr', 'te']:
#         variables["object"]['language'] = lang
#         check_post(SOURCE_GLOBAL_QUERY,variables)

#     version_variable["object"]['versionTag'] = "2"
#     version_add(version_query,version_variable)
#     variables["object"]['versionTag'] = '2'
#     for lang in ['hi', 'mr', 'te']:
#         variables["object"]['language'] = lang
#         check_post(SOURCE_GLOBAL_QUERY,variables)

#     variables["object"]['contentType'] = 'commentary'
#     variables["object"]['versionTag'] = "1"
#     variables["object"]['metaData'] = "{\"owner\":\"myself\"}"
#     variables["object"]['license'] = "ISC"
#     for lang in ['hi', 'mr', 'te']:
#         variables["object"]['language'] = lang
#         check_post(SOURCE_GLOBAL_QUERY,variables)

#     #without auth
#     executed = gql_request(query=SOURCE_GET)
#     assert_not_available_content_gql(executed["data"]["contents"])

#     #with auth
#     executed = gql_request(query=SOURCE_GET,headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert len(executed["data"]["contents"]) > 0
#     items = executed["data"]["contents"]
#     for item in items:
#         assert_positive_get(item)

#     # filter with contentType
#     query1= """
#         {
#   contents(contentType:"commentary",latestRevision:false){
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#     language{
#       languageId
#       language
#       code
#       scriptDirection
#       metaData
#     }
#     version{
#       versionId
#       versionAbbreviation
#       versionName
#       versionTag
#       metaData
#     }
#     year
#     license{
#       name
#       code
#       license
#       permissions
#       active
#     }
#     metaData
#     active
#   }
# }
#     """
#     executed1 = gql_request(query=query1,headers=headers_auth)
#     assert isinstance(executed1, Dict)
#     assert len(executed1["data"]["contents"]) >= 3
#     items = executed1["data"]["contents"]
#     for item in items:
#         assert_positive_get(item)

#     # filter with language
#     query2 = """
#         {
#   contents(languageCode:"hi",latestRevision:false){
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#     language{
#       languageId
#       language
#       code
#       scriptDirection
#       metaData
#     }
#     version{
#       versionId
#       versionAbbreviation
#       versionName
#       versionTag
#       metaData
#     }
#     year
#     license{
#       name
#       code
#       license
#       permissions
#       active
#     }
#     metaData
#     active
#   }
# }
#     """
#     executed2 = gql_request(query=query2,headers=headers_auth)
#     assert isinstance(executed2, Dict)
#     assert len(executed2["data"]["contents"]) >= 3
#     items = executed2["data"]["contents"]
#     for item in items:
#         assert_positive_get(item)

#     # filter with versionTag
#     query3 = """
#         {
#   contents(versionTag:2){
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#     language{
#       languageId
#       language
#       code
#       scriptDirection
#       metaData
#     }
#     version{
#       versionId
#       versionAbbreviation
#       versionName
#       versionTag
#       metaData
#     }
#     year
#     license{
#       name
#       code
#       license
#       permissions
#       active
#     }
#     metaData
#     active
#   }
# }
#     """
#     executed3 = gql_request(query=query3,headers=headers_auth)
#     assert isinstance(executed3, Dict)
#     assert len(executed3["data"]["contents"]) >= 3
#     items = executed3["data"]["contents"]
#     for item in items:
#         assert_positive_get(item)

#     # filter with version
#     query4 = """
#         {
#   contents(versionAbbreviation:"TTT",latestRevision:false){
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#     language{
#       languageId
#       language
#       code
#       scriptDirection
#       metaData
#     }
#     version{
#       versionId
#       versionAbbreviation
#       versionName
#       versionTag
#       metaData
#     }
#     year
#     license{
#       name
#       code
#       license
#       permissions
#       active
#     }
#     metaData
#     active
#   }
# }
#     """
#     executed4 = gql_request(query=query4,headers=headers_auth)
#     assert isinstance(executed4, Dict)
#     assert len(executed4["data"]["contents"]) >= 9
#     items = executed4["data"]["contents"]
#     for item in items:
#         assert_positive_get(item)

#   # filter with sourcename
#     query_source = """
#         {
#   contents(sourceName:"hi_TTT_1_commentary"){
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#     language{
#       languageId
#       language
#       code
#       scriptDirection
#       metaData
#     }
#     version{
#       versionId
#       versionAbbreviation
#       versionName
#       versionTag
#       metaData
#     }
#     year
#     license{
#       name
#       code
#       license
#       permissions
#       active
#     }
#     metaData
#     active
#   }
# }
#     """
#     executed_source = gql_request(query=query_source,headers=headers_auth)
#     assert isinstance(executed_source, Dict)
#     assert len(executed_source["data"]["contents"]) == 1
#     items = executed_source["data"]["contents"]
#     for item in items:
#         assert_positive_get(item)

#     # filter with license
#     query5 = """
#         {
#   contents(licenseCode:"CC-BY-SA"){
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#     language{
#       languageId
#       language
#       code
#       scriptDirection
#       metaData
#     }
#     version{
#       versionId
#       versionAbbreviation
#       versionName
#       versionTag
#       metaData
#     }
#     year
#     license{
#       name
#       code
#       license
#       permissions
#       active
#     }
#     metaData
#     active
#   }
# }
#     """
#     executed5 = gql_request(query=query5,headers=headers_auth)
#     assert isinstance(executed5, Dict)
#     assert len(executed5["data"]["contents"]) >= 3
#     items = executed5["data"]["contents"]
#     for item in items:
#         assert_positive_get(item)

#     # filter with license ISC
#     query6 = """
#         {
#   contents(licenseCode:"ISC"){
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#     language{
#       languageId
#       language
#       code
#       scriptDirection
#       metaData
#     }
#     version{
#       versionId
#       versionAbbreviation
#       versionName
#       versionTag
#       metaData
#     }
#     year
#     license{
#       name
#       code
#       license
#       permissions
#       active
#     }
#     metaData
#     active
#   }
# }
#     """
#     executed6 = gql_request(query=query6,headers=headers_auth)
#     assert isinstance(executed6, Dict)
#     assert len(executed6["data"]["contents"]) >= 3
#     items = executed6["data"]["contents"]
#     for item in items:
#         assert_positive_get(item)

# # filter with version and versionTag
#     query7 = """
#     {
#   contents(versionAbbreviation:"TTT",versionTag:1){
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#     language{
#       languageId
#       language
#       code
#       scriptDirection
#       metaData
#     }
#     version{
#       versionId
#       versionAbbreviation
#       versionName
#       versionTag
#       metaData
#     }
#     year
#     license{
#       name
#       code
#       license
#       permissions
#       active
#     }
#     metaData
#     active
#   }
# }
# """
#     executed7 = gql_request(query=query7,headers=headers_auth)
#     assert isinstance(executed7, Dict)
#     assert len(executed7["data"]["contents"]) >= 3
#     items = executed7["data"]["contents"]
#     for item in items:
#         assert_positive_get(item)


# def test_get_source_filter_access_tag():
#     """filter source with access tags"""
#     #create source 
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     #create source
#     source_data = {
#   "object": {
#     "contentType": "infographic",
#     "version": "TTT",
#     "year": 2020,
#     "accessPermissions": [
#       types.SourcePermissions.CONTENT.name
#     ],
#   }
# }
#     source_data["object"]['language'] = 'hi'
#     check_post(SOURCE_GLOBAL_QUERY,source_data)

#     source_data["object"]['language'] = 'mr'
#     source_data["object"]['accessPermissions'] = [types.SourcePermissions.OPENACCESS.name]
#     check_post(SOURCE_GLOBAL_QUERY,source_data)

#     source_data["object"]['language'] = 'te'
#     source_data["object"]['accessPermissions'] = [types.SourcePermissions.PUBLISHABLE.name]
#     check_post(SOURCE_GLOBAL_QUERY,source_data)

#     get_qry = """
#       query get_source($obj:[SourcePermissions],$ver:String){
#   contents(accessTag:$obj,versionAbbreviation:$ver){
#     sourceName
#   }
# }
#     """
#     get_var = {
#     "obj": [
#     types.SourcePermissions.CONTENT.name
#   ],
#   "ver": "TTT"
# }
#     executed1 = gql_request(query=get_qry,variables=get_var, headers=headers_auth)
#     assert isinstance(executed1, Dict)
#     assert len(executed1["data"]["contents"]) >= 3

#     get_var["obj"] = [types.SourcePermissions.OPENACCESS.name]
#     executed2 = gql_request(query=get_qry,variables=get_var, headers=headers_auth)
#     assert isinstance(executed2, Dict)
#     assert len(executed2["data"]["contents"]) >= 1

#     get_var["obj"] = [types.SourcePermissions.PUBLISHABLE.name]
#     executed3 = gql_request(query=get_qry,variables=get_var, headers=headers_auth)
#     assert isinstance(executed3, Dict)
#     assert len(executed3["data"]["contents"]) >= 1

#     get_var["obj"] = [types.SourcePermissions.PUBLISHABLE.name,types.SourcePermissions.OPENACCESS.name]
#     executed4 = gql_request(query=get_qry,variables=get_var, headers=headers_auth,)
#     assert_not_available_content_gql(executed4["data"]["contents"])


# def test_put_default():
#     '''Add some data and test updating them'''
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     version_variable["object"]['versionTag'] = "2"
#     version_add(version_query,version_variable)
#     variables = {
#     "object": {
#         "contentType": "commentary",
#         "version": "TTT",
#         'language': 'ml',
#         "year": 2021,
#     }
#     }
#     check_post(SOURCE_GLOBAL_QUERY,variables)

# #     #data update
# #     up_query="""
# #         mutation editsource($object:InputEditSource){
# #   editSource(sourceArg:$object){
# #     message
# #     data{
# #       sourceName
# #       contentType{
# #         contentId
# #         contentType
# #       }
# #       language{
# #         languageId
# #         language
# #         code
# #         scriptDirection
# #         metaData
# #       }
# #       version{
# #         versionId
# #         versionAbbreviation
# #         versionName
# #         versionTag
# #         metaData
# #       }
# #       year
# #       license{
# #         name
# #         code
# #         license
# #         permissions
# #         active
# #       }
# #       metaData
# #       active
# #     }
# #   }
# # }
# #     """
#     up_variables={
#   "object": {
#     "sourceName": "ml_TTT_1_commentary",
#     "versionTag": "2"
#   }
# }
#     #without auth
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY_UPDATE,operation="mutation", variables=up_variables)
#     assert "errors" in executed
#     #with auth
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY_UPDATE,operation="mutation", variables=up_variables,
#       headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert executed["data"]["editSource"]["message"] == "Source edited successfully"
#     item =executed["data"]["editSource"]["data"]
#     assert_positive_get(item)
#     assert item["version"]["versionTag"] == "2"
#     assert item['sourceName'] == "ml_TTT_2_commentary"

#     up_variables2={
#   "object": {
#     "sourceName": "ml_TTT_2_commentary",
#     "metaData": "{\"owner\":\"new owner\"}"
#   }
# }
#     executed2 = gql_request(query=SOURCE_GLOBAL_QUERY_UPDATE,operation="mutation", variables=up_variables2,
#       headers=headers_auth)
#     assert isinstance(executed2, Dict)
#     assert executed2["data"]["editSource"]["message"] == "Source edited successfully"
#     item =executed2["data"]["editSource"]["data"]
#     assert_positive_get(item)
#     assert item['metaData']['owner'] == "new owner"

# def test_post_put_gitlab_source():
#     '''Positive test for gitlab content type'''
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     variables = {
#     "object": {
#         "contentType": "gitlabrepo",
#         "version": "TTT",
#         'language': 'hi',
#         "year": 2021,
#     }}
#     # error for no repo link in metadata
#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables,
#       headers=headers_auth)
#     assert "errors" in executed

#     link ="https://gitlab/project/video"
#     link2 = "https://gitlab/project/videoNew"

#     # with repo link default branch is main
#     variables["object"]["metaData"] = "{\"repo\":\""+link+"\"}"
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables,
#       headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert executed["data"]["addSource"]["message"] == "Source created successfully"
#     assert executed["data"]["addSource"]['data']["metaData"]["defaultBranch"] == "main"

#     # create another source with same repo link
#     variables["object"]["language"] = "ml"
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables,
#       headers=headers_auth)
#     assert "errors" in executed

#     # update another source with exising repo link
#     variables["object"]["metaData"] = "{\"repo\":\""+link2+"\"}"
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", variables=variables,
#       headers=headers_auth)
#     assert executed["data"]["addSource"]["message"] == "Source created successfully"

#     up_variables={
#   "object": {
#     "sourceName": "ml_TTT_1_gitlabrepo",
#     "metaData": "{\"repo\":\""+link+"\"}"
#   }
# }
#     executed2 = gql_request(query=SOURCE_GLOBAL_QUERY_UPDATE,operation="mutation", variables=up_variables,
#       headers=headers_auth)
#     assert "errors" in executed2
    

# def test_soft_delete():
#     '''Soft delete is achived by updating the active flag to Fasle'''
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     variables = {
#     "object": {
#         "contentType": "commentary",
#         "version": "TTT",
#         'language': 'ml',
#         "year": 2021
#     }
#     }
#     executed = check_post(SOURCE_GLOBAL_QUERY,variables)
#     assert executed["data"]["addSource"]["data"]["active"]

#        #data update
#     up_query="""
#         mutation editsource($object:InputEditSource){
#   editSource(sourceArg:$object){
#     message
#     data{
#       sourceName
#       contentType{
#         contentId
#         contentType
#       }
#       language{
#         languageId
#         language
#         code
#         scriptDirection
#         metaData
#       }
#       version{
#         versionId
#         versionAbbreviation
#         versionName
#         versionTag
#         metaData
#       }
#       year
#       license{
#         name
#         code
#         license
#         permissions
#         active
#       }
#       metaData
#       active
#     }
#   }
# }
#     """
#     up_variables={
#   "object": {
#     'sourceName': 'ml_TTT_1_commentary',
#     "active": False
#   }
# }
#     executed2 = gql_request(query=up_query,operation="mutation", variables=up_variables,
#       headers=headers_auth)
#     assert isinstance(executed2, Dict)
#     assert executed2["data"]["editSource"]["message"] == "Source edited successfully"
#     item =executed2["data"]["editSource"]["data"]
#     assert_positive_get(item)
#     assert not item['active']

#     query1 = """
#         {
#   contents(active:false){
#     sourceName
#     contentType{
#       contentId
#       contentType
#     }
#     language{
#       languageId
#       language
#       code
#       scriptDirection
#       metaData
#     }
#     version{
#       versionId
#       versionAbbreviation
#       versionName
#       versionTag
#       metaData
#     }
#     year
#     license{
#       name
#       code
#       license
#       permissions
#       active
#     }
#     metaData
#     active
#   }
# }
#     """
#     executed = gql_request(query=query1,headers=headers_auth)
#     assert isinstance(executed, Dict)
#     assert len(executed["data"]["contents"]) > 0
#     items = executed["data"]["contents"]
#     for item in items:
#         assert_positive_get(item)
#         assert not item["active"]
# #pylint: disable=C0302
#     assert 'ml_TTT_1_commentary' in [item['sourceName'] for item in items]

# def test_created_user_can_only_edit():
#     """source edit can do by created user and Super Admin"""
#     SA_user_data = {
#             "user_email": SUPER_USER,
#             "password": SUPER_PASSWORD
#         }
#     response = login(SA_user_data)
#     token =  response["data"]["login"]["token"]

#     headers_SA = {"contentType": "application/json",
#                     "accept": "application/json",
#                     'Authorization': "Bearer"+" "+token
#                 }

#     #create source 
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     #create source
#     executed = gql_request(query=SOURCE_GLOBAL_QUERY,operation="mutation", 
#       variables=SOURCE_GLOBAL_VARIABLES,headers=headers_SA)
#     assert isinstance(executed, Dict)
#     assert executed["data"]["addSource"]["message"] == "Source created successfully"
    
#     #Edit with SA Created User
#     up_query="""
#         mutation editsource($object:InputEditSource){
#   editSource(sourceArg:$object){
#     message
#     data{
#       sourceName
#       contentType{
#         contentId
#         contentType
#       }
#       language{
#         languageId
#         language
#         code
#         scriptDirection
#         metaData
#       }
#       version{
#         versionId
#         versionAbbreviation
#         versionName
#         versionTag
#         metaData
#       }
#       year
#       license{
#         name
#         code
#         license
#         permissions
#         active
#       }
#       metaData
#       active
#     }
#   }
# }
#     """
#     up_variables={
#   "object": {
#     "sourceName": "hi_TTT_1_commentary",
#     "metaData": "{\"owner\":\"New One\",\"access-key\":\"123xyz\"}"
#   }
# }
#     #with auth
#     executed = gql_request(query=up_query,operation="mutation", variables=up_variables,
#       headers=headers_SA)
#     assert isinstance(executed, Dict)
#     assert executed["data"]["editSource"]["message"] == "Source edited successfully"

#     #Edit with Not created User
#     executed = gql_request(query=up_query,operation="mutation", variables=up_variables,
#       headers=headers_auth)
#     assert "errors" in executed

# def test_diffrernt_sources_with_app_and_roles():
#     """Test getting sources with users having different permissions and 
#     also from multiple apps"""
#     headers_auth = {"contentType": "application/json",
#                 "accept": "application/json"
#             }
#     #app names
#     API = types.App.API
#     AG =  types.App.AG
#     VACHAN = types.App.VACHAN
#     VACHANADMIN = types.App.VACHANADMIN

#     #create sources for test with different access permissions
#     #content is default
#     #create source 
#     version_variable = {
#         "object": {
#         "versionAbbreviation": "TTT",
#         "versionName": "test version"
#     }
#     }
#     #Create a version
#     version_add(version_query,version_variable)
#     #create source
#     source_data = {
#   "object": {
#     "contentType": "commentary",
#     "language": "hi",
#     "version": "TTT",
#     "year": 2020,
#     "accessPermissions": [
#       types.SourcePermissions.CONTENT.name
#     ],
#   }
# }
#     resposne = check_post(SOURCE_GLOBAL_QUERY,source_data)
#     resp_data = resposne["data"]["addSource"]["data"]["metaData"]
#     assert resp_data["accessPermissions"] == [types.SourcePermissions.CONTENT.value]

#     #open-access
#     source_data["object"]["language"] = 'ml'
#     source_data["object"]["accessPermissions"] = [types.SourcePermissions.OPENACCESS.name]
#     resposne = check_post(SOURCE_GLOBAL_QUERY,source_data)
#     resp_data = resposne["data"]["addSource"]["data"]["metaData"]
#     assert resp_data["accessPermissions"] == \
#       [types.SourcePermissions.OPENACCESS.value , types.SourcePermissions.CONTENT.value]

#     #publishable
#     source_data["object"]["language"] = 'tn'
#     source_data["object"]["accessPermissions"] = [types.SourcePermissions.PUBLISHABLE.name]
#     resposne = check_post(SOURCE_GLOBAL_QUERY,source_data)
#     resp_data = resposne["data"]["addSource"]["data"]["metaData"]
#     assert resp_data["accessPermissions"] == \
#       [types.SourcePermissions.PUBLISHABLE.value , types.SourcePermissions.CONTENT.value]

#     #downloadable
#     source_data["object"]["language"] = 'af'
#     source_data["object"]["accessPermissions"] = [types.SourcePermissions.DOWNLOADABLE.name]
#     resposne = check_post(SOURCE_GLOBAL_QUERY,source_data)
#     resp_data = resposne["data"]["addSource"]["data"]["metaData"]
#     assert resp_data["accessPermissions"] == \
#       [types.SourcePermissions.DOWNLOADABLE.value , types.SourcePermissions.CONTENT.value]

#     #derivable
#     source_data["object"]["language"] = 'ak'
#     source_data["object"]["accessPermissions"] = [types.SourcePermissions.DERIVABLE.name]
#     resposne = check_post(SOURCE_GLOBAL_QUERY,source_data)
#     resp_data = resposne["data"]["addSource"]["data"]["metaData"]
#     assert resp_data["accessPermissions"] == \
#       [types.SourcePermissions.DERIVABLE.value , types.SourcePermissions.CONTENT.value]
    
#     filter_qry = """
#       {
#   contents(versionAbbreviation:"TTT"){
#     sourceName
#     metaData
#   }
# }
#     """
#     permission = types.SourcePermissions

#     def check_resp_permission(response,check_list):
#         """function to check permission in response"""
#         db_perm_list = []
#         for i in range(len(response)):
#             temp_list = response[i]["metaData"]['accessPermissions']
#             db_perm_list = db_perm_list + list(set(temp_list)-set(db_perm_list))
#         for item in check_list:
#             assert item in db_perm_list
#         # check based on source
#         for item in response:
#             if item["sourceName"] == "hi_TTT_1_commentary":
#                 assert permission.CONTENT.value in item['metaData']['accessPermissions']
#             elif item["sourceName"] == "ml_TTT_1_commentary":
#                 assert permission.OPENACCESS.value in item['metaData']['accessPermissions']
#             elif item["sourceName"] == "tn_TTT_1_commentary":
#                 assert permission.PUBLISHABLE.value in item['metaData']['accessPermissions']
#             elif item["sourceName"] == "af_TTT_1_commentary":
#                 assert permission.DOWNLOADABLE.value in item['metaData']['accessPermissions']
#             elif item["sourceName"] == "ak_TTT_1_commentary":
#                 assert permission.DERIVABLE.value in item['metaData']['accessPermissions']

#     #Get without Login
#     #default : API
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     # assert permission.OPENACCESS.value in resp_data[0]["metaData"]['accessPermissions']
#     check_list = [permission.OPENACCESS.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Autographa
#     headers_auth['app'] = types.App.AG.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["contents"])
#     #APP : Vachan Online
#     headers_auth['app'] = types.App.VACHAN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Admin
#     headers_auth['app'] = types.App.VACHANADMIN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["contents"])

#     #Get with AgUser
#     #default : API
#     headers_auth = {"contentType": "application/json","accept": "application/json"}
#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgUser']['token']
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Autographa
#     headers_auth['app'] = types.App.AG.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Online
#     headers_auth['app'] = types.App.VACHAN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Admin
#     headers_auth['app'] = types.App.VACHANADMIN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["contents"])

#     #Get with VachanUser
#     #default : API
#     headers_auth = {"contentType": "application/json","accept": "application/json"}
#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Autographa
#     headers_auth['app'] = types.App.AG.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["contents"])    
#     #APP : Vachan Online
#     headers_auth['app'] = types.App.VACHAN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Admin
#     headers_auth['app'] = types.App.VACHANADMIN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["contents"])    

#     #Get with VachanAdmin
#     #default : API
#     headers_auth = {"contentType": "application/json","accept": "application/json"}
#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 5
#     # assert permission.CONTENT.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.OPENACCESS.value in resp_data[1]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[2]['metaData']['accessPermissions']
#     # assert permission.DOWNLOADABLE.value in resp_data[3]['metaData']['accessPermissions']
#     # assert permission.DERIVABLE.value in resp_data[4]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value,permission.CONTENT.value,
#       permission.DOWNLOADABLE.value, permission.DERIVABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Autographa
#     headers_auth['app'] = types.App.AG.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["contents"])    
#     #APP : Vachan Online
#     headers_auth['app'] = types.App.VACHAN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Admin
#     headers_auth['app'] = types.App.VACHANADMIN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 5
#     # assert permission.CONTENT.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.OPENACCESS.value in resp_data[1]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[2]['metaData']['accessPermissions']
#     # assert permission.DOWNLOADABLE.value in resp_data[3]['metaData']['accessPermissions']
#     # assert permission.DERIVABLE.value in resp_data[4]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value,permission.CONTENT.value,
#       permission.DOWNLOADABLE.value, permission.DERIVABLE.value]
#     check_resp_permission(resp_data,check_list)

#     #Get with API-User
#     #default : API
#     headers_auth = {"contentType": "application/json","accept": "application/json"}
#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['APIUser']['token']
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Autographa
#     headers_auth['app'] = types.App.AG.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["contents"])    
#     #APP : Vachan Online
#     headers_auth['app'] = types.App.VACHAN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Admin
#     headers_auth['app'] = types.App.VACHANADMIN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["contents"])    

#     #Get with AgAdmin
#     #default : API
#     headers_auth = {"contentType": "application/json","accept": "application/json"}
#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Autographa
#     headers_auth['app'] = types.App.AG.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Online
#     headers_auth['app'] = types.App.VACHAN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Admin
#     headers_auth['app'] = types.App.VACHANADMIN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert len(executed["data"]["contents"]) == 0

#     #Get with BcsDeveloper
#     #default : API
#     headers_auth = {"contentType": "application/json","accept": "application/json"}
#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['BcsDev']['token']
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 5
#     # assert permission.CONTENT.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.OPENACCESS.value in resp_data[1]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[2]['metaData']['accessPermissions']
#     # assert permission.DOWNLOADABLE.value in resp_data[3]['metaData']['accessPermissions']
#     # assert permission.DERIVABLE.value in resp_data[4]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value,permission.CONTENT.value,
#       permission.DOWNLOADABLE.value, permission.DERIVABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Autographa
#     headers_auth['app'] = types.App.AG.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["contents"])    
#     #APP : Vachan Online
#     headers_auth['app'] = types.App.VACHAN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Admin
#     headers_auth['app'] = types.App.VACHANADMIN.value
#     executed = gql_request(query=filter_qry, headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["contents"])

#     #Super Admin
#     SA_user_data = {
#             "user_email": SUPER_USER,
#             "password": SUPER_PASSWORD
#         }
#     response = login(SA_user_data)
#     token =  response["data"]["login"]["token"]

#     headers_SA = {"contentType": "application/json",
#                     "accept": "application/json",
#                     'Authorization': "Bearer"+" "+token
#                 }

#     #Get with SA Admin
#     #default : API
#     executed = gql_request(query=filter_qry, headers=headers_SA)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 5
#     # assert permission.CONTENT.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.OPENACCESS.value in resp_data[1]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[2]['metaData']['accessPermissions']
#     # assert permission.DOWNLOADABLE.value in resp_data[3]['metaData']['accessPermissions']
#     # assert permission.DERIVABLE.value in resp_data[4]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value,permission.CONTENT.value,
#       permission.DOWNLOADABLE.value, permission.DERIVABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Autographa
#     headers_SA['app'] = types.App.AG.value
#     executed = gql_request(query=filter_qry, headers=headers_SA)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Online
#     headers_SA['app'] = types.App.VACHAN.value
#     executed = gql_request(query=filter_qry, headers=headers_SA)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 2
#     # assert permission.OPENACCESS.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[1]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value]
#     check_resp_permission(resp_data,check_list)
#     #APP : Vachan Admin
#     headers_SA['app'] = types.App.VACHANADMIN.value
#     executed = gql_request(query=filter_qry, headers=headers_SA)
#     resp_data = executed["data"]["contents"]
#     assert len(resp_data) == 5
#     # assert permission.CONTENT.value in resp_data[0]['metaData']['accessPermissions']
#     # assert permission.OPENACCESS.value in resp_data[1]['metaData']['accessPermissions']
#     # assert permission.PUBLISHABLE.value in resp_data[2]['metaData']['accessPermissions']
#     # assert permission.DOWNLOADABLE.value in resp_data[3]['metaData']['accessPermissions']
#     # assert permission.DERIVABLE.value in resp_data[4]['metaData']['accessPermissions']
#     check_list = [permission.OPENACCESS.value,permission.PUBLISHABLE.value,permission.CONTENT.value,
#       permission.DOWNLOADABLE.value, permission.DERIVABLE.value]
#     check_resp_permission(resp_data,check_list)